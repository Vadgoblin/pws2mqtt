import json
from typing import Any

import paho.mqtt.client as mqtt
import uvicorn
from fastapi import FastAPI, Response, status
from paho.mqtt.enums import CallbackAPIVersion
from starlette.requests import Request

from weather_models import WeatherStationPayload

app = FastAPI()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker. Result code: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("Disconnected from MQTT broker. Result code:", reason_code)


mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)
mqtt_client.connect_async("rpi5.local", 1883, 10)
mqtt_client.loop_start()


@app.get("/weatherstation/updateweatherstation.php")
async def update_weather_station(request: Request):
    data = WeatherStationPayload(**request.query_params)

    processed_payload = data.export_to_dict()
    processed_payload = round_floats(processed_payload)

    mqtt_message = json.dumps(processed_payload)

    mqtt_client.publish("weatherstation", mqtt_message)
    print(json.dumps(processed_payload, indent=2))

    # Weather Underground-compatible stations expect 'success\n' in plain text
    return Response(content="success\n", media_type="text/plain", status_code=status.HTTP_200_OK)


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
