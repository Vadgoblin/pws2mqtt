import json
from typing import Dict, Any

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from flatten_dict import flatten_dict
from mqtt_payload_format import MqttPayloadFormat


class MQTT_Client:
    def __init__(self):
        self._payload_format = MqttPayloadFormat.JSON_FLAT

        self._mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
        self._mqtt_client.on_connect = self._connect_callback
        self._mqtt_client.on_disconnect = self._disconnect_callback
        self._mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)
        self._mqtt_client.connect_async("rpi5.local", 1883, 10)
        self._mqtt_client.loop_start()

    @staticmethod
    def _connect_callback(client, userdata, flags, reason_code, properties):
        print(f"Connected to MQTT broker. Result code: {reason_code}")

    @staticmethod
    def _disconnect_callback(client, userdata, disconnect_flags, reason_code, properties):
        print("Disconnected from MQTT broker. Result code:", reason_code)

    def send_data(self, topic_prefix: str, payload: Dict[str, Any]):
        match self._payload_format:
            case MqttPayloadFormat.JSON:
                mqtt_message = json.dumps(payload)
                self._mqtt_client.publish(topic_prefix, mqtt_message)
            case MqttPayloadFormat.JSON_FLAT:
                payload_flat = flatten_dict(payload)
                mqtt_message = json.dumps(payload_flat)
                self._mqtt_client.publish(topic_prefix, mqtt_message)
            case MqttPayloadFormat.INDIVIDUAL:
                raise NotImplementedError
            case MqttPayloadFormat.INDIVIDUAL_FLAT:
                raise NotImplementedError
