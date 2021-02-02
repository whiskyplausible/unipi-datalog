from bottle import route, run, template, static_file
from threading import Thread 
import time
from datetime import datetime
import requests
import json
import platform

dev = True

if platform.platform() == "Linux-5.4.83-v7+-armv7l-with-debian-10.7":
    dev = False
    print("not dev")

record = False
outfile = None
time_delay = 0

def do_record():
    global outfile, time_delay
    url = "http://localhost/"
    path = "/home/unipi/"
    if dev:
        url = "http://192.168.1.128/"
        path = ""
    #print("record thread started")
    last_record = False
    while True:
        while record:
            if not last_record:
                outfile = open(path+"capture.csv","w") 
                last_record = True
            req = requests.post(url+'json/ai/2_01', data = "{}")
            value = "-1"
            try:
                value = json.loads(req.text)["data"]["result"]["value"]
                cal = float(value) * 2.083333
                outfile.write(str(datetime.now()) + ", " + str(value) + ","+ str(cal) + "\n")
            except:
                print("some problem getting value")
            #print(value)
            if time_delay > 0:
                time.sleep(time_delay/1000.0)
        if not record and last_record:
            outfile.close()
            last_record = False
    time.sleep(1)

@route('/')
def index():
    index_page = '<a href="/start/">start capture</a> <a href="/stop/">stop capture</a> <a href="/download/">download capture</a>'
    index_page += '<br>to set delay between each record (for example to 100ms), go to http://192.xxx.xxx.xxx:8081/delay/100'
    return index_page

@route('/delay/<dly>')
def set_delay(dly):
    global time_delay
    try:
        time_delay = int(dly)
    except:
        return 'invalid delay'
    return 'delay changed <a href="/">back</a>'

@route('/start/')
def start_capture():
    global record
    record = True
    return 'starting capture <a href="/">back</a>'

@route('/stop/')
def stop_capture():
    global record
    record = False
    return 'stopping capture <a href="/">back</a>'

@route('/download/')
def download_capture():
    global record

    if record:
        return 'stop capture first'

    return static_file('capture.csv', root='')

t = Thread(target = do_record)
t.start()
if dev:
    run(host='localhost', port=8081)
else:
    run(host='0.0.0.0', port=8081)