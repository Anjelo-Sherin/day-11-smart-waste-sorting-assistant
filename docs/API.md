# API Reference

The **Smart Waste Sorting Assistant** exposes a high-performance RESTful API built on FastAPI.

**Base URL:** `http://localhost:8011`

---

## 1. Health & Service Telemetry

### `GET /api/health`
Checks service health and returns model inference device.

**Response:**
```json
{
  "status": "healthy",
  "service": "Smart Waste Sorting Assistant with Recycling Map",
  "day": 11,
  "classes": ["e-waste", "glass", "metal", "organic", "paper", "plastic"],
  "device": "cpu",
  "confidence_threshold": 0.58
}
```

---

## 2. Waste Classification

### `POST /api/classify`
Classifies a waste item from a multipart image file or base64 string. Optionally accepts GPS coordinates (`lat`, `lon`) to return the nearest recycling center.

**Request (Multipart Form):**
- `file`: Image binary (`image/jpeg`, `image/png`)
- `lat` (optional): `float` (e.g., `12.9716`)
- `lon` (optional): `float` (e.g., `77.5946`)

**Example `curl`:**
```bash
curl -X POST http://localhost:8011/api/classify \
  -F "file=@data/sample_images/plastic_bottle.jpg" \
  -F "lat=12.9716" \
  -F "lon=77.5946"
```

**Response:**
```json
{
  "prediction": {
    "predicted_class": "plastic",
    "confidence": 0.836,
    "confidence_percentage": 83.6,
    "needs_second_photo": false,
    "second_photo_guidance": null,
    "all_predictions": [
      {"class": "plastic", "confidence": 0.836},
      {"class": "metal", "confidence": 0.045},
      {"class": "glass", "confidence": 0.038},
      {"class": "paper", "confidence": 0.032},
      {"class": "organic", "confidence": 0.026},
      {"class": "e-waste", "confidence": 0.023}
    ],
    "inference_device": "cpu"
  },
  "disposal_guide": {
    "class_name": "plastic",
    "display_name": "Recyclable Plastics",
    "bin_name": "Blue / Yellow Recycling Bin",
    "bin_color": "#2563EB",
    "icon": "🧴",
    "preparation_steps": [
      "Empty any residual liquid or food scraps.",
      "Rinse lightly with cold water.",
      "Crush or flatten bottles to save volume.",
      "Re-attach the plastic screw cap."
    ],
    "contamination_warnings": [
      "Do NOT include soft plastic film/chip packets."
    ],
    "environmental_impact": {
      "co2_saved_kg": 0.18,
      "water_saved_liters": 2.4,
      "landfill_diverted_grams": 45,
      "energy_saved_kwh": 0.42
    },
    "points_reward": 15
  },
  "recycling_map": {
    "closest_facility": {
      "id": "local-42",
      "name": "GreenCycle Community Drop-off",
      "distance_km": 0.56,
      "walking_time_mins": 7,
      "types": ["plastic", "paper", "metal", "glass"]
    }
  }
}
```

---

### `POST /api/classify-multiview`
Fuses two photos of the same object to resolve ambiguity when initial confidence is low.

**Request:**
- `file1`: First camera view (`multipart/form-data`)
- `file2`: Second camera view (`multipart/form-data`)

---

## 3. GIS & Recycling Centers

### `GET /api/recycling-map`
Finds nearby recycling amenities around coordinates using OpenStreetMap Overpass data.

**Query Parameters:**
- `lat` (required): Latitude (`float`)
- `lon` (required): Longitude (`float`)
- `waste_type` (optional): Filter by material (`plastic`, `e-waste`, `glass`, etc.)
- `limit` (optional): Maximum facilities to return (default: `5`)

**Example `curl`:**
```bash
curl "http://localhost:8011/api/recycling-map?lat=37.7749&lon=-122.4194&limit=3"
```

---

## 4. Gamification & Community

### `POST /api/record-action`
Records that a user sorted an item properly, credits points, updates daily streak, and unlocks badges.

**Payload:**
```json
{
  "user_id": "user_current",
  "waste_class": "plastic",
  "confidence": 0.95,
  "photo_notes": "Recycled 500ml water bottle"
}
```

### `GET /api/leaderboard`
Returns the top community recycling leaders ranked by Green Score.

### `GET /api/user/profile`
Returns current user stats, streak history, unlocked badges, and lifetime environmental savings.
