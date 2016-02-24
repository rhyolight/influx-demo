> This is a demo of InfluxDB given at a private Numenta engineering meeting.

## Install InfluxDB

    > brew update
    > brew install influxdb

> 

    > influx --version
    InfluxDB shell 0.10.1

## Run InfluxDB daemon

    > influxd

     8888888           .d888 888                   8888888b.  888888b.
       888            d88P"  888                   888  "Y88b 888  "88b
       888            888    888                   888    888 888  .88P
       888   88888b.  888888 888 888  888 888  888 888    888 8888888K.
       888   888 "88b 888    888 888  888  Y8bd8P' 888    888 888  "Y88b
       888   888  888 888    888 888  888   X88K   888    888 888    888
       888   888  888 888    888 Y88b 888 .d8""8b. 888  .d88P 888   d88P
     8888888 888  888 888    888  "Y88888 888  888 8888888P"  8888888P"

    2016/02/23 09:48:12 InfluxDB starting, version 0.10.1, branch 0.10.0, commit b8bb32ecad9808ef00219e7d2469514890a0987a, built unknown

Leave this process running in your shell. Or you can start it in the background with `&`.

## Connect via CLI

    > influx
    Visit https://enterprise.influxdata.com to register for updates, InfluxDB server management, and monitoring.
    Connected to http://localhost:8086 version 0.10.1
    InfluxDB shell 0.10.1

>

    > show databases
    name: databases
    ---------------
    name
    _internal

Type `exit` or `quit` to leave the CLI.

## Collect sample data from your computer

### Install the requirements

This will install the InfluxDB python client.

    pip install -r requirements.txt

### Run the collector

Running this program will collect a bunch of metrics from your computer in real-time and feed them into InfluxDB.

    > python collect_samples.py

It will run for about 100 seconds, unless you change the defaults. You may kill it anytime without problems.

## Query InfluxDB

Connect to the CLI by typing `influx`, then query the database to see the samples you just collected.

**Select the `demo` database:**

    > use demo
    Using database demo

**Show all collected measurements:**

    > show measurements
    name: measurements
    ------------------
    name
    cpu
    disk
    memory
    network

**Show complete series information:**

    > show series
    name: cpu
    ---------
    _key				timezone	user
    cpu,timezone=PST,user=mtaylor	PST		mtaylor
    
    
    name: disk
    ----------
    _key				timezone	user
    disk,timezone=PST,user=mtaylor	PST		mtaylor
    
    
    name: memory
    ------------
    _key					timezone	user
    memory,timezone=PST,user=mtaylor	PST		mtaylor
    
    
    name: network
    -------------
    _key					timezone	user
    network,timezone=PST,user=mtaylor	PST		mtaylor

**Select data from a measurement:**

    > select * from cpu
    name: cpu
    ---------
    time		percent	timezone	user
    1456342834	11	PST		mtaylor
    1456342835	10.8	PST		mtaylor
    1456342837	8.6	PST		mtaylor
    1456342838	12.3	PST		mtaylor
    1456342839	11.3	PST		mtaylor
    1456342840	10.7	PST		mtaylor
    1456342841	10.8	PST		mtaylor
    1456342842	8.4	PST		mtaylor
    1456342843	12.3	PST		mtaylor
    1456342844	11	PST		mtaylor

**A more complex query:**

    > select percent from cpu where percent<10
    name: cpu
    ---------
    time		percent
    1456342837	8.6
    1456342842	8.4

**Aggregation function:**

    > select mean(percent) from cpu
    name: cpu
    ---------
    time	mean
    0	10.72
