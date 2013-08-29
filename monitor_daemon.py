#!/usr/bin/env python

import os
import subprocess
import re
import time
import requests
import datetime

URL = "http://api.bitcoinaverage.com/ticker/USD"

def process_exists(proc_name):
    ps = subprocess.Popen("ps ax -o pid= -o args= ", shell=True, stdout=subprocess.PIPE)
    ps_pid = ps.pid
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()

    for line in output.split("\n"):
        res = re.findall("(\d+) (.*)", line)
        if res:
            pid = int(res[0][0])
            if proc_name in res[0][1] and pid != os.getpid() and pid != ps_pid:
                return True
    return False

def get_time_diff():
    r = requests.get(URL).json()
    current_data_datetime = r['timestamp']
    
    current_time = time.time()
    
    current_data_datetime = current_data_datetime[:-6] #prior to python 3.2 strptime doesnt work properly with numeric timezone offsets.
    current_data_datetime = datetime.datetime.strptime(current_data_datetime, '%a, %d %b %Y %H:%M:%S')
    current_data_timestamp = int((current_data_datetime - datetime.datetime(1970, 1, 1)).total_seconds())
    
    diff = current_time - current_data_timestamp
    return diff

mailApi = 'ssmtp bitcoinaverage@gmail.com < /home/backend/tools/mailApi.txt'
mailHistory = 'ssmtp bitcoinaverage@gmail.com < /home/backend/tools/mailHistory.txt'

while True:
    
    if get_time_diff() > float(5*60):

	print "api_daemon.py - Frozen"
	os.system(mailApi)
	
    if process_exists('api_daemon.py') == False:

        print("api_daemon.py - Not running")
        os.system(mailApi)

    if process_exists('history_daemon.py') == False:

	print("history_daemon.py - Not Running")
	os.system(mailHistory)

    time.sleep(120)