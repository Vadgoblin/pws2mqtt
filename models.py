from typing import Optional, Any

from pydantic import BaseModel, Field, model_validator, PrivateAttr, RootModel

from converter import WeatherUnits


class StationInfo(BaseModel):
    station_id: str = Field(validation_alias="ID")
    password: str = Field(validation_alias="PASSWORD", exclude=True)
    action: str = "updateraww"
    realtime: Optional[int] = None
    rtfreq: Optional[int] = None
    dateutc: Optional[str] = None


class IndoorEnvironment(BaseModel):
    _is_normalized: bool = PrivateAttr(default=False)

    temperature: Optional[float] = Field(default=None, validation_alias="indoortempf")
    humidity: Optional[int] = Field(default=None, validation_alias="indoorhumidity")
    barometric_pressure: Optional[float] = Field(default=None, validation_alias="baromin")

    @model_validator(mode="after")
    def normalize_to_metric(self) -> "IndoorEnvironment":
        if self._is_normalized:
            return self

        self.temperature = WeatherUnits.f_to_c(self.temperature)
        self.barometric_pressure = WeatherUnits.inhg_to_hpa(self.barometric_pressure)

        self._is_normalized = True
        return self


class OutdoorEnvironment(BaseModel):
    _is_normalized: bool = PrivateAttr(default=False)

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
    illuminance: Optional[float] = None
    uv_index: Optional[float] = Field(default=None, validation_alias="UV")

    @model_validator(mode="after")
    def compute_illuminance(self) -> "OutdoorEnvironment":
        if self.solar_radiation is not None:
            self.illuminance = WeatherUnits.wm2_to_lux(self.solar_radiation)
        return self

    @model_validator(mode="after")
    def normalize_to_metric(self) -> "OutdoorEnvironment":
        if self._is_normalized:
            return self

        self.temperature = WeatherUnits.f_to_c(self.temperature)
        self.dew_point = WeatherUnits.f_to_c(self.dew_point)
        self.wind_speed = WeatherUnits.mph_to_kmh(self.wind_speed)
        self.wind_gust = WeatherUnits.mph_to_kmh(self.wind_gust)
        self.rain_rate = WeatherUnits.in_to_mm(self.rain_rate)
        self.daily_rain = WeatherUnits.in_to_mm(self.daily_rain)

        self._is_normalized = True
        return self


class ChannelReading(BaseModel):
    _is_normalized: bool = PrivateAttr(default=False)

    temperature: float
    humidity: Optional[int] = None

    @classmethod
    def from_raw_data(cls, data: dict, channel: int) -> Optional["ChannelReading"]:
        # Firmware quirk: channel 1 has no suffix
        t_key = "soiltempf" if channel == 1 else f"soiltemp{channel}f"
        h_key = "soilmoisture" if channel == 1 else f"soilmoisture{channel}"

        raw_temp = data.get(t_key)
        if raw_temp is None:
            return None

        return cls.model_validate({
            "temperature": raw_temp,
            "humidity": data.get(h_key),
        })

    @model_validator(mode="after")
    def normalize_to_metric(self) -> "ChannelReading":
        if self._is_normalized:
            return self

        self.temperature = WeatherUnits.f_to_c(self.temperature)

        self._is_normalized = True
        return self


class Channels(RootModel[dict[int, ChannelReading]]):
    @model_validator(mode="before")
    @classmethod
    def parse_flat(cls, data: Any) -> dict[int, ChannelReading]:
        if not isinstance(data, dict):
            return {}

        return {
            ch: reading
            for ch in range(1, 8)
            if (reading := ChannelReading.from_raw_data(data, ch)) is not None
        }


class WeatherStationPayload(BaseModel):
    station: StationInfo
    indoor: IndoorEnvironment
    outdoor: OutdoorEnvironment
    channels: Channels

    @model_validator(mode="before")
    @classmethod
    def assemble_from_flat_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            data = dict(data)

        station = StationInfo.model_validate(data)
        indoor = IndoorEnvironment.model_validate(data)
        outdoor = OutdoorEnvironment.model_validate(data)
        channels = Channels.model_validate(data)

        return {
            "station": station,
            "indoor": indoor,
            "outdoor": outdoor,
            "channels": channels,
        }
