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

session = Session()

# uncomment for whathow (main counter)
url, session.headers.update = "http://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e&init=1711160585473", ({'referer': "https://whathow.neocities.org/"})
# uncomment for jared site
# url, session.headers.update = "http://www.cutercounter.com/hits.php?id=hexpacno&nd=6&style=61", ({'referer': "https://jared.nekoweb.org/"})

# ini file / Config File.
ininame = 'settings.ini'

# Default Count / This should probably be changed depending to your hardware, network capabilities. 
count = 500

# Default Debug / Usally used in Development and it will be asked to be turned on if settings.ini is not present.
debug = False

# Memory Threshold / Dont change unless you know what you are doing.
THRESHOLD = 8000 * 1024 * 1024  # 8GB / Memory of Free Space available.

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
    if mem.free <= THRESHOLD and count >= 500:
        print(f"WARNING, Memory IS TOO LOW!")
        print(f"THIS WILL RESULT IN A LOT OF LAG!!")
        x = query_yes_no("DO YOU WISH TO CONTINUE?","no")
        if x:
            None
        else:
            quit()

def debugcheck():
    global debug
    if debug:
        print(f"WARNING, DEBUG SET TO TRUE!")
        print(f"THIS WILL RESULT IN A LOT OF LOGS!!")
        x = query_yes_no("DO YOU WISH TO TURN IT OFF?","yes")
        if x:
            debug = False
        else:
            debug = True

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
                    if debug:
                        print(f"DEBUG | {response.status_code} | {response}")
                    avg_time[randint(0, 49)] = rtime
                    None
            # if failure, increment fail counter and randomly add response time
            elif (response.status_code != 200):
                with lock:
                    fails.value += 1
                    if debug:
                        print(f"DEBUG | {response.status_code} | {response}")
                    avg_time[randint(0, 49)] = rtime
                None
        # if exception, increment sysfails and print error
        except Exception as e:
            with lock:
                if debug:
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
    print("100% of processes started.")
    print("Ctrl+C to end")
    if debug == False:
        while True:
            # printing status, '\r' is to update newest line
            print((f"| {(time.time() - main_start):.2f} seconds elapsed"),
                (f"| {counter.value} succeeded"),
                (f"| {fails.value} failed"),
                (f"| {sysfails.value} errors"),
                (f"| average ping: {fmean(avg_time[:4]):.3f} |"), end='\r')

            time.sleep(0.08)
    else:
        None

# doesn't run if imported
if (__name__ == "__main__"):
    try:
        setup()
        main()
    # handles ctrl c without leaving orphans now
    except (KeyboardInterrupt, SystemExit):
        for child in children:
            child.terminate()
        print("you killed it :(")
    except Exception as e:
        print(e)
        print("it died :(")
