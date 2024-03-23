import requests
import threading
import time

countsuc = 0
countfail = 0
s = requests.Session()

def trigger_php_code(url,threadnumberid):
    global countsuc
    global countfail
    while True:
        try:
            start_time = time.time()
            response = s.head(url)
            if response.status_code == 200:
                countsuc = countsuc + 1
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Success | SUC: {countsuc} | FAIL: {countfail} | Elapsed time: {elapsed_time:.1f}s | ID: {threadnumberid}")
                None
            else:
                countfail = countfail + 1
                print(f"Failed | SUC: {countsuc} FAIL: {countfail} ID: {threadnumberid}")
                None
        except Exception as e:
            countfail = countfail + 1
            # print(f"An error occurred for ID: {threadnumberid} {e}")
            None

url = "http://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e&init=1711160585473&init_freecounterstat=0&library=library_counters&coef=0.75&type=193&lenght=9&pv=0"

def trigger_php_code_threaded(num_threads):
    threads = []

    for i in range(num_threads):
        threadnumberid = i
        thread = threading.Thread(target=trigger_php_code, args=(url,threadnumberid))
        threads.append(thread)
        thread.start()
        print(f"ID: {threadnumberid} Started!")

    for thread in threads:
        thread.join()

num_threads = 450

try:
    while True:
        trigger_php_code_threaded(num_threads)
except KeyboardInterrupt:
    print("Execution interrupted by user.")