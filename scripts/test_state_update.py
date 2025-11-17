#!/usr/bin/env python3
"""
test_state_update.py
Publish a single state update to Ditto-connected MQTT topic.

Usage examples:
  python test_state_update.py                          # defaults to bin/incoming/bin001 -> olive.production:bin001, state=1
  python test_state_update.py --host 193.136.195.37 --port 1884 --topic bin/incoming/bin001 --thing olive.production:bin001 --state 0
  python test_state_update.py --mqtt5 --content-type application/json

Install dependency:
  pip install paho-mqtt
"""

import argparse
import json
import sys

try:
    import paho.mqtt.client as mqtt
    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes
except Exception:
    print("Missing dependency: install paho-mqtt with 'pip install paho-mqtt'", file=sys.stderr)
    raise


def publish_state(host, port, topic, thing, state, mqtt5=False, content_type=None, user=None, password=None):
    payload = {"thingId": thing, "state": state}
    payload_bytes = json.dumps(payload).encode('utf-8')

    if mqtt5:
        client = mqtt.Client(protocol=mqtt.MQTTv5)
    else:
        client = mqtt.Client()

    # set username/password if provided
    if user is not None:
        # password may be None (username-only) — paho allows that
        client.username_pw_set(user, password)
    try:
        client.connect(host, port, 60)
    except Exception as e:
        print(f"Failed to connect to {host}:{port}: {e}")
        return 2

    if mqtt5 and content_type:
        props = Properties(PacketTypes.PUBLISH)
        props.ContentType = content_type
        info = client.publish(topic, payload_bytes, qos=0, properties=props)
    else:
        info = client.publish(topic, payload_bytes, qos=0)

    # wait for publish to complete
    try:
        info.wait_for_publish()
    except Exception:
        pass

    if info.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Published -> topic: {topic}\n payload: {json.dumps(payload)}")
        client.disconnect()
        return 0
    else:
        print(f"Publish failed (rc={info.rc})")
        client.disconnect()
        return 3


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='193.136.195.37', help='MQTT broker host')
    p.add_argument('--port', default=1884, type=int, help='MQTT broker port')
    p.add_argument('--topic', default='bin/incoming/bin001', help='MQTT topic')
    p.add_argument('--thing', default='olive.production:bin001', help='thingId')
    p.add_argument('--state', default=1, help='state value (int or string)')
    p.add_argument('--mqtt5', action='store_true', help='Use MQTT v5 and allow Content-Type property')
    p.add_argument('--content-type', default=None, help='Content-Type property to set when using MQTT v5')
    p.add_argument('--user', default=None, help='MQTT username (optional)')
    p.add_argument('--password', default=None, help='MQTT password (optional)')
    args = p.parse_args()

    # convert state to int if possible
    try:
        state_val = int(args.state)
    except Exception:
        try:
            state_val = float(args.state)
        except Exception:
            state_val = args.state

    rc = publish_state(
        args.host,
        args.port,
        args.topic,
        args.thing,
        state_val,
        mqtt5=args.mqtt5,
        content_type=args.content_type,
        user=args.user,
        password=args.password,
    )
    sys.exit(rc)


if __name__ == '__main__':
    main()
