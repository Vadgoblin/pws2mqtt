from typing import Optional, Any

from pydantic import BaseModel, Field, model_validator, PrivateAttr

from converter import WeatherUnits


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
    _is_normalized: bool = PrivateAttr(default=False)

    # Pressure
    barometric_pressure: Optional[float] = Field(default=None, validation_alias="baromin")

    # Ambient air
    temperature: Optional[float] = Field(default=None, validation_alias="tempf")
    dew_point: Optional[float] = Field(default=None, validation_alias="dewptf")
    humidity: Optional[int] = Field(default=None, validation_alias="humidity")

    # Wind
    wind_speed: Optional[float] = Field(default=None, validation_alias="windspeedmph")
    wind_gust: Optional[float] = Field(default=None, validation_alias="windgustmph")
    wind_direction: Optional[int] = Field(default=None, validation_alias="winddir")

    # Rain
    rain_rate: Optional[float] = Field(default=None, validation_alias="rainin")
    daily_rain: Optional[float] = Field(default=None, validation_alias="dailyrainin")

    # Solar
    solar_radiation: Optional[float] = Field(default=None, validation_alias="solarradiation")
    uv_index: Optional[float] = Field(default=None, validation_alias="UV")

    @model_validator(mode="after")
    def normalize_to_metric(self) -> "OutdoorEnvironment":
        if self._is_normalized:
            return self

        self.temperature = WeatherUnits.f_to_c(self.temperature)
        self.dew_point = WeatherUnits.f_to_c(self.dew_point)
        self.barometric_pressure = WeatherUnits.inhg_to_hpa(self.barometric_pressure)
        self.wind_speed = WeatherUnits.mph_to_kmh(self.wind_speed)
        self.wind_gust = WeatherUnits.mph_to_kmh(self.wind_gust)
        self.rain_rate = WeatherUnits.in_to_mm(self.rain_rate)
        self.daily_rain = WeatherUnits.in_to_mm(self.daily_rain)

        self._is_normalized = True
        return self


class ChannelReading(BaseModel):
    temperature_f: float
    humidity_pct: Optional[int] = None


class WeatherStationPayload(BaseModel):
    station: StationInfo
    indoor: IndoorEnvironment
    outdoor: OutdoorEnvironment
    channels: dict[int, ChannelReading] = Field(default_factory=dict)

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

        channels: dict[int, ChannelReading] = {}
        for ch in range(1, 8):
            # Channel 1 often has no digit suffix in firmware aliases
            temp_key = "soiltempf" if ch == 1 else f"soiltemp{ch}f"
            hum_key = "soilmoisture" if ch == 1 else f"soilmoisture{ch}"

            raw_temp = data.get(temp_key)
            raw_hum = data.get(hum_key)

            if raw_temp is not None:
                try:
                    channels[ch] = ChannelReading(
                        temperature_f=float(raw_temp),
                        humidity_pct=int(raw_hum) if raw_hum is not None else None,
                    )

                except (ValueError, TypeError):
                    continue

        return {
            "station": station,
            "indoor": indoor,
            "outdoor": outdoor,
            "channels": channels,
        }
