import os
from sys import api_version
from datetime import datetime
import time
from pprint import pprint

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
    pprint(sorted(articles, key=lambda a: a.usageCount, reverse=True))

    metrics = client.get_metrics()
    pprint(metrics)
    

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


        metrics = client.get_metrics()

        for k,v in {
            "user_count": metrics.userCount,
            "balance": metrics.balance,
            "transaction_count": metrics.transactionCount
        }.items():
            p = Point(k)
            p.field(field="value", value=v)

            write_api.write(
                bucket=os.environ.get("INFLUXDB_BUCKET"),
                org=os.environ.get("INFLUXDB_ORG"),
                record=p
           )


        write_api.flush()

        time.sleep(UPDATE_INTERVAL)

    
COMMANDS = {
    'render': render,
    'update': update
}

def main():
    Fire(COMMANDS)