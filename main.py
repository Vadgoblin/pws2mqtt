import json
from typing import Any

import uvicorn
from fastapi import FastAPI, Response, status
from starlette.requests import Request

from models import WeatherStationPayload

app = FastAPI()


@app.get("/weatherstation/updateweatherstation.php")
async def update_weather_station(request: Request):
    data = WeatherStationPayload(**request.query_params)


    # Process  the data
    # station_payload = data.model_dump()
    processed_payload = serialize_payload(data)
    processed_payload = round_floats(processed_payload)
    print(json.dumps(processed_payload, indent=2))

    # Weather Underground-compatible stations expect 'success\n' in plain text
    return Response(content="success\n", media_type="text/plain", status_code=status.HTTP_200_OK)


def serialize_payload(data: WeatherStationPayload):
    processed_data = {
        "station_id": data.station.station_id,
        "indoor": data.indoor.model_dump(),
        "outdoor": data.outdoor.model_dump(),
        "channels": data.channels.model_dump()
    }

    return processed_data

def round_floats(obj: Any, decimals: int = 2) -> Any:
    """Recursively traverse a dictionary or list and round all float values."""
    if isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(item, decimals) for item in obj]
    return obj

uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    reload=False,
)
