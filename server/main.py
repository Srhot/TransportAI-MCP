from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API anahtarını kontrol et
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
if not AVIATIONSTACK_API_KEY:
    logger.warning("AVIATIONSTACK_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")

app = FastAPI(
    title="TransportAI MCP Server",
    description="Model Context Protocol server for TransportAI with AviationStack integration",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AviationStack API ayarları
AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1"

# Model sınıfları
class ModelRequest(BaseModel):
    model_id: str
    input_data: Dict[str, Any]

class ModelResponse(BaseModel):
    model_id: str
    output_data: Dict
    metadata: Optional[Dict] = None
    timestamp: str

class FlightInfo(BaseModel):
    airline: str
    flight_number: str
    departure: Dict
    arrival: Dict
    status: str

class FlightRequest(BaseModel):
    flight_iata: str

# Aktif bağlantıları tutacak sözlük
active_connections: Dict[str, WebSocket] = {}

def get_flight_info(flight_iata: str) -> Dict:
    """AviationStack API'den uçuş bilgilerini al"""
    if not AVIATIONSTACK_API_KEY:
        raise HTTPException(status_code=500, detail="AviationStack API key not configured")
    
    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "flight_iata": flight_iata
    }
    
    try:
        response = requests.get(f"{AVIATIONSTACK_BASE_URL}/flights", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"AviationStack API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching flight data: {str(e)}")

def process_flight_data(flight_data: Dict) -> Dict:
    """Uçuş verilerini işle ve formatla"""
    processed_data = {
        "flights": [],
        "summary": {
            "total_flights": 0,
            "active_flights": 0,
            "grounded_flights": 0
        }
    }
    
    if 'data' in flight_data:
        for flight in flight_data['data']:
            flight_info = {
                "airline": flight.get('airline', {}).get('name', 'Unknown'),
                "flight_number": flight.get('flight', {}).get('iata', 'Unknown'),
                "departure": {
                    "airport": flight.get('departure', {}).get('airport', 'Unknown'),
                    "iata": flight.get('departure', {}).get('iata', 'Unknown'),
                    "scheduled": flight.get('departure', {}).get('scheduled', 'Unknown'),
                    "actual": flight.get('departure', {}).get('actual', 'Unknown')
                },
                "arrival": {
                    "airport": flight.get('arrival', {}).get('airport', 'Unknown'),
                    "iata": flight.get('arrival', {}).get('iata', 'Unknown'),
                    "scheduled": flight.get('arrival', {}).get('scheduled', 'Unknown'),
                    "actual": flight.get('arrival', {}).get('actual', 'Unknown')
                },
                "status": flight.get('flight_status', 'Unknown')
            }
            
            processed_data["flights"].append(flight_info)
            processed_data["summary"]["total_flights"] += 1
            
            if flight_info["status"] == "active":
                processed_data["summary"]["active_flights"] += 1
            else:
                processed_data["summary"]["grounded_flights"] += 1
    
    return processed_data

@app.get("/")
async def root():
    return {"message": "TransportAI MCP Server is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(AVIATIONSTACK_API_KEY)
    }

@app.post("/test-flight", 
    response_model=Dict,
    summary="Test AviationStack API Connection",
    description="Test the connection to AviationStack API with a flight IATA code",
    tags=["Flight Information"])
async def test_flight(request: FlightRequest):
    """
    Test the AviationStack API connection with a flight IATA code.
    
    - **flight_iata**: The IATA code of the flight (e.g., "TK1234")
    
    Returns the raw response from AviationStack API.
    """
    if not AVIATIONSTACK_API_KEY:
        raise HTTPException(status_code=500, detail="AviationStack API key not configured")
    
    try:
        response = requests.get(
            f"http://api.aviationstack.com/v1/flights",
            params={
                "access_key": AVIATIONSTACK_API_KEY,
                "flight_iata": request.flight_iata
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching flight data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time model communication"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                request = json.loads(data)
                response = await process_model_request(request)
                await websocket.send_json(response)
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "error": "Invalid JSON format"
                })
            except HTTPException as e:
                await websocket.send_json({
                    "error": e.detail
                })
            except Exception as e:
                await websocket.send_json({
                    "error": str(e)
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        logger.info("WebSocket connection closed")

async def process_model_request(request: Dict) -> Dict:
    """Gelen model isteğini işler ve ilgili modele yönlendirir."""
    try:
        model_request = ModelRequest(**request)
        
        if model_request.model_id == "flight-info":
            # Uçuş bilgisi isteği
            flight_iata = model_request.input_data.get("flight_iata")
            if not flight_iata:
                raise HTTPException(status_code=400, detail="Flight IATA code is required")
            
            raw_flight_data = get_flight_info(flight_iata)
            processed_data = process_flight_data(raw_flight_data)
            
            response = ModelResponse(
                model_id=model_request.model_id,
                output_data=processed_data,
                metadata={"source": "AviationStack API"},
                timestamp=datetime.now().isoformat()
            )
        elif model_request.model_id == "transport-prediction":
            # Ulaşım tahmin modeli isteği (Placeholder)
            # Burada ulaşım tahmin modelinizin işleme mantığını ekleyebilirsiniz
            logger.info(f"Received transport-prediction request with input: {model_request.input_data}")
            # Geçici olarak basit bir yanıt dönelim
            response = ModelResponse(
                model_id=model_request.model_id,
                output_data={
                    "prediction": "Bu bir placeholder yanıttır. Gerçek tahmin burada olacak.",
                    "received_input": model_request.input_data
                    },
                metadata={"status": "placeholder"},
                timestamp=datetime.now().isoformat()
            )
        else:
            # Bilinmeyen model_id
            raise HTTPException(status_code=404, detail=f"Unknown model_id: {model_request.model_id}")
        
        return response.dict()
    except Exception as e:
        logger.error(f"Error in process_model_request: {str(e)}")
        # Hatanın istemciye geri gönderilmesi için HTTPException olarak yeniden fırlat
        if not isinstance(e, HTTPException):
             raise HTTPException(status_code=500, detail=str(e))
        else:
             raise e

@app.get("/models")
async def list_models():
    return {
        "models": [
            {
                "id": "flight-info",
                "name": "Flight Information Model",
                "description": "Uçuş bilgilerini AviationStack API'den alır",
                "version": "1.0.0"
            },
            {
                "id": "transport-prediction",
                "name": "Transport Prediction Model",
                "description": "Ulaşım tahmin modeli",
                "version": "1.0.0"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Server başlatılıyor...")
    logger.info(f"API Key durumu: {'Mevcut' if AVIATIONSTACK_API_KEY else 'Bulunamadı'}")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info") 