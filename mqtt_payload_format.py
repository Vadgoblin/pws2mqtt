from enum import StrEnum


class MQTTPayloadFormat(StrEnum):
    JSON = "json"                        # Single payload: nested JSON
    JSON_FLAT = "json_flat"              # Single payload: flattened JSON
    INDIVIDUAL = "individual"            # Topic tree: weather_station/outdoor/wind_speed
    INDIVIDUAL_FLAT = "individual_flat"  # Flat topics: weather_station/outdoor.wind_speed
