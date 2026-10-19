"""
Smart Waste Sorting Assistant with Recycling Map — FastAPI Server
Serves image classification, disposal guides, OpenStreetMap GIS navigation,
and gamification endpoints.
"""

import base64
import io
import os
from typing import Optional, List
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image

from src.classifier import WasteClassifierPipeline
from src.disposal_guide import get_disposal_guide, calculate_savings_batch, DISPOSAL_DATABASE
from src.gis_service import GISRecyclingService
from src.database import init_db
from src.gamification import GamificationEngine

app = FastAPI(
    title="Smart Waste Sorting Assistant with Recycling Map",
    description="Point your camera at trash, learn the bin, and navigate to the nearest recycler.",
    version="1.0.0",
)

# Enable CORS for local and web development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize AI and GIS services
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "waste_classifier.pt")
classifier_pipeline = WasteClassifierPipeline(model_path=MODEL_PATH)
gis_service = GISRecyclingService()

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_images")
if os.path.exists(SAMPLE_DIR):
    app.mount("/sample-images", StaticFiles(directory=SAMPLE_DIR), name="sample_images")


class RecordActionRequest(BaseModel):
    user_id: str = "user_current"
    waste_class: str
    confidence: float = 0.95
    photo_notes: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Smart Waste Sorting Assistant is Starting...</h1>")


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Smart Waste Sorting Assistant with Recycling Map",
        "day": 11,
        "classes": classifier_pipeline.classes,
        "device": str(classifier_pipeline.device),
        "confidence_threshold": classifier_pipeline.confidence_threshold,
    }


@app.post("/api/classify")
async def classify_waste_image(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
):
    """
    Classifies a waste item from uploaded file or webcam base64 stream.
    Returns prediction, bin guidance, and nearest recycling point if coordinates supplied.
    """
    pil_image = None
    if file:
        content = await file.read()
        pil_image = Image.open(io.BytesIO(content))
    elif image_base64:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        decoded = base64.b64decode(image_base64)
        pil_image = Image.open(io.BytesIO(decoded))
    else:
        raise HTTPException(status_code=400, detail="Must provide an image file or base64 image data.")

    # 1. Run classifier
    prediction = classifier_pipeline.predict(pil_image)
    waste_class = prediction["predicted_class"]

    # 2. Get disposal guide
    guide = get_disposal_guide(waste_class)

    # 3. If GPS is provided, find nearest recycling point
    nearest_gis = None
    if lat is not None and lon is not None:
        gis_result = gis_service.get_nearby_recyclers(
            user_lat=lat, user_lon=lon, waste_filter=waste_class, limit=3
        )
        nearest_gis = {
            "closest_facility": gis_result["closest_facility"],
            "route_waypoints": gis_result["route_waypoints"],
            "facilities": gis_result["facilities"],
        }

    return {
        "prediction": prediction,
        "disposal_guide": guide,
        "recycling_map": nearest_gis,
    }


@app.post("/api/classify-multiview")
async def classify_multiview(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """
    Fuses two angles/photos of the same waste item to resolve ambiguity.
    """
    img1 = Image.open(io.BytesIO(await file1.read()))
    img2 = Image.open(io.BytesIO(await file2.read()))

    pred1 = classifier_pipeline.predict(img1)
    pred2 = classifier_pipeline.predict(img2)

    fused = classifier_pipeline.fuse_predictions(pred1, pred2)
    guide = get_disposal_guide(fused["predicted_class"])

    return {
        "fused_prediction": fused,
        "disposal_guide": guide,
        "first_photo_prediction": pred1,
        "second_photo_prediction": pred2,
    }


@app.post("/api/record-action")
async def record_user_sorting_action(payload: RecordActionRequest):
    """
    Records that the user sorted an item, updates streak, adds Green Score points,
    and checks for new badges.
    """
    result = GamificationEngine.record_disposal(
        user_id=payload.user_id,
        waste_class=payload.waste_class,
        confidence=payload.confidence,
        photo_notes=payload.photo_notes,
    )
    return result


@app.get("/api/recycling-map")
async def get_recycling_map(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    waste_type: Optional[str] = Query(None, description="Optional waste category filter"),
    limit: int = Query(5, description="Max facilities to return"),
):
    """
    Queries real-world recycling amenities around coordinates with route waypoints.
    """
    return gis_service.get_nearby_recyclers(
        user_lat=lat, user_lon=lon, waste_filter=waste_type, limit=limit
    )


@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Returns top sorting community members."""
    return {"leaderboard": GamificationEngine.get_leaderboard(limit=limit)}


@app.get("/api/user/profile")
async def get_user_profile(user_id: str = "user_current"):
    """Returns user green score, streaks, badges, and carbon savings."""
    return GamificationEngine.get_user_profile(user_id=user_id)


@app.get("/api/disposal-guide/{waste_class}")
async def get_guide(waste_class: str):
    """Retrieves full disposal guide for any class."""
    return get_disposal_guide(waste_class)


@app.get("/api/disposal-guides")
async def list_all_guides():
    """Returns all 6 waste disposal guides and parameters."""
    return DISPOSAL_DATABASE


@app.get("/manifest.json")
async def get_manifest():
    manifest_file = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_file):
        return FileResponse(manifest_file, media_type="application/manifest+json")
    return {"name": "Smart Waste Sorting Assistant"}
