import os
from sys import api_version
from datetime import datetime
import time

from fire import Fire
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from strichliste2influxdb.api.strichliste import StrichlisteClient

UPDATE_INTERVAL = int(os.environ.get("STRICHLISTE_UPDATE_INTERVAL", "60"))

influx = InfluxDBClient(
    api_version=2,
    url=os.environ.get("INFLUXDB_URL"),
    token=os.environ.get("INFLUXDB_TOKEN")
)

write_api = influx.write_api(write_options=SYNCHRONOUS)

def render():
    client = StrichlisteClient(os.environ.get("STRICHLISTE_BASE_URL"))
    articles = list(client.get_articles())
    from pprint import pprint; pprint(sorted(articles, key=lambda a: a.usageCount, reverse=True))
    print(len(articles))

def update():
    client = StrichlisteClient(os.environ.get("STRICHLISTE_BASE_URL"))

    while True:
        articles = list(client.get_articles())
        for a in articles:
            record = Point("usage_times")
            record.field(field="value", value=a.usageCount)
            record.tag(key="id", value=a.id)
            record.tag(key="name", value=a.name)

            write_api.write(
                bucket=os.environ.get("INFLUXDB_BUCKET"),
                org=os.environ.get("INFLUXDB_ORG"),
                record=record
            )

        write_api.flush()

        print(f"[i] wrote {len(articles)} points to influx")

        time.sleep(UPDATE_INTERVAL)

    
COMMANDS = {
    'render': render,
    'update': update
}

def main():
    Fire(COMMANDS)