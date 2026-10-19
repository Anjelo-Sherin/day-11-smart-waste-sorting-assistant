"""
Tests for Waste Disposal Guide and Impact Matrix
"""

from src.disposal_guide import get_disposal_guide, calculate_savings_batch, DISPOSAL_DATABASE


def test_disposal_guide_classes():
    required_classes = ["plastic", "paper", "metal", "glass", "organic", "e-waste"]
    for c in required_classes:
        guide = get_disposal_guide(c)
        assert guide["class_name"] == c
        assert "bin_name" in guide
        assert "bin_color" in guide
        assert len(guide["preparation_steps"]) > 0
        assert len(guide["contamination_warnings"]) > 0
        assert "environmental_impact" in guide
        impact = guide["environmental_impact"]
        assert impact["co2_saved_kg"] > 0
        assert impact["water_saved_liters"] >= 0


def test_batch_savings_calculation():
    items = ["plastic", "aluminum_can", "paper", "e-waste"]
    totals = calculate_savings_batch(items)
    assert totals["total_co2_saved_kg"] > 0
    assert totals["total_water_saved_liters"] > 0
    assert totals["total_landfill_diverted_kg"] > 0
