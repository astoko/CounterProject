from multiprocessing import Process, Value, Array, cpu_count, Lock
from statistics import fmean, StatisticsError
from configparser import ConfigParser
from psutil import virtual_memory
from colorama import Fore, Style
from requests import Session
from random import randint
from os.path import isfile
import configparser
import time

# ini / config file + requests session
settings_file = 'settings.ini'
session = Session()

# Handles config file and setup of variables
def setup():
    global count
    global url
    config = ConfigParser()

    if isfile(settings_file):
        config.read(settings_file)

        try:
            print("Reading COUNT")
            count = int(config.get('GLOBAL','COUNT'))
        except ValueError:
            raise ResourceWarning(f"{Fore.RED}Error: Invalid count set. Set a valid count in {Fore.BLUE}settings.ini{Fore.RED}.\nCount must be an {Fore.GREEN}integer{Style.RESET_ALL}.")
        try:
            print("Reading MODE")
            mode = int(config.get('GLOBAL', 'MODE'))
        except ValueError:
            raise ResourceWarning(f"{Fore.RED}Error: Invalid mode set. Set a valid mode in {Fore.BLUE}settings.ini{Fore.RED}.\nMode must be an {Fore.GREEN}integer{Style.RESET_ALL}.")

        print(f"Count has been set to {count}.")
 
        memcheck()

    else:
        # Creates config if it does not exist
        print("Config file not found, creating")
        
        # Sets defaults
        config['GLOBAL'] = {'COUNT': 500,
                            'MODE': 0}

        # Writes to file
        with open(settings_file, 'w') as configfile:
            config.write(configfile)

        # Sets variables in program
        count = 500
        mode = 0

        memcheck()

    # check validity of mode + modify vars according to mode
    match mode:
        case 0:
            mode = "WhatHow"

            url, session.headers.update = "http://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e", ({'referer': "https://whathow.neocities.org/"})
        case 1:
            mode = "Jared"
            raise ResourceWarning(f"this mode,,, uhh,,, {Fore.RED}doesn't work{Style.RESET_ALL},,, 3:")

            url, session.headers.update = "http://www.cutercounter.com/hits.php?id=hexpacno&nd=6&style=61", ({'referer': "https://jared.nekoweb.org/", 'sec-fetch-site': "cross-site"})
        case _:
            raise ResourceWarning(f"{Fore.RED}Error: Invalid mode set. Set a valid mode in {Fore.BLUE}settings.ini{Fore.RED}.\nList of valid modes can be found in {Fore.GREEN}README.md{Fore.RED}.{Style.RESET_ALL}")
    
    print(f"Mode set to {Fore.CYAN}{mode}{Style.RESET_ALL}.")
            

def memcheck():
    memory = virtual_memory().available
    # Average usage per process is ~8.3MB, subtracts 1GB from available ram to avoid swapping too much
    max_count = (memory - (10 ** 9)) / 8300000
    if (max_count < count):
        # throws error
        raise ResourceWarning(f"{Fore.RED}Warning: Memory too low for selected count. Set a lower count in {Fore.BLUE}settings.ini{Fore.RED}.\nWe recommend a count below {Fore.GREEN}{(max_count - 10):.0f}{Fore.RED} given the amount of available memory in your system.{Style.RESET_ALL}")

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
        except KeyboardInterrupt:
            pass
            None
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
    global children
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
              (f"| {Fore.GREEN}{counter.value} succeeded{Style.RESET_ALL}"),
              (f"| {Fore.MAGENTA}{fails.value} failed{Style.RESET_ALL}"),
              (f"| {Fore.RED}{sysfails.value} errors{Style.RESET_ALL}"),
              (f"| average ping: {fmean(avg_time[:4]):.3f}"),
              (f"| {Fore.GREEN}~{(counter.value / (time.time() - main_start) * 60):.1f} hits per minute{Style.RESET_ALL}"),
              (f"|"), end='\r')

        time.sleep(0.08)

if (__name__ == "__main__"):
    try:
        setup()
        main()
    except (KeyboardInterrupt, SystemExit):
        # killing children
        for child in children:
            child.terminate()
        print(f"\n{Fore.MAGENTA}you killed it :({Style.RESET_ALL}")
        exit()
    except ResourceWarning as e:
        print(e)
        None
    except Exception as e:
        print(e)
        print(f"\n{Fore.RED}it died :({Style.RESET_ALL}")
        None
