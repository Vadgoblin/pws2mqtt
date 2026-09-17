import json

import uvicorn
from fastapi import FastAPI, Response, status
from starlette.requests import Request

from models import WeatherStationPayload

app = FastAPI()


@app.get("/weatherstation/updateweatherstation.php")
async def update_weather_station(request: Request):
    data = WeatherStationPayload(**request.query_params)

    # Example verification
    # if data.ID != "expected_id" or data.PASSWORD != "expected_password":
    #     return Response(content="INVALIDCREDENTIALS\n", media_type="text/plain", status_code=status.HTTP_401_UNAUTHORIZED)

    # Process  the data
    station_payload = data.model_dump()
    print(json.dumps(station_payload, indent=2))

    # Weather Underground-compatible stations expect 'success\n' in plain text
    return Response(content="success\n", media_type="text/plain", status_code=status.HTTP_200_OK)


uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    reload=False,
)
