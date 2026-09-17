import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends, Response, status
from pydantic import BaseModel, ConfigDict
from starlette.requests import Request

app = FastAPI()


class WeatherStationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Credentials and metadata
    ID: str
    PASSWORD: str
    action: str = "updateraww"
    realtime: Optional[int] = None
    rtfreq: Optional[int] = None
    dateutc: Optional[str] = None

    # Weather observations
    baromin: Optional[float] = None
    tempf: Optional[float] = None
    dewptf: Optional[float] = None
    humidity: Optional[int] = None
    windspeedmph: Optional[float] = None
    windgustmph: Optional[float] = None
    winddir: Optional[int] = None
    rainin: Optional[float] = None
    dailyrainin: Optional[float] = None
    solarradiation: Optional[float] = None
    UV: Optional[float] = None

    # Indoor
    indoortempf: Optional[float] = None
    indoorhumidity: Optional[int] = None


    # soiltempf: Optional[float] = None
    # soilmoisture: Optional[int] = None


@app.get("/weatherstation/updateweatherstation.php")
async def update_weather_station(request: Request):
    data = WeatherStationData(**request.query_params)

    # Example verification
    # if data.ID != "expected_id" or data.PASSWORD != "expected_password":
    #     return Response(content="INVALIDCREDENTIALS\n", media_type="text/plain", status_code=status.HTTP_401_UNAUTHORIZED)

    # Process  the data
    station_payload = data.model_dump()
    print(station_payload)
    print(json.dumps(station_payload, indent=2))

    # Weather Underground-compatible stations expect 'success\n' in plain text
    return Response(content="success\n", media_type="text/plain", status_code=status.HTTP_200_OK)


uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    reload=False,
)
