#!/usr/bin/env python
# -*- coding: utf-8 -*-

import twitter  # pip install python-twitter
                # https://pypi.python.org/pypi/python-twitter
                # https://github.com/bear/python-twitter

import paho.mqtt.client as paho   # pip install paho-mqtt
import ssl
import sys, time
import os

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2013 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def on_connect(mosq, userdata, rc):
    for topic in userdata['conf']['topics']:
        mqttc.subscribe(topic, 0)

def on_message(mosq, userdata, msg):
    payload = str(msg.payload)

    # text = topic + ': ' + payload
    text = payload
    text = text[0:138]      # truncate for twitter

    tweet(userdata['conf'], text)

def on_disconnect(mosq, userdata, rc):
    print "OOOOPS! disconnected"
    time.sleep(10)

def tweet(conf, status):
    twapi = twitter.Api(
        consumer_key        = conf['consumer_key'],
        consumer_secret     = conf['consumer_secret'],
        access_token_key    = conf['token'],
        access_token_secret = conf['token_secret']
    )

    try:
        res = twapi.PostUpdate(status, trim_user=False)
    except twitter.TwitterError, e:
        print "mqtt2twitter: ", str(e)
    except Exception, e:
        print "mqtt2twitter: ", str(e)

if __name__ == '__main__':

    configfile = os.getenv("MQTT2TWITTERCONF", "mqtt2twitter.conf")
    conf = {}

    try:
        execfile(configfile, conf)
    except Exception, e:
        print "Cannot load %s: %s" % (configfile, str(e))
        sys.exit(2)

    mqttc = paho.Client('mqtt2twitter', clean_session=False, userdata=dict(conf=conf))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    if conf['username'] is not None:
        mqttc.username_pw_set(conf['username'], conf['password'])

    mqttc.will_set('/clients/mqtt2twitter', payload="Adios!", qos=0, retain=False)

    mqttc.connect(conf['broker'], int(conf['port']), 60)

    try:
        mqttc.loop_forever()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        raise

