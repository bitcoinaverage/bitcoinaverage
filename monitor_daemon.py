#!/usr/bin/env python

import os
import subprocess
import re
import time
import requests
import datetime
import csv
import StringIO
from email import Utils

ticker_URL = "http://api.bitcoinaverage.com/ticker/USD"
history_URL = "http://api.bitcoinaverage.com/history/USD/per_minute_24h_sliding_window.csv"

# email address to use in the to field
recipient = 'bitcoinaverage@gmail.com'

# email address to use in the from field
sender = 'bitcoinaverage@gmail.com'

# email body
message = '''To: %s
From: %s
Subject: The %s Daemon is Down!

It seems that the %s daemon may have died '''


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

def api_time_diff():
    r = requests.get(ticker_URL).json()
    current_data_datetime = r['timestamp']
    current_time = time.time()
    
    current_data_datetime = current_data_datetime[:-6] #prior to python 3.2 strptime doesnt work properly with numeric timezone offsets.
    current_data_datetime = datetime.datetime.strptime(current_data_datetime, '%a, %d %b %Y %H:%M:%S')
    current_data_timestamp = int((current_data_datetime - datetime.datetime(1970, 1, 1)).total_seconds())
    
    diff = current_time - current_data_timestamp
    return diff

def history_time_diff():

    csv_result = requests.get(history_URL).text
    csvfile = StringIO.StringIO(csv_result)
    csvreader = csv.reader(csvfile, delimiter=',')
    
    history_list = []
    
    for row in csvreader:
	history_list.append(row)
	
    last_log = history_list[-1]
    
    current_data_datetime = last_log[0]
    current_time = time.time()
    
    current_data_datetime = datetime.datetime.strptime(current_data_datetime, '%Y-%m-%d %H:%M:%S')
    current_data_timestamp = int((current_data_datetime - datetime.datetime(1970, 1, 1)).total_seconds())
    
    diff = (current_time - current_data_timestamp)
    return diff
    

def send_email(daemon):
    try:
        ssmtp = subprocess.Popen(('/usr/sbin/ssmtp', recipient), stdin=subprocess.PIPE)
    except OSError:
        print 'could not start sSMTP, email not sent'
    # pass the email contents to sSMTP over stdin
    ssmtp.communicate(message % (recipient, sender, daemon, daemon))
    # wait until the email has finished sending
    ssmtp.wait()

while True:
    
    if api_time_diff() > float(5*60):
	print "api_daemon.py - Frozen"
	send_email("API")
	
    if history_time_diff() > float(5*60):
	print "history_daemon.py - Frozen"
	send_email("History")
	

#    if process_exists('api_daemon.py') == False:
#	print("api_daemon.py - Not running")
#	#os.system(mailApi)
#	send_email("API")
#	
#    if process_exists('history_daemon.py') == False:
#	print("history_daemon.py - Not Running")
#	#os.system(mailHistory)
#	send_email("History")

    timestamp = Utils.formatdate(time.time())
    print timestamp + " - monitor_daemon.py"

    time.sleep(120)
    