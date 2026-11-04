"""
classification_engine.py – Hybrid 3-layer transaction classification engine.
Layer 1: Rule-based heuristics (highest priority)
Layer 2: ML (TF-IDF + LinearSVC)
Layer 3: Fallback → Other / Uncategorized
"""
import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

from modules.rule_engine import RuleEngine
from modules.ml_classifier import MLClassifier

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.50  # Below this ML prediction is overridden as Uncategorized


class ClassificationEngine:
    """
    Hybrid classification engine that combines rule-based and ML approaches.
    """

    def __init__(self):
        self.rule_engine = RuleEngine()
        self.ml_classifier = MLClassifier()
        logger.info(
            "ClassificationEngine ready. ML trained: %s",
            self.ml_classifier.is_trained,
        )

    def classify_transaction(
        self,
        description: str,
        debit: Optional[float] = None,
        credit: Optional[float] = None,
    ) -> Dict:
        """
        Classify a single transaction.

        Returns a dict with:
            - category: str
            - confidence: float (0–1)
            - method: str ("rule-based" | "ml" | "fallback")
        """
        # Layer 1: Rule-based
        rule_cat, rule_conf = self.rule_engine.classify(description, debit, credit)
        if rule_conf >= 0.90:
            return {"category": rule_cat, "confidence": rule_conf, "method": "rule-based"}

        # Layer 2: ML
        ml_cat, ml_conf = self.ml_classifier.predict(description)

        # If ML is confident enough, use it
        if ml_conf >= CONFIDENCE_THRESHOLD and ml_cat != "Other / Uncategorized":
            # Rule takes priority if it found something (even with lower confidence)
            if rule_cat != "Other / Uncategorized":
                return {"category": rule_cat, "confidence": rule_conf, "method": "rule-based"}
            return {"category": ml_cat, "confidence": ml_conf, "method": "ml"}

        # Layer 3: Fallback
        if rule_cat != "Other / Uncategorized":
            return {"category": rule_cat, "confidence": rule_conf, "method": "rule-based"}

        return {"category": "Other / Uncategorized", "confidence": 0.0, "method": "fallback"}

    def classify_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify all transactions in a DataFrame.
        Adds 'category', 'confidence', and 'classification_method' columns.
        """
        df = df.copy()
        categories = []
        confidences = []
        methods = []

        for _, row in df.iterrows():
            result = self.classify_transaction(
                description=str(row.get("description", "")),
                debit=row.get("debit"),
                credit=row.get("credit"),
            )
            categories.append(result["category"])
            confidences.append(round(result["confidence"], 2))
            methods.append(result["method"])

        df["category"] = categories
        df["confidence"] = confidences
        df["classification_method"] = methods
        return df

    def add_custom_rule(self, category: str, keywords: List[str]):
        """Add a custom keyword rule at runtime."""
        self.rule_engine.add_custom_rule(category, keywords)
