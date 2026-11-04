"""
rule_engine.py – Rule-based heuristic transaction classification engine.
Loads rules from config/classification_rules.json and applies keyword/pattern matching.
"""
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent / "config" / "classification_rules.json"


class RuleEngine:
    """
    Applies configurable keyword and regex pattern rules to classify transactions.
    Rules are loaded from JSON configuration for easy customisation.
    """

    def __init__(self, rules_path: Optional[str] = None):
        self.rules: List[Dict] = []
        self._load_rules(rules_path or str(CONFIG_PATH))

    def _load_rules(self, path: str):
        """Load classification rules from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.rules = sorted(data.get("rules", []), key=lambda r: r.get("priority", 99))
            logger.info("Loaded %d classification rules.", len(self.rules))
        except Exception as exc:
            logger.error("Could not load rules from %s: %s", path, exc)
            self.rules = []

    def classify(
        self,
        description: str,
        debit: Optional[float] = None,
        credit: Optional[float] = None,
    ) -> Tuple[str, float]:
        """
        Classify a transaction using rule-based matching.

        Returns:
            (category, confidence) where confidence is 0.0–1.0
        """
        if not description:
            return "Other / Uncategorized", 0.0

        desc_lower = description.lower()

        for rule in self.rules:
            category = rule.get("category", "Other / Uncategorized")
            credit_only = rule.get("credit_only", False)
            debit_only = rule.get("debit_only", False)

            # Direction filter
            if credit_only and (credit is None or credit == 0):
                continue
            if debit_only and (debit is None or debit == 0):
                continue

            # Keyword matching
            matched = False
            keywords = rule.get("keywords", [])
            for kw in keywords:
                kw_lower = kw.lower()
                # For short keywords (<=4 chars), require word-boundary match to avoid false positives
                if len(kw_lower) <= 4:
                    if re.search(r'\b' + re.escape(kw_lower) + r'\b', desc_lower):
                        matched = True
                        break
                else:
                    if kw_lower in desc_lower:
                        matched = True
                        break

            # Pattern matching
            if not matched:
                patterns = rule.get("patterns", [])
                for pat in patterns:
                    if re.search(re.escape(pat), description, re.IGNORECASE):
                        matched = True
                        break

            if matched:
                return category, 0.95

        return "Other / Uncategorized", 0.0

    def add_custom_rule(self, category: str, keywords: List[str], priority: int = 50):
        """Add a custom rule at runtime (not persisted to file)."""
        self.rules.append({
            "category": category,
            "priority": priority,
            "keywords": keywords,
            "patterns": [],
        })
        self.rules.sort(key=lambda r: r.get("priority", 99))
        logger.info("Added custom rule for category '%s' with %d keywords.", category, len(keywords))
