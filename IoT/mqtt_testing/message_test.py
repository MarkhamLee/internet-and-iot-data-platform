import json
import os
import sys
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()


# Load connection variables
TOPIC = '/test/topic'
MQTT_BROKER = os.environ['MQTT_BROKER']
MQTT_USER = os.environ['MQTT_USER']
MQTT_SECRET = os.environ['MQTT_SECRET']
MQTT_PORT = int(os.environ['MQTT_PORT'])


def main():

    loop_count = 0

    # get unique client ID
    clientID = com_utilities.getClientID()

    # get mqtt client
    client = com_utilities.mqttClient(clientID,
                                      MQTT_USER,
                                      MQTT_SECRET,
                                      MQTT_BROKER,
                                      MQTT_PORT)
    # start device monitoring

    while loop_count < 10:

        payload = {
            "key1": "test-data1",
            "key2": "test-data2"
        }

        payload = json.dumps(payload)
        client.publish(TOPIC, payload)
        loop_count += 1

        sleep(1)

    client.loop_stop()


if __name__ == "__main__":
    main()
