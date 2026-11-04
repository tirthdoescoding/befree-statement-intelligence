"""
ml_classifier.py – Traditional ML-based transaction classifier (TF-IDF + LinearSVC).
Falls back gracefully when no trained model is available.
"""
import os
import logging
import pickle
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "models"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
CLASSIFIER_PATH = MODEL_DIR / "svc_classifier.pkl"
DATA_PATH = Path(__file__).parent.parent / "data" / "sample_transactions.csv"


class MLClassifier:
    """
    TF-IDF + LinearSVC classifier for transaction categorisation.
    Trains on sample data if no saved model is found.
    """

    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        self._load_or_train()

    def _load_or_train(self):
        """Load a saved model or train a new one from sample data."""
        if VECTORIZER_PATH.exists() and CLASSIFIER_PATH.exists():
            try:
                with open(VECTORIZER_PATH, "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(CLASSIFIER_PATH, "rb") as f:
                    self.classifier = pickle.load(f)
                self.is_trained = True
                logger.info("ML model loaded from disk.")
                return
            except Exception as exc:
                logger.warning("Failed to load saved model: %s. Will retrain.", exc)

        self._train()

    def _train(self):
        """Train from the sample transactions CSV."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.svm import LinearSVC
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import LabelEncoder

            if not DATA_PATH.exists():
                logger.warning("Sample data not found at %s. ML classifier disabled.", DATA_PATH)
                return

            df = pd.read_csv(DATA_PATH)
            df = df.dropna(subset=["Description", "Category"])
            df = df[df["Category"].str.strip() != ""]

            if len(df) < 10:
                logger.warning("Not enough training data (%d rows). ML classifier disabled.", len(df))
                return

            X = df["Description"].astype(str).tolist()
            y = df["Category"].astype(str).tolist()

            self.vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 4),
                max_features=5000,
                sublinear_tf=True,
            )
            X_vec = self.vectorizer.fit_transform(X)

            self.classifier = LinearSVC(C=1.0, max_iter=2000, class_weight="balanced")
            self.classifier.fit(X_vec, y)
            self.is_trained = True

            # Save model
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            with open(VECTORIZER_PATH, "wb") as f:
                pickle.dump(self.vectorizer, f)
            with open(CLASSIFIER_PATH, "wb") as f:
                pickle.dump(self.classifier, f)

            logger.info("ML model trained on %d samples and saved.", len(X))
        except Exception as exc:
            logger.error("ML training failed: %s", exc)
            self.is_trained = False

    def predict(self, description: str) -> Tuple[str, float]:
        """
        Predict a category for the given transaction description.

        Returns:
            (category, confidence) where confidence is 0.0–1.0
        """
        if not self.is_trained or not self.vectorizer or not self.classifier:
            return "Other / Uncategorized", 0.0

        try:
            X = self.vectorizer.transform([description])
            label = self.classifier.predict(X)[0]

            # Compute confidence using decision function margin
            decision = self.classifier.decision_function(X)[0]
            if hasattr(decision, "__len__"):
                max_score = float(max(decision))
                # Normalise to [0,1] with sigmoid
                import math
                confidence = 1 / (1 + math.exp(-max_score * 0.5))
                confidence = min(0.90, max(0.3, confidence))
            else:
                confidence = 0.6

            return label, confidence
        except Exception as exc:
            logger.error("ML prediction failed: %s", exc)
            return "Other / Uncategorized", 0.0

    def retrain(self):
        """Force retrain the model from sample data."""
        self.is_trained = False
        self.vectorizer = None
        self.classifier = None
        # Remove old model files
        for p in [VECTORIZER_PATH, CLASSIFIER_PATH]:
            if p.exists():
                p.unlink()
        self._train()
