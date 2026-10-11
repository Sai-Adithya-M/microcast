import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.predictor import MountainWeatherPredictor
from core.audio_narrator import TrailAudioNarrator
from core.sky_vision import SkyVisionAnalyzer

app = FastAPI(
    title="MicroCast API",
    description="Offline Mountain Squall & Microclimate Prediction using TabPFN and Sky Vision",
    version="1.1.0"
)

# Initialize engines
predictor = MountainWeatherPredictor(data_path="data/mountain_weather_history.csv")
narrator = TrailAudioNarrator()
vision_analyzer = SkyVisionAnalyzer()

# Mount static directory
os.makedirs("static", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class TelemetryPayload(BaseModel):
    pressure_drop_hpa_hr: float = Field(..., description="Barometric pressure drop in hPa per hour", ge=0.0, le=10.0)
    altitude_m: float = Field(2400.0, description="Altitude in meters above sea level", ge=0.0, le=8848.0)
    temp_c: float = Field(12.0, description="Ambient temperature in Celsius", ge=-40.0, le=55.0)
    humidity_pct: float = Field(80.0, description="Relative humidity percentage", ge=0.0, le=100.0)
    wind_speed_kmh: float = Field(35.0, description="Wind speed in km/h", ge=0.0, le=250.0)
    cloud_type_code: int = Field(2, description="Cloud code: 0=Cirrus, 1=Cumulus, 2=Lenticular, 3=Congestus, 4=Cumulonimbus", ge=0, le=4)

@app.get("/")
def get_index():
    return FileResponse("static/index.html")

@app.post("/api/analyze-sky")
async def analyze_sky_photo(file: UploadFile = File(...)):
    """
    Takes an uploaded or captured photo of the sky, extracts cloud morphology,
    and returns the classified cloud type code (0-4) and confidence.
    """
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file received.")
        
        result = vision_analyzer.analyze_image_bytes(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")

@app.post("/api/predict")
def predict_trail_weather(payload: TelemetryPayload):
    try:
        prediction = predictor.predict(
            pressure_drop_hpa_hr=payload.pressure_drop_hpa_hr,
            altitude_m=payload.altitude_m,
            temp_c=payload.temp_c,
            humidity_pct=payload.humidity_pct,
            wind_speed_kmh=payload.wind_speed_kmh,
            cloud_type_code=payload.cloud_type_code
        )

        # Generate audio alert
        narration = narrator.generate_narration(prediction)
        prediction["narration"] = narration

        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "tabpfn_active": predictor.model is not None,
        "vision_active": True
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
