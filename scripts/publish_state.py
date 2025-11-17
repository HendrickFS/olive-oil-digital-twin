#!/usr/bin/env python3
"""
publish_state.py
Simple MQTT publisher to send: {"thingId":"olive.production:bin001","state":0}

Usage:
  python publish_state.py                      # uses defaults
  python publish_state.py --host 193.136.195.37 --port 1884 --topic bin/incoming/bin001 --thing olive.production:bin001 --state 0
  python publish_state.py --mqtt5 --content-type application/json

Requires: paho-mqtt
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


def publish(host, port, topic, thingId, state_value, mqtt5=False, content_type=None):
    payload = {"thingId": thingId, "state": state_value}
    payload_str = json.dumps(payload)

    if mqtt5:
        client = mqtt.Client(protocol=mqtt.MQTTv5)
    else:
        client = mqtt.Client()

    #!/usr/bin/env python3
    """
    publish_state.py
    Publisher helper that can:
     - publish a single JSON state message (thingId + state/value)
     - process an XML file (same logic you provided) and publish messages per sensor

    Usage:
      python publish_state.py --publish --host 193.136.195.37 --port 1884 --topic bin/incoming/bin001 --thing olive.production:bin001 --state 0
      python publish_state.py --xml exemplo.xml

    The XML processing mirrors the script you shared: it builds topic names like
      <shortname>/incoming/<id>  (e.g. bin/incoming/bin001)
    and payloads like {"thingId":"olive.production:bin001","temperature":25.0}

    Requires: paho-mqtt
      pip install paho-mqtt
    """

    import argparse
    import json
    import sys
    import re
    import xml.etree.ElementTree as ET

    try:
        import paho.mqtt.client as mqtt
    except Exception:
        print("Missing dependency: install paho-mqtt with 'pip install paho-mqtt'", file=sys.stderr)
        raise

    MQTT_BROKER_DEFAULT = '193.136.195.37'
    MQTT_PORT_DEFAULT = 1884

    id_dict = {
        '0': 'olive.production:centrifuge001',
        '1': 'olive.production:decanter001',
        '2': 'olive.production:deposit001',
        '3': 'olive.production:mixer001',
        '4': 'olive.production:mixer002',
        '5': 'olive.production:centrifuge001',
        '6': 'olive.production:decanter001',
        '7': 'olive.production:mill001',
    }

    body_dict = {
        '0': 'temperature',
        '1': 'temperature',
        '2': 'temperature',
        '3': 'temperature',
        '4': 'temperature',
        '5': 'inputTemperature',
        '6': 'inputTemperature',
        '7': 'temperature',
    }


    def extract_name(name: str) -> str:
        match = re.match(r"([a-zA-Z]+)", name)
        if not match:
            return name
        return match.group(1)


    def publish_message(client, topic, payload):
        # publish as utf-8 bytes
        client.publish(topic, json.dumps(payload).encode('utf-8'))


    def process_xml_and_publish(xml_string, broker, port):
        root = ET.fromstring(xml_string)
        sensors = root.findall('.//Sensors/Entry')
        sensors_list = []
        for sensor in sensors:
            sid = sensor.findtext('ID')
            field = body_dict.get(sid, 'unknown')
            thing = id_dict.get(sid, 'unknown')
            val_text = sensor.findtext('Val')
            if val_text is None:
                continue
            # numeric conversion and scaling for temperature
            if field in ('temperature', 'inputTemperature'):
                try:
                    value = float(val_text) / 100.0
                except Exception:
                    value = val_text
            else:
                value = val_text

            sensor_data = {
                'thingId': thing,
                field: value
            }
            sensors_list.append(sensor_data)

        client = mqtt.Client()
        client.connect(broker, port, 60)
        client.loop_start()

        for sensor in sensors_list:
            short = extract_name(sensor['thingId'].split(':')[1])
            topic = f"{short}/incoming/{sensor['thingId'].split(':')[1]}"
            print(f"Publishing to {topic}: {sensor}")
            publish_message(client, topic, sensor)

        client.loop_stop()
        client.disconnect()


    def publish_single(broker, port, topic, thing, state):
        payload = {'thingId': thing}
        # if state is numeric, send as number, else keep as-is
        payload['state'] = state
        client = mqtt.Client()
        client.connect(broker, port, 60)
        publish_message(client, topic, payload)
        client.disconnect()
        print(f"Published {payload} to {topic}")


    def main():
        p = argparse.ArgumentParser()
        p.add_argument('--host', default=MQTT_BROKER_DEFAULT)
        p.add_argument('--port', default=MQTT_PORT_DEFAULT, type=int)
        p.add_argument('--xml', help='Path to XML file to process and publish')
        p.add_argument('--publish', action='store_true', help='Publish a single state message')
        p.add_argument('--topic', default='bin/incoming/bin001')
        p.add_argument('--thing', default='olive.production:bin001')
        p.add_argument('--state', default=0)
        args = p.parse_args()

        if args.xml:
            with open(args.xml, 'r', encoding='utf-8') as fh:
                xml_string = fh.read()
            process_xml_and_publish(xml_string, args.host, args.port)
            return

        if args.publish:
            # try to interpret state as number
            try:
                s = int(args.state)
            except Exception:
                try:
                    s = float(args.state)
                except Exception:
                    s = args.state
            publish_single(args.host, args.port, args.topic, args.thing, s)
            return

        print("Nothing done. Use --xml <file> or --publish with --thing/--state")


    if __name__ == '__main__':
        main()
