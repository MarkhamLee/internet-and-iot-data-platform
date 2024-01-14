# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# generic service for passing message on to Slack, but putting it here as a
# service the entire K3s cluster can use, I don't need to include Slack clients
# in the other containers

import flask
import json
from flask import Flask, request
from slack_utilities import SlackUtilities
from logging_util import logger


utilities = SlackUtilities()
app = Flask('slack_service')


# endpoint for API health check
# the "ping" endpoint is one that is required by AWS
@app.route("/ping", methods=['GET'])
def health():

    logger.info('health check request received')

    results = {"API Status": 200}
    resultjson = json.dumps(results)

    logger.info(f'health check response: {resultjson}')

    return flask.Response(response=resultjson, status=200,
                          mimetype='application/json')


@app.route("/send_message", methods=['POST'])
def send_message():

    alert_text = request.form.get('text')
    slack_channel = request.form.get('slack_channel')

    logger.info('Message at /send_message endpoint received')

    # send message
    response = utilities.send_slack_message(alert_text, slack_channel)

    resultjson = json.dumps(response)

    return flask.Response(response=resultjson, status=200,
                          mimetype='application/json')


@app.route("/send_webhook", methods=['POST'])
def send_message_webhook():

    alert_text = request.form.get('text')
    slack_webhook = request.form.get('url')

    logger.info('Message at /send_webhook endpoint received')

    # send message
    response = utilities.send_slack_webhook(slack_webhook, alert_text)

    results = {"Message sent status": response}
    resultjson = json.dumps(results)

    return flask.Response(response=resultjson, status=200,
                          mimetype='application/json')
