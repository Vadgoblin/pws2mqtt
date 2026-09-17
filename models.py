from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator



class StationInfo(BaseModel):
    station_id: str = Field(validation_alias="ID")
    password: str = Field(validation_alias="PASSWORD", exclude=True)
    action: str = "updateraww"
    realtime: Optional[int] = None
    rtfreq: Optional[int] = None
    dateutc: Optional[str] = None


class IndoorEnvironment(BaseModel):
    temperature_f: Optional[float] = Field(default=None, validation_alias="indoortempf")
    humidity_pct: Optional[int] = Field(default=None, validation_alias="indoorhumidity")


class OutdoorEnvironment(BaseModel):
    # Pressure
    barometric_pressure_in: Optional[float] = Field(default=None, validation_alias="baromin")

    # Ambient air
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

    # Solar
    solar_radiation_wm2: Optional[float] = Field(default=None, validation_alias="solarradiation")
    uv_index: Optional[float] = Field(default=None, validation_alias="UV")


class RemoteChannelReading(BaseModel):
    channel: int
    temperature_f: float
    humidity_pct: Optional[int] = None



class WeatherStationPayload(BaseModel):
    station: StationInfo
    indoor: IndoorEnvironment
    outdoor: OutdoorEnvironment
    channels: list[RemoteChannelReading] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def assemble_from_flat_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            # Supports MultiDict/QueryParams (FastAPI Request.query_params)
            data = dict(data)

        # # Helper to convert blank/placeholder strings to None
        # cleaned: dict[str, Any] = {
        #     k: (None if v in ("", "null", "NULL", "--", "N/A") else v)
        #     for k, v in data.items()
        # }


        station = StationInfo.model_validate(data)
        indoor = IndoorEnvironment.model_validate(data)
        outdoor = OutdoorEnvironment.model_validate(data)

        channels: list[RemoteChannelReading] = []
        for ch in range(1, 8):
            # Channel 1 often has no digit suffix in firmware aliases
            temp_key = "soiltempf" if ch == 1 else f"soiltemp{ch}f"
            hum_key = "soilmoisture" if ch == 1 else f"soilmoisture{ch}"

            raw_temp = data.get(temp_key)
            raw_hum = data.get(hum_key)

            if raw_temp is not None:
                try:
                    channels.append(
                        RemoteChannelReading(
                            channel=ch,
                            temperature_f=float(raw_temp),
                            humidity_pct=int(raw_hum) if raw_hum is not None else None,
                        )
                    )
                except (ValueError, TypeError):
                    continue

        return {
            "station": station,
            "indoor": indoor,
            "outdoor": outdoor,
            "channels": channels,
        }