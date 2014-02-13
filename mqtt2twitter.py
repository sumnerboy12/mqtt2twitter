#!/usr/bin/env python
# -*- coding: utf-8 -*-

import twitter  # pip install python-twitter
                # https://pypi.python.org/pypi/python-twitter
                # https://github.com/bear/python-twitter
import paho.mqtt.client as paho   # pip install paho-mqtt
import logging
import os
import signal
import sys
import time

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2013 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

# script name used for conf/log file names etc
SCRIPTNAME = 'mqtt2twitter'

# get the config and log file names
CONFIGFILE = os.getenv(SCRIPTNAME.upper() + 'CONF', SCRIPTNAME + ".conf")
LOGFILE = os.getenv(SCRIPTNAME.upper() + 'LOG', SCRIPTNAME + ".log")

# load configuration
conf = {}
try:
    execfile(CONFIGFILE, conf)
except Exception, e:
    print "Cannot load configuration %s: %s" % (CONFIGFILE, str(e))
    sys.exit(2)

LOGLEVEL = conf.get('loglevel', logging.DEBUG)
LOGFORMAT = conf.get('logformat', '%(asctime)-15s %(message)s')

MQTT_HOST = conf.get('broker', 'localhost')
MQTT_PORT = int(conf.get('port', 1883))
MQTT_LWT = conf.get('lwt', None)

# initialise logging    
logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
logging.info("Starting " + SCRIPTNAME)
logging.info("INFO MODE")
logging.debug("DEBUG MODE")

# initialise MQTT broker connection
mqttc = paho.Client(SCRIPTNAME, clean_session=False)

# check for authentication
if conf['username'] is not None:
    mqttc.username_pw_set(conf['username'], conf['password'])

# configure the last-will-and-testament
if MQTT_LWT is not None:
    mqttc.will_set(MQTT_LWT, payload=SCRIPTNAME, qos=0, retain=False)

def connect():
    """
    Connect to the broker
    """
    logging.debug("Attempting connection to MQTT broker %s:%d..." % (MQTT_HOST, MQTT_PORT))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    result = mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
    if result == 0:
        mqttc.loop_forever()
    else:
        logging.info("Connection failed with error code %s. Retrying in 10s...", result)
        time.sleep(10)
        connect()
         
def disconnect(signum, frame):
    """
    Signal handler to ensure we disconnect cleanly 
    in the event of a SIGTERM or SIGINT.
    """
    logging.debug("Disconnecting from MQTT broker...")
    mqttc.loop_stop()
    mqttc.disconnect()
    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)

def tweet(message):
    logging.debug("Tweeting %s..." % message)
    twapi = twitter.Api(
        consumer_key        = conf['consumer_key'],
        consumer_secret     = conf['consumer_secret'],
        access_token_key    = conf['token'],
        access_token_secret = conf['token_secret']
    )

    try:
        res = twapi.PostUpdate(message, trim_user=False)
    except twitter.TwitterError, e:
        logging.error("TwitterError: %s" % str(e))
    except Exception, e:
        logging.error("Error: %s" % str(e))

def on_connect(mosq, userdata, result_code):
    logging.debug("Connected to MQTT broker, subscribing to topics...")
    for sub in conf['topics']:
        logging.debug("Subscribing to %s" % sub)
        mqttc.subscribe(sub, 0)

def on_message(mosq, userdata, msg):
    """
    Message received from the broker
    """
    topic = msg.topic
    payload = str(msg.payload)
    logging.debug("Message received on %s: %s" % (topic, payload))

    # Try to find matching settings for this topic
    for sub in conf['topics']:
        if paho.topic_matches_sub(sub, topic):
            tweet(payload[0:138])
            break

def on_disconnect(mosq, userdata, result_code):
    """
    Handle disconnections from the broker
    """
    if result_code == 0:
        logging.info("Clean disconnection")
    else:
        logging.info("Unexpected disconnection! Reconnecting in 5 seconds...")
        logging.debug("Result code: %s", result_code)
        time.sleep(5)
        connect()

# use the signal module to handle signals
signal.signal(signal.SIGTERM, disconnect)
signal.signal(signal.SIGINT, disconnect)
        
# connect to broker and start listening
connect()
