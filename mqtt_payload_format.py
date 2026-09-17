from enum import StrEnum


class MqttPayloadFormat(StrEnum):
    JSON = "json"                       # Single payload: nested JSON
    JSON_FLAT = "json_flat"             # Single payload: flattened JSON
    INDIVIDUAL = "individual"           # Topic tree: weather/outdoor/temperature -> 24.5
    INDIVIDUAL_FLAT = "individual_flat" # Flat topics: weather/outdoor_temp -> 24.5
