import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion


class MQTT_Client:
    def __init__(self):
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

    def send_json(self, payload:str):
        self._mqtt_client.publish("weatherstation", payload)
