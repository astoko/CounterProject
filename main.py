from multiprocessing import Process, Value, Array, cpu_count, Lock
from statistics import fmean, StatisticsError
from requests import Session
from random import randint
import time

# url = "http://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e&init=1711160585473"
url = "http://counter11.optistats.ovh/private/freecounterstat.php?c=pec7c8rlblcyry81uy93wbyaqpp2jjbn"
session = Session()

def process(counter, fails, avg_time, child, lock):
    while True:
        try:
            start = time.time()
            response = session.head(url)
            rtime = time.time() - start
            if (response.status_code == 200):
                with lock:
                    counter.value += 1
                    avg_time[randint(0, 4)] = rtime
                    None
            elif (response.status_code != 200):
                with lock:
                    fails.value += 1
                    avg_time[randint(0, 4)] = rtime
                None
        except Exception as e:
            with lock:
                print(e)
                fails.value += 1
            None

def main():
    counter = Value('L', 0)
    fails = Value('L', 0)
    avg_time = Array('f', [1, 1, 1, 1, 1])
    lock = Lock()
    children = []
    main_start = time.time()  
    
    for i in range(3000):
        children.append(Process(target=process, args=(counter, fails, avg_time, url, lock)))
        children[i].start()
    
    print("Ctrl+C to end")
    while True:
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
        print(e)
