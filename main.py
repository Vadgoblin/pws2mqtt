import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends, Response, status
from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request

app = FastAPI()


class WeatherStationData(BaseModel):
    # Credentials and metadata
    station_id: str = Field(validation_alias="ID")
    password: str = Field(validation_alias="PASSWORD", exclude=True)
    action: str = "updateraww"
    realtime: Optional[int] = None
    rtfreq: Optional[int] = None
    dateutc: Optional[str] = None

    # Outdoor stations
    # Pressure
    barometric_pressure_in: Optional[float] = Field(default=None, validation_alias="baromin")

    # Temperature & Humidity
    temperature_f: Optional[float] = Field(default=None, validation_alias="tempf")
    dew_point_f: Optional[float] = Field(default=None, validation_alias="dewptf")
    humidity_pct: Optional[int] = Field(default=None, validation_alias="humidity")

    # Wind
    wind_speed_mph: Optional[float] = Field(default=None, validation_alias="windspeedmph")
    wind_gust_mph: Optional[float] = Field(default=None, validation_alias="windgustmph")
    wind_direction_deg: Optional[int] = Field(default=None, validation_alias="winddir")

    # Rain
    rain_rate_in: Optional[float] = Field(default=None, validation_alias="rainin")
    daily_rain_in: Optional[float] = Field(default=None, validation_alias="dailyrainin")

    # Solar & Light
    solar_radiation_wm2: Optional[float] = Field(default=None, validation_alias="solarradiation")
    uv_index: Optional[float] = Field(default=None, validation_alias="UV")

    # Indoor station
    indoor_temp_f: Optional[float] = Field(default=None, validation_alias="indoortempf")
    indoor_humidity: Optional[int] = Field(default=None, validation_alias="indoorhumidity")

    # Remote Air Sensors (1 to 7)
    channel_1_temperature: Optional[float] = Field(default=None, validation_alias="soiltempf", exclude_if=lambda v: v is None)
    channel_1_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture", exclude_if=lambda v: v is None)

    channel_2_temperature: Optional[float] = Field(default=None, validation_alias="soiltemp2f", exclude_if=lambda v: v is None)
    channel_2_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture2", exclude_if=lambda v: v is None)

    channel_3_temperature: Optional[float] = Field(default=None, validation_alias="soiltemp3f", exclude_if=lambda v: v is None)
    channel_3_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture3", exclude_if=lambda v: v is None)

    channel_4_temperature: Optional[float] = Field(default=None, validation_alias="soiltemp4f", exclude_if=lambda v: v is None)
    channel_4_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture4", exclude_if=lambda v: v is None)

    channel_5_temperature: Optional[float] = Field(default=None, validation_alias="soiltemp5f", exclude_if=lambda v: v is None)
    channel_5_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture5", exclude_if=lambda v: v is None)

    channel_6_temperature: Optional[float] = Field(default=None, validation_alias="soiltemp6f", exclude_if=lambda v: v is None)
    channel_6_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture6", exclude_if=lambda v: v is None)

    channel_7_temperature: Optional[float] = Field(default=None, validation_alias="soiltemp7f", exclude_if=lambda v: v is None)
    channel_7_humidity: Optional[int] = Field(default=None, validation_alias="soilmoisture7", exclude_if=lambda v: v is None)

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
