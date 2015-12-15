import zmq
import sys
import numpy as np
import json
from time import sleep

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)
    
i=0
names = ["A","B","C","D"]
gtypes = ["histogram", "line","scatter"]#,"multiline"]

def new_hist_data(): 
    tot = np.random.randint(3000) + 1
    return list(np.random.randn(tot))

def new_scatter_data(xmin, xmax, ymin, ymax):
    x = np.random.uniform(xmin,xmax)
    y = np.random.uniform(ymin,ymax)
    return [x,y]

def new_line_data():
    return (np.random.uniform(0,0.1), np.random.uniform(0,100))

def new_multiline_data(n):
    return list(np.random.uniform(0,0.1,n))

def generate_data():
    name = np.random.choice(names)
    gtype = np.random.choice(gtypes)
    if gtype == "histogram":
        data = new_hist_data()
    elif gtype == "scatter":
        data = new_scatter_data(0,10,0,10)
    elif gtype == "line":
        data = new_line_data()
    elif gtype == "multiline":
        data = new_multiline_data(3)
    else:
        print("wrong graph type")
        
    return {"name": name, "gtype": gtype, "data": data, "props": {}}

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

while True:
    messagedata = json.dumps(generate_data())
    topic = "graph"
    socket.send_string(messagedata)
    sleep(0.25)