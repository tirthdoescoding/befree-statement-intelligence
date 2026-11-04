"""
tests/test_classification.py – Tests for the classification engine.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from modules.rule_engine import RuleEngine
from modules.ml_classifier import MLClassifier
from modules.classification_engine import ClassificationEngine


@pytest.fixture
def rule_engine():
    return RuleEngine()


@pytest.fixture
def engine():
    return ClassificationEngine()


class TestRuleEngine:
    def test_salary_credit(self, rule_engine):
        cat, conf = rule_engine.classify("SALARY CREDIT JAN 2024", credit=75000)
        assert cat == "Salary"
        assert conf >= 0.9

    def test_atm_withdrawal(self, rule_engine):
        cat, conf = rule_engine.classify("ATM CASH WITHDRAWAL", debit=5000)
        assert cat == "ATM Withdrawal"
        assert conf >= 0.9

    def test_food_dining_swiggy(self, rule_engine):
        cat, conf = rule_engine.classify("UPI/SWIGGY/FOOD ORDER", debit=350)
        assert cat == "Food & Dining"

    def test_emi_loan(self, rule_engine):
        cat, conf = rule_engine.classify("EMI HOME LOAN PAYMENT", debit=25000)
        assert cat == "EMI / Loan"

    def test_shopping_amazon(self, rule_engine):
        cat, conf = rule_engine.classify("AMAZON SHOPPING PURCHASE", debit=2000)
        assert cat == "Shopping"

    def test_utilities_airtel(self, rule_engine):
        cat, conf = rule_engine.classify("AIRTEL BILL PAYMENT", debit=599)
        assert cat == "Utilities"

    def test_insurance(self, rule_engine):
        cat, conf = rule_engine.classify("HDFC LIFE INSURANCE PREMIUM", debit=5000)
        assert cat == "Insurance"

    def test_investment_sip(self, rule_engine):
        cat, conf = rule_engine.classify("SIP HDFC MF JAN 2024", debit=2000)
        assert cat == "Investment"

    def test_interest_credit(self, rule_engine):
        cat, conf = rule_engine.classify("INTEREST CREDIT", credit=250)
        assert cat == "Interest"

    def test_transport_uber(self, rule_engine):
        cat, conf = rule_engine.classify("UBER RIDE PAYMENT", debit=350)
        assert cat == "Transportation"

    def test_healthcare_apollo(self, rule_engine):
        cat, conf = rule_engine.classify("APOLLO PHARMACY PURCHASE", debit=850)
        assert cat == "Healthcare"

    def test_uncategorized_fallback(self, rule_engine):
        cat, conf = rule_engine.classify("RANDOM TRANSACTION 12345")
        assert cat == "Other / Uncategorized"

    def test_empty_description(self, rule_engine):
        cat, conf = rule_engine.classify("")
        assert cat == "Other / Uncategorized"
        assert conf == 0.0

    def test_custom_rule(self, rule_engine):
        rule_engine.add_custom_rule("Food & Dining", ["netflix-dinner"])
        cat, conf = rule_engine.classify("netflix-dinner payment", debit=100)
        assert cat == "Food & Dining"


class TestMLClassifier:
    def test_ml_loads_or_trains(self):
        ml = MLClassifier()
        assert isinstance(ml.is_trained, bool)

    def test_ml_predict_returns_tuple(self):
        ml = MLClassifier()
        result = ml.predict("SALARY CREDIT")
        assert isinstance(result, tuple)
        assert len(result) == 2
        cat, conf = result
        assert isinstance(cat, str)
        assert 0.0 <= conf <= 1.0

    def test_ml_predict_known_category(self):
        ml = MLClassifier()
        if ml.is_trained:
            cat, conf = ml.predict("SALARY CREDIT JAN 2024")
            assert isinstance(cat, str)


class TestClassificationEngine:
    def test_classify_salary(self, engine):
        result = engine.classify_transaction("SALARY CREDIT JAN 2024", credit=75000)
        assert result["category"] == "Salary"
        assert result["method"] == "rule-based"

    def test_classify_returns_dict(self, engine):
        result = engine.classify_transaction("TEST TRANSACTION")
        assert "category" in result
        assert "confidence" in result
        assert "method" in result

    def test_classify_dataframe(self, engine):
        import pandas as pd
        df = pd.DataFrame([
            {"date": "2024-01-01", "description": "SALARY CREDIT", "debit": None, "credit": 75000, "balance": 125000},
            {"date": "2024-01-02", "description": "ATM WITHDRAWAL", "debit": 5000, "credit": None, "balance": 120000},
        ])
        result = engine.classify_dataframe(df)
        assert "category" in result.columns
        assert "confidence" in result.columns
        assert "classification_method" in result.columns
        assert len(result) == 2
