from paho.mqtt import client as mqtt
import uuid
from hw_library.logging_util import logger


class Communications():

    def __init__(self):

        pass

    @staticmethod
    def get_client_id():

        client_id = str(uuid.uuid4())

        return client_id

    @staticmethod
    def mqtt_client(client_id: str, user_name: str, pwd: str,
                    host: str, port: int):

        def connection_status(client, user_data, flags, code):

            if code == 0:
                print('connected')

            else:
                print(f'connection error: {code} retrying...')
                logger.DEBUG(f'connection error occured, return code: {code}')

        client = mqtt.Client(client_id)
        client.username_pw_set(username=user_name, password=pwd)
        client.on_connect = connection_status

        code = client.connect(host, port)

        # this is so that the client will attempt to reconnect automatically/
        # no need to add reconnect
        # logic.
        client.loop_start()

        return client, code
