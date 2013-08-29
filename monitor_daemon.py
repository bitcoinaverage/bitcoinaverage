#!/usr/bin/env python

import os
import subprocess
import re
import time

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

mailApi = 'ssmtp bitcoinaverage@gmail.com < /home/backend/tools/mailApi.txt'
mailHistory = 'ssmtp bitcoinaverage@gmail.com < /home/backend/tools/mailHistory.txt'

while True:
    
    if process_exists('api_daemon.py') == False:
        
        print("api_daemon.py - Not running")
        os.system(mailApi)
    if process_exists('history_daemon.py') == False:

	print("history_daemon.py - Not Running")
	os.system(mailHistory)    
    time.sleep(120)
