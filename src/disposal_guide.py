"""
Disposal Guide and Waste Action Matrix
Maps waste classes to appropriate bins, preparation steps, contamination warnings,
and quantified environmental savings (CO2, water, landfill).
"""

from typing import Dict, Any, List

DISPOSAL_DATABASE: Dict[str, Dict[str, Any]] = {
    "plastic": {
        "class_name": "plastic",
        "display_name": "Recyclable Plastics",
        "bin_name": "Blue / Yellow Recycling Bin",
        "bin_color": "#2563EB",  # Royal Blue
        "bin_badge_class": "bg-blue-100 text-blue-800 border-blue-300",
        "icon": "🧴",
        "accepted_resin_codes": ["#1 PETE", "#2 HDPE", "#4 LDPE", "#5 PP"],
        "preparation_steps": [
            "Empty any residual liquid or food scraps.",
            "Rinse lightly with cold water (no need for dish soap).",
            "Crush or flatten bottles to save volume in collection trucks.",
            "Re-attach the plastic screw cap so it doesn't get lost in sorting trommels.",
        ],
        "contamination_warnings": [
            "Do NOT include soft plastic film/chip packets unless your local municipality accepts soft plastics.",
            "Black plastic cannot be detected by optical near-infrared (NIR) sorters in many facilities.",
            "Never put motor oil bottles or pesticide containers into domestic recycling bins.",
        ],
        "environmental_impact": {
            "co2_saved_kg": 0.18,
            "water_saved_liters": 2.4,
            "landfill_diverted_grams": 45,
            "energy_saved_kwh": 0.42,
        },
        "eco_fact": "Recycling 1 ton of plastic saves approximately 5,774 kWh of electricity and 16.3 barrels of oil.",
        "points_reward": 15,
    },
    "paper": {
        "class_name": "paper",
        "display_name": "Paper & Cardboard",
        "bin_name": "Blue Paper Bin",
        "bin_color": "#0284C7",  # Sky Blue
        "bin_badge_class": "bg-sky-100 text-sky-800 border-sky-300",
        "icon": "📦",
        "accepted_resin_codes": ["Corrugated Cardboard", "Office Paper", "Newspapers", "Clean Boxes"],
        "preparation_steps": [
            "Flatten and break down cardboard boxes before disposal.",
            "Remove plastic tape, bubble wrap, and polystyrene inserts.",
            "Keep dry — wet paper clogs mechanical screening machinery.",
        ],
        "contamination_warnings": [
            "Greasy pizza boxes CANNOT be recycled (food grease prevents paper fibers from binding during pulping). Compost the greasy half instead!",
            "Thermal receipt paper often contains BPA and should not be mixed with standard paper pulp.",
            "Wax-coated cups and juice cartons usually require specialized Tetra Pak recycling streams.",
        ],
        "environmental_impact": {
            "co2_saved_kg": 0.22,
            "water_saved_liters": 7.5,
            "landfill_diverted_grams": 90,
            "energy_saved_kwh": 0.35,
        },
        "eco_fact": "Every metric ton of recycled cardboard saves 17 mature trees and 7,000 gallons of fresh water.",
        "points_reward": 10,
    },
    "metal": {
        "class_name": "metal",
        "display_name": "Metals & Aluminum Cans",
        "bin_name": "Yellow / Gray Metal Bin",
        "bin_color": "#D97706",  # Amber/Bronze
        "bin_badge_class": "bg-amber-100 text-amber-800 border-amber-300",
        "icon": "🥫",
        "accepted_resin_codes": ["Aluminum Cans (ALU 41)", "Steel/Tin Food Cans (FE 40)", "Clean Foil"],
        "preparation_steps": [
            "Empty completely and rinse away leftover sauce or soup.",
            "Ball up clean aluminum foil into a fist-sized ball so sorting magnets can catch it.",
            "Tuck tin can lids inside the can to protect sanitation workers from cuts.",
        ],
        "contamination_warnings": [
            "Do NOT place pressurized aerosol cans in domestic bins unless 100% empty and depressurized.",
            "Scrap car parts, heavy iron pipes, and wire hangers should be taken to scrap metal recyclers.",
        ],
        "environmental_impact": {
            "co2_saved_kg": 0.38,
            "water_saved_liters": 3.8,
            "landfill_diverted_grams": 60,
            "energy_saved_kwh": 1.25,
        },
        "eco_fact": "Aluminum can be recycled infinitely with zero degradation in quality. Recycling 1 can saves 95% of the energy needed to make a new one from bauxite ore.",
        "points_reward": 20,
    },
    "glass": {
        "class_name": "glass",
        "display_name": "Glass Bottles & Jars",
        "bin_name": "Green / Brown Glass Bank",
        "bin_color": "#059669",  # Emerald Green
        "bin_badge_class": "bg-emerald-100 text-emerald-800 border-emerald-300",
        "icon": "🍾",
        "accepted_resin_codes": ["GL 70 (Clear)", "GL 71 (Green)", "GL 72 (Brown)"],
        "preparation_steps": [
            "Rinse out food residue and liquids.",
            "Remove metal or cork caps (sort them into metal or compost respectively).",
            "Sort by color (clear, amber, green) if your local bottle bank has designated chutes.",
        ],
        "contamination_warnings": [
            "Drinking glasses, Pyrex, ceramics, mirrors, and lightbulbs have higher melting temperatures and contaminate furnace batches.",
            "Broken glass shards should be securely wrapped and marked before municipal drop-off.",
        ],
        "environmental_impact": {
            "co2_saved_kg": 0.15,
            "water_saved_liters": 1.8,
            "landfill_diverted_grams": 250,
            "energy_saved_kwh": 0.30,
        },
        "eco_fact": "A glass bottle can take over 1,000,000 years to decompose in a landfill, but is 100% recyclable into new glass jars indefinitely.",
        "points_reward": 15,
    },
    "organic": {
        "class_name": "organic",
        "display_name": "Compost & Organic Waste",
        "bin_name": "Brown / Green Compost Bin",
        "bin_color": "#16A34A",  # Forest Green
        "bin_badge_class": "bg-green-100 text-green-800 border-green-300",
        "icon": "🍏",
        "accepted_resin_codes": ["Fruit & Vegetable Scraps", "Coffee Grounds", "Eggshells", "Yard Trimmings"],
        "preparation_steps": [
            "Peel off produce stickers (PLU stickers are made of vinyl plastic, not paper!).",
            "Chop large melon rinds or branches to accelerate microbial decomposition.",
            "Line your caddy with certified BPI compostable bags or newspaper sheets.",
        ],
        "contamination_warnings": [
            "Do NOT include plastic bags, plastic cutlery, or conventional pet waste.",
            "Avoid large quantities of animal bones or dairy in small home compost bins to avoid pests.",
        ],
        "environmental_impact": {
            "co2_saved_kg": 0.31,
            "water_saved_liters": 0.5,
            "landfill_diverted_grams": 350,
            "energy_saved_kwh": 0.15,
        },
        "eco_fact": "Composting organic matter prevents anaerobic decomposition in landfills, directly eliminating potent methane emissions (CH4).",
        "points_reward": 12,
    },
    "e-waste": {
        "class_name": "e-waste",
        "display_name": "Electronic Waste & Batteries",
        "bin_name": "Special E-Waste Collection Center",
        "bin_color": "#DC2626",  # Warning Red
        "bin_badge_class": "bg-red-100 text-red-800 border-red-300",
        "icon": "💻",
        "accepted_resin_codes": ["Li-Ion Batteries", "Smartphones", "Cables", "Motherboards", "Appliances"],
        "preparation_steps": [
            "Tape the terminals of lithium or 9V batteries with electrical tape to prevent short-circuiting.",
            "Perform a factory reset and securely wipe personal data before dropping off phones or laptops.",
            "Keep cables neatly bundled or coiled.",
        ],
        "contamination_warnings": [
            "NEVER throw lithium-ion batteries into standard trash or curbside recycling. They puncture and cause catastrophic waste facility fires!",
            "Handle cracked monitors or mercury thermometer devices with gloves and sealed bags.",
        ],
        "environmental_impact": {
            "co2_saved_kg": 1.45,
            "water_saved_liters": 18.0,
            "landfill_diverted_grams": 180,
            "energy_saved_kwh": 4.80,
        },
        "eco_fact": "1 million recycled mobile phones recover 35,000 lbs of copper, 772 lbs of silver, and 75 lbs of pure gold.",
        "points_reward": 30,
    },
}


def get_disposal_guide(waste_class: str) -> Dict[str, Any]:
    """Retrieve full disposal guide for a given waste class."""
    key = waste_class.lower().strip()
    if key not in DISPOSAL_DATABASE:
        key = "plastic"  # Safe default fallback
    return DISPOSAL_DATABASE[key]


def calculate_savings_batch(items: List[str]) -> Dict[str, float]:
    """Calculate cumulative environmental impact for a list of items."""
    total_co2 = 0.0
    total_water = 0.0
    total_landfill = 0.0
    total_energy = 0.0

    for item in items:
        guide = get_disposal_guide(item)
        impact = guide["environmental_impact"]
        total_co2 += impact["co2_saved_kg"]
        total_water += impact["water_saved_liters"]
        total_landfill += impact["landfill_diverted_grams"]
        total_energy += impact["energy_saved_kwh"]

    return {
        "total_co2_saved_kg": round(total_co2, 2),
        "total_water_saved_liters": round(total_water, 2),
        "total_landfill_diverted_kg": round(total_landfill / 1000.0, 3),
        "total_energy_saved_kwh": round(total_energy, 2),
    }
