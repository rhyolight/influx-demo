import os
import psutil
from datetime import datetime
import time
from dateutil.tz import tzlocal

from influxdb import InfluxDBClient

HOST = "localhost"
PORT = 8086
DB = "demo"
USERNAME = None
PASSWORD = None
USER = os.environ["USER"]
SAMPLE_COUNT = 100
SAMPLE_INTERVAL_SECONDS = 1


def main():
  influxClient = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    ssl=False
  )

  setupDatabase(influxClient)

  timezone = datetime.now(tzlocal()).tzname()

  for i in xrange(SAMPLE_COUNT):
    print "Collection sample of your computer metrics..."
    if i % 10 == 0:
      print "\t({} samples remaining before I quit)".format(SAMPLE_COUNT - i)
    sample = getSample()
    timestamp = int(time.mktime(sample["time"].timetuple()))

    payload = createInfluxPayload(sample, timestamp, timezone)

    # Write all measurements
    influxClient.write_points(payload)
    # Wait.
    time.sleep(SAMPLE_INTERVAL_SECONDS)


def createInfluxPayload(sample, timestamp, timezone):
  payload = []
  # CPU measurement
  payload.append({
    "tags": {
      "user": USER,
      "timezone": timezone,
    },
    "time": timestamp,
    "measurement": "cpu",
    "fields": {
      "percent": sample["cpu"]
    }
  })
  # Disk measurement
  payload.append({
    "tags": {
      "user": USER,
      "timezone": timezone,
    },
    "time": timestamp,
    "measurement": "disk",
    "fields": {
      "writeBytes": sample["writeBytes"],
      "readTime": sample["readTime"],
      "writeTime": sample["writeTime"],
    }
  })
  # Memory measurement
  payload.append({
    "tags": {
      "user": USER,
      "timezone": timezone,
    },
    "time": timestamp,
    "measurement": "memory",
    "fields": {
      "percent": sample["memory"],
    }
  })
  # Network measurement
  payload.append({
    "tags": {
      "user": USER,
      "timezone": timezone,
    },
    "time": timestamp,
    "measurement": "network",
    "fields": {
      "bytesSent": sample["bytesSent"],
      "bytesReceived": sample["bytesReceived"],
    }
  })
  return payload


def getSample():
  diskCounters = psutil.disk_io_counters()
  netCounters = psutil.net_io_counters()
  return {
    "cpu": psutil.cpu_percent(),
    "writeBytes": diskCounters.write_bytes,
    "readTime": diskCounters.read_time,
    "writeTime": diskCounters.write_time,
    "memory": psutil.virtual_memory().percent,
    "bytesSent": netCounters.bytes_sent,
    "bytesReceived": netCounters.bytes_recv,
    "time": datetime.now()
  }


def setupDatabase(client):
  databases = client.get_list_database()
  if DB not in [d["name"] for d in databases]:
    print "Creating Influx database '%s'..." % DB
    client.create_database(DB)
  print "Using Influx database '%s'." % DB
  client.switch_database(DB)


if __name__ == "__main__":
  main()
