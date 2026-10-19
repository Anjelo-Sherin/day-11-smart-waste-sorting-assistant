"""
Generate realistic sample waste images for testing and one-click demo gallery.
Categories: plastic, paper, metal, glass, organic, e-waste
"""

import os
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_images")


def create_sample_images():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Plastic: Clear blue mineral water bottle
    img_plastic = Image.new("RGB", (320, 320), color=(240, 245, 250))
    draw = ImageDraw.Draw(img_plastic)
    # Bottle body
    draw.rounded_rectangle([110, 80, 210, 280], radius=15, fill=(185, 225, 250), outline=(130, 190, 240), width=3)
    # Bottle neck & cap
    draw.rectangle([135, 45, 185, 80], fill=(200, 235, 255), outline=(130, 190, 240), width=2)
    draw.rectangle([130, 30, 190, 45], fill=(30, 144, 255))  # blue cap
    # Label
    draw.rectangle([110, 140, 210, 200], fill=(0, 102, 204))
    draw.text((120, 160), "PET #1 BOTTLE", fill=(255, 255, 255))
    # Highlights / reflections
    draw.line([125, 90, 125, 270], fill=(255, 255, 255), width=3)
    img_plastic.save(os.path.join(OUTPUT_DIR, "plastic_bottle.jpg"), quality=95)

    # 2. Paper: Clean corrugated cardboard box / office paper
    img_paper = Image.new("RGB", (320, 320), color=(250, 248, 242))
    draw = ImageDraw.Draw(img_paper)
    # Cardboard box shape
    draw.rectangle([60, 70, 260, 260], fill=(210, 180, 140), outline=(160, 120, 80), width=4)
    # Box flap crease
    draw.line([60, 150, 260, 150], fill=(160, 120, 80), width=3)
    draw.line([160, 70, 160, 150], fill=(160, 120, 80), width=3)
    draw.text((80, 180), "CORRUGATED BOX", fill=(100, 70, 40))
    draw.text((80, 205), "100% RECYCLABLE", fill=(100, 70, 40))
    img_paper.save(os.path.join(OUTPUT_DIR, "cardboard_box.jpg"), quality=95)

    # 3. Metal: Aluminum soda can
    img_metal = Image.new("RGB", (320, 320), color=(245, 245, 245))
    draw = ImageDraw.Draw(img_metal)
    # Silver metallic cylinder
    draw.rounded_rectangle([105, 60, 215, 275], radius=20, fill=(215, 215, 220), outline=(160, 160, 165), width=3)
    # Metallic specular highlights
    draw.rectangle([115, 65, 135, 270], fill=(255, 255, 255))
    draw.rectangle([170, 65, 195, 270], fill=(240, 240, 245))
    # Can rim & pull tab
    draw.ellipse([110, 50, 210, 75], fill=(190, 190, 195), outline=(140, 140, 145), width=2)
    draw.rectangle([145, 55, 175, 68], fill=(130, 130, 135))
    draw.text((120, 150), "ALU 41 CAN", fill=(80, 80, 80))
    img_metal.save(os.path.join(OUTPUT_DIR, "aluminum_can.jpg"), quality=95)

    # 4. Glass: Green beverage bottle
    img_glass = Image.new("RGB", (320, 320), color=(245, 250, 245))
    draw = ImageDraw.Draw(img_glass)
    # Green glass bottle
    draw.rounded_rectangle([115, 95, 205, 280], radius=16, fill=(46, 139, 87), outline=(34, 110, 68), width=3)
    draw.rectangle([138, 40, 182, 95], fill=(60, 155, 98), outline=(34, 110, 68), width=2)
    # Vertical specular shine line
    draw.line([130, 105, 130, 265], fill=(230, 255, 235), width=4)
    draw.text((125, 170), "GL 71 GLASS", fill=(255, 255, 255))
    img_glass.save(os.path.join(OUTPUT_DIR, "glass_bottle.jpg"), quality=95)

    # 5. Organic: Banana peel & green apple core
    img_organic = Image.new("RGB", (320, 320), color=(252, 250, 240))
    draw = ImageDraw.Draw(img_organic)
    # Leafy green & banana organic curves
    draw.chord([50, 80, 250, 270], start=30, end=180, fill=(34, 139, 34), outline=(20, 100, 20), width=3)
    draw.arc([70, 60, 260, 250], start=20, end=190, fill=(230, 190, 40), width=18)
    draw.ellipse([140, 130, 210, 210], fill=(120, 180, 50), outline=(80, 130, 30), width=2)
    draw.text((100, 220), "ORGANIC COMPOST", fill=(40, 80, 20))
    img_organic.save(os.path.join(OUTPUT_DIR, "organic_food.jpg"), quality=95)

    # 6. E-Waste: Circuit board / old broken smartphone
    img_ewaste = Image.new("RGB", (320, 320), color=(30, 35, 40))
    draw = ImageDraw.Draw(img_ewaste)
    # Circuit board body / smartphone
    draw.rounded_rectangle([80, 50, 240, 270], radius=14, fill=(15, 60, 45), outline=(100, 180, 130), width=3)
    # Screen / microchips
    draw.rectangle([100, 75, 220, 160], fill=(20, 20, 25), outline=(60, 60, 70), width=2)
    # Traces & solder pads
    for y in range(175, 250, 14):
        draw.line([95, y, 225, y], fill=(218, 165, 32), width=2)
    draw.rectangle([130, 185, 190, 235], fill=(40, 40, 45), outline=(200, 200, 200), width=1)
    draw.text((110, 110), "E-WASTE CHIP", fill=(0, 255, 150))
    img_ewaste.save(os.path.join(OUTPUT_DIR, "electronic_device.jpg"), quality=95)

    print("Sample waste test images generated successfully in:", OUTPUT_DIR)


if __name__ == "__main__":
    create_sample_images()
