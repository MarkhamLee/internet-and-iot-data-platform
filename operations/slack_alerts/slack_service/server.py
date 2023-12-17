# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# generic service for passing message on to Slack, but putting it here as a
# service the entire K3s cluster can use, I don't need to include Slack clients
# in the other containers

from flask import Flask, request
import flask
import json
from slack_utilities import SlackUtilities


utilities = SlackUtilities()
app = Flask('slack_service')


# endpoint for API health check
# the "ping" endpoint is one that is required by AWS
@app.route("/ping", methods=['GET'])
def health():

    app.logger.info('health check request received')

    results = {"API Status": 200}
    resultjson = json.dumps(results)

    app.logger.info(f'health check response: {resultjson}')

    return flask.Response(response=resultjson, status=200,
                          mimetype='application/json')


@app.route("/send_message", methods=['POST'])
def send_message():

    alert_text = request.form.get('type')
    slack_channel = request.form.get('threshold')

    # send message
    response = utilities.send_slack_message(alert_text, slack_channel)

    results = {"API Status": response}
    resultjson = json.dumps(results)

    return flask.Response(response=resultjson, status=200,
                          mimetype='application/json')
