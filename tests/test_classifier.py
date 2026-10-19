"""
Tests for MobileNetV3 Waste Classifier Pipeline
"""

import os
import torch
import numpy as np
from PIL import Image
from src.classifier import MobileNetV3Waste, WasteClassifierPipeline, WASTE_CLASSES


def test_mobilenet_model_forward():
    model = MobileNetV3Waste(num_classes=6)
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        output = model(dummy_input)
    assert output.shape == (1, 6)


def test_preprocessing():
    pipeline = WasteClassifierPipeline()
    img = Image.new("RGB", (300, 400), color=(100, 150, 200))
    tensor = pipeline.preprocess_image(img)
    assert tensor.shape == (1, 3, 224, 224)
    assert isinstance(tensor, torch.Tensor)


def test_prediction_all_sample_images():
    pipeline = WasteClassifierPipeline()
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_images")

    test_cases = [
        ("plastic_bottle.jpg", "plastic"),
        ("cardboard_box.jpg", "paper"),
        ("aluminum_can.jpg", "metal"),
        ("glass_bottle.jpg", "glass"),
        ("organic_food.jpg", "organic"),
        ("electronic_device.jpg", "e-waste"),
    ]

    for filename, expected_class in test_cases:
        path = os.path.join(sample_dir, filename)
        if os.path.exists(path):
            res = pipeline.predict(path)
            assert "predicted_class" in res
            assert res["predicted_class"] in WASTE_CLASSES
            assert 0.0 <= res["confidence"] <= 1.0
            assert len(res["all_predictions"]) == 6


def test_prediction_fusion():
    pipeline = WasteClassifierPipeline()
    pred1 = {
        "predicted_class": "plastic",
        "confidence": 0.52,
        "all_predictions": [
            {"class": "plastic", "confidence": 0.52},
            {"class": "metal", "confidence": 0.48},
        ],
    }
    pred2 = {
        "predicted_class": "plastic",
        "confidence": 0.70,
        "all_predictions": [
            {"class": "plastic", "confidence": 0.70},
            {"class": "metal", "confidence": 0.30},
        ],
    }
    fused = pipeline.fuse_predictions(pred1, pred2)
    assert fused["predicted_class"] == "plastic"
    assert fused["confidence"] > 0.55
    assert fused["fused_from_photos"] == 2
