from multiprocessing import Process, Value, Array, cpu_count, Lock
from statistics import fmean, StatisticsError
from configparser import ConfigParser
from psutil import virtual_memory
from requests import Session
from random import randint
from os.path import isfile
import configparser
import time
import sys
import os

# ini / config file.
settings_file = 'settings.ini'

session = Session()

# keep the url config in main.py so referrer and counter can be defined together

# uncomment for whathow (main counter)
url, session.headers.update = "http://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e", ({'referer': "https://whathow.neocities.org/"})

# uncomment for jared site
# url, session.headers.update = "http://www.cutercounter.com/hits.php?id=hexpacno&nd=6&style=61", ({'referer': "https://jared.nekoweb.org/"})

# Setup / Added for more automated process.
def setup():
    global debug
    global count
    config = ConfigParser()
    
    if isfile(settings_file):
        config.read(settings_file)

        print(f"Reading GLOBAL/COUNT")
        print(f"Reading GLOBAL/DEBUG")

        count = int(config.get('GLOBAL','COUNT'))
        debug = config.get('GLOBAL','DEBUG')

        print(f"Count has been set to {count}.")
        print(f"Debug has been set to {debug}.")
 
        memcheck()
    else:
        # Creates config if it does not exist
        print("Config file not found, creating")
        
        # Sets defaults
        config['GLOBAL'] = {'COUNT': 500,
                            'DEBUG': False}

        # Writes to file
        with open(settings_file, 'w') as configfile:
            config.write(configfile)

        # Sets variables in program
        count = 500
        debug = False

        memcheck()

def memcheck():
    mem = virtual_memory()
    # Average usage per process is ~8.55MB, subtracts 1GB from available ram to avoid swapping too much
    if (((mem.available - (10 ** 9)) / 8555000) < count):
        print("Warning: Memory too low")
        print("Set a lower count")
        exit("")

def process(counter, fails, sysfails, avg_time, child, lock):
    while True:
        try:
            # gets response time and status code, then closes request
            start = time.time()
            response = session.head(url)
            rtime = time.time() - start
            status=response.status_code
            response.close()

            # if successful, increment success counter and randomly add response time to average array
            if (response.status_code == 200):
                with lock:
                    counter.value += 1
                    avg_time[randint(0, 49)] = rtime
                    None
            # if failure, increment fail counter and randomly add response time
            elif (response.status_code != 200):
                with lock:
                    fails.value += 1
                    avg_time[randint(0, 49)] = rtime
                None
        # if exception, increment sysfails and print error
        except Exception as e:
            with lock:
                print(e)
                sysfails.value += 1
            None

def main():
    # initialize multiprocessing variables
    counter = Value('L', 0)
    fails = Value('L', 0)
    sysfails = Value('L', 0)
    avg_time = Array('f', [1] * 50)
    lock = Lock()
    # array of processes
    children = []
    # elapsed time timer
    main_start = time.time()  

    # create [count] processes
    for i in range(count):
        children.append(Process(target=process, args=(counter, fails, sysfails, avg_time, url, lock)))
        children[i].start()
        print((f"{(i / (count - 1) * 100):.2f}% of processes started."), end='\r')
    
    # workaround so the previous printing doesn't get overwritten 
    print("100.00% of processes started.")
    print("Ctrl+C to end")
    while True:
        # printing status, '\r' is to update newest line
        print((f"| {(time.time() - main_start):.2f} seconds elapsed"),
              (f"| {counter.value} succeeded"),
              (f"| {fails.value} failed"),
              (f"| {sysfails.value} errors"),
              (f"| average ping: {fmean(avg_time[:4]):.3f} |"), end='\r')

        time.sleep(0.08)

if (__name__ == "__main__"):
    try:
        setup()
        main()
    except (KeyboardInterrupt, SystemExit):
        # killing children
        for child in children:
            child.terminate()
        print("you killed it :(")
    except Exception as e:
        # if someone has an issue and debug isn't on it's helpful to know that it crashed
        print(e)
        print("it died :(")
        None
