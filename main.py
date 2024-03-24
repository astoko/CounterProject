# Imports
# !!! REMEMBER THAT REQUESTS NEED TO BE INSTALLED !!!

from multiprocessing import Process, Value, Array, cpu_count, Lock
from statistics import fmean, StatisticsError
from requests import Session
import os
import sys
from random import randint
import time
import configparser
import psutil

# Memory Threshold / Dont change unless you know what you are doing.
THRESHOLD = 8000 * 1024 * 1024  # 8GB / Memory

# Request URL / Already Set to the counter.
url = "https://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e&init=1711160585473" # whathow

# ini file / 
# Config file.
ininame = 'settings.ini'

# url = "https://www.cutercounter.com/hits.php?id=hexpacno&nd=6&style=61" # jared site
session = Session()
session.headers.update({'referer': "https://jared.nekoweb.org/"})

# Default Count / This should probably be changed depending to your hardware, network capabilities. 
count = 500

# Default Debug / Usally used in Development and it will be asked to be turned on 
debug = False

# Setup / Added for more automated process.
def setup():
    global count
    global debug
    print(f"Checking Settings if present...")
    file = os.path.isfile(ininame)
    if file:
        config = configparser.ConfigParser()
        config.read(ininame)
        print(f"File found, Setting Count..")
        print(" ")
        print(f"Reading GLOBAL/COUNT")
        count = int(config.get('GLOBAL','COUNT'))
        print(f"Reading GLOBAL/DEBUG")
        debug = config.get('GLOBAL','DEBUG')
        print(" ")
        print(f"COUNT: {count} has been set")
        print(f"DEBUG: {debug} has been set")
        print(" ")
        memcheck()
        debugcheck()
    else:
        config = configparser.ConfigParser()
        config['GLOBAL'] = {'COUNT': count,
                            'DEBUG': debug}
        with open(ininame, 'w') as configfile:
            config.write(configfile)
        memcheck()
        debugcheck()

def memcheck():
    global count
    global debug
    mem = psutil.virtual_memory()
    if mem.available <= THRESHOLD and count >= 500:
        print(f"WARNING, Memory IS TOO LOW!")
        print(f"THIS WILL RESULT IN A LOT OF LAG!!")
        x = query_yes_no("DO YOU WISH TO CONTINUE?","no")
        if x:
            None
        else:
            quit()

def debugcheck():
    global count
    global debug
    if debug:
        print(f"WARNING, DEBUG SET TO TRUE!")
        print(f"THIS WILL RESULT IN A LOT OF LOGS!!")
        x = query_yes_no("DO YOU WISH TO TURN IT OFF?","no")
        if x:
            debug = True
        else:
            debug = False

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

# The big guns / this does the requests, status checks and error outputs on request time.
def process(counter, fails, avg_time, child, lock, numberID):
    while True:
        try:
            start = time.time()
            response = session.head(url)
            rtime = time.time() - start
            status = response.status_code
            response.close()

            if (status == 200):
                with lock:
                    if debug:
                        print(f"{numberID} ID | 200")
                    counter.value += 1
                    avg_time[randint(0, 4)] = rtime
                    None
            elif (status != 200):
                with lock:
                    if debug:
                        print(f"{numberID} ID | {status}")
                    fails.value += 1
                    avg_time[randint(0, 4)] = rtime
                None
        except Exception as e:
            with lock:
                if debug:
                    print(e)
                None
                fails.value += 1
            None

def main():
    
    setup()

    counter = Value('L', 0)
    fails = Value('L', 0)
    avg_time = Array('f', [1, 1, 1, 1, 1])
    lock = Lock()
    children = []
    main_start = time.time()  
    
    for i in range(count):
        numberID = i
        if debug:
            print(f"{i} Process has started..")
        children.append(Process(target=process, args=(counter, fails, avg_time, url, lock, numberID)))
        children[i].start()
    
    print("Ctrl+C to end")
    while True:
        if debug:
            None
        else:
            print((f"| {(time.time() - main_start):.2f} seconds elapsed"),
                (f"| {counter.value} succeeded"),
                (f"| {fails.value} failed"),
                (f"| average ping: {fmean(avg_time[:5]):.2f} |"), end='\r')

        time.sleep(0.08)

if (__name__ == "__main__"):
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("you killed it :(")
    except Exception as e:
        if debug:
            print(e)
        None
