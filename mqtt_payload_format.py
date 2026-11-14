from enum import StrEnum


class MQTTPayloadFormat(StrEnum):
    JSON = "json"                        # Single payload: nested JSON
    JSON_FLAT = "json_flat"              # Single payload: flattened JSON
    INDIVIDUAL = "individual"            # Topic tree: weather/outdoor/temperature -> 24.5
    INDIVIDUAL_FLAT = "individual_flat"  # Flat topics: weather/outdoor_temperature -> 24.5
