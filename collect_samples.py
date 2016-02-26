import os
import platform
import psutil
from datetime import datetime
import time
from dateutil.tz import tzlocal

from influxdb import InfluxDBClient

# Influx connection details
HOST = "localhost"
PORT = 8086
DB = "demo"
USERNAME = None
PASSWORD = None
USE_SSL = False

SAMPLE_COUNT = 100
SAMPLE_INTERVAL_SECONDS = 0.5


def main():
  """
  Main demo program. Takes samples of computer metrics and stores them into
  InfluxDB.
  """
  influxClient = InfluxDBClient(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    ssl=USE_SSL
  )

  setupDatabase(influxClient)

  for i in xrange(SAMPLE_COUNT):
    print "Collection sample of your computer metrics..."
    if i % 10 == 0:
      print "\t({} samples remaining before I quit)".format(SAMPLE_COUNT - i)

    # Sample computer for metrics.
    sample = getSample()

    # Create an object to write to InfluxDB containing all sample measurements.
    payload = createInfluxPayload(sample)

    # Write all measurements.
    influxClient.write_points(payload)

    # Wait.
    time.sleep(SAMPLE_INTERVAL_SECONDS)


def createInfluxPayload(sample):
  """
  Given a metric sample, creates a payload object to write to InfluxDB.
  """
  payload = []
  sampleTime = sample["time"]
  # This timestamp needs to be 19 digits long and contain millisecond
  # precision.
  timestamp = int(
    time.mktime(sampleTime.timetuple())*1e3 + sampleTime.microsecond/1e3
  ) * 1000000


  # CPU measurement
  payload.append({
    "tags": getTags(),
    "time": timestamp,
    "measurement": "cpu",
    "fields": {
      "percent": sample["cpu"]
    }
  })
  # Disk measurement
  payload.append({
    "tags": getTags(),
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
    "tags": getTags(),
    "time": timestamp,
    "measurement": "memory",
    "fields": {
      "percent": sample["memory"],
    }
  })
  # Network measurement
  payload.append({
    "tags": getTags(),
    "time": timestamp,
    "measurement": "network",
    "fields": {
      "bytesSent": sample["bytesSent"],
      "bytesReceived": sample["bytesReceived"],
    }
  })
  return payload


def getTags():
  """
  Gets the InfluxDB tags we want to use for metrics being stored from this
  program.
  """
  return {
    "user": os.environ["USER"],
    # "host": platform.node(),
    "timezone": datetime.now(tzlocal()).tzname(),
  }


def getSample():
  """
  Samples some metrics on this computer right now. Returns timestamp of the
  sample with the sample.
  """
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
  """
  Creates a database for this demo if one does not exist. Creates a 1-hour
  retention policy if one does not exist. Switches to use the new database for
  default queries.
  """
  databases = client.get_list_database()
  if DB not in [d["name"] for d in databases]:
    print "Creating Influx database '%s'..." % DB
    client.create_database(DB)

  print "Using Influx database '%s'." % DB
  client.switch_database(DB)

  retentionPolicyName = "one_hour"
  retentionPolicyDuration = "1h"
  retentionPolicies = client.get_list_retention_policies()
  if retentionPolicyName not in [rp["name"] for rp in retentionPolicies]:
    print "Creating {} retention policy called \"{}\"...".format(
      retentionPolicyDuration, retentionPolicyName
    )
    client.create_retention_policy(
      retentionPolicyName, retentionPolicyDuration, 1, database=DB, default=True
    )



if __name__ == "__main__":
  main()
