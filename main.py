from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Response, status
from starlette.requests import Request

from mqtt_client import MQTT_Client
from weather_models import WeatherStationPayload

app = FastAPI()
mqtt_client = MQTT_Client()


@app.get("/weatherstation/updateweatherstation.php")
async def update_weather_station(request: Request):
    data = WeatherStationPayload(**request.query_params)
    station_id = data.station.station_id
    payload = await preprocess_data(data)

    mqtt_client.send_data(f"weather_station/{station_id}", payload)
    # print(json.dumps(processed_payload, indent=2))

    # Weather Underground-compatible stations expect 'success\n' in plain text
    return Response(content="success\n", media_type="text/plain", status_code=status.HTTP_200_OK)


async def preprocess_data(data: WeatherStationPayload) -> Dict[str, Any]:
    station_data = data.export_to_dict()
    del station_data["station_id"]

    return round_floats(station_data)


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
