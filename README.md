**NOTE: this script has been superceeded by [mqttwarn](https://github.com/jpmens/mqttwarn).**
---

# mqtt2xbmc

This program subscribes to any number of MQTT topics (including wildcards) and publishes received payloads as tweets (copy `mqtt2twitter.conf.sample` to `mqtt2twitter.conf` for use). 

See details in the config sample for how to configure this script.

Based on JP Mens [mqtwit](https://github.com/jpmens/mqtwit) script.

## Requirements

* An MQTT broker (e.g. [Mosquitto](http://mosquitto.org))
* Twitter auth tokens
* The Paho Python module: `pip install paho-mqtt`
* The Python Twitter module: `pip install python-twitter`

