import redis
import zmq
import json

from bokeh.plotting import Document, Session, push, show

from histogram.histogram import Histogram
from line.line import Line
from scatter.scatter import Scatter


bokehport = "5006"
bokehurl = "http://127.0.0.1:%s/" %bokehport
s = Session(load_from_config = False, root_url = bokehurl)
#s.login("user","psw")

zmqport = "5556"
zmqurl = "tcp://localhost:%s" %zmqport
topic = b''
context = zmq.Context()
s_sub = context.socket(zmq.SUB)
s_sub.connect(zmqurl)
s_sub.setsockopt(zmq.SUBSCRIBE, topic)

redishost = 'localhost'
redisport = 6379


gtypes = {"line": lambda idkey: Line(title = idkey), 
          "histogram": lambda idkey: Histogram(title = idkey), 
          "scatter": lambda idkey: Scatter(title = idkey)}
gobjs = {} #conterrà (idkey:gobj) per ogni graph creato
gdocs = {} #conterrà (idkey:gdoc) per ogni graph creato
#conterrà idkey:gurl per ogni graph creato
gurls = redis.StrictRedis(host = redishost, port = redisport, db = 0)


while True:
    #resta in ascolto di un messaggio su zmqurl
    rawmsg = s_sub.recv_string()
    #estrae dal messaggio ricevuto name, gtype, data 
    msg = json.loads(rawmsg)
    name = msg["name"]
    gtype = msg["gtype"]
    data = msg["data"]
    #risale alla id univoca del graph
    idkey = name + " (" + gtype + ")"
    
    if idkey in gobjs: #se il graph già esiste
        #recupera graph e lo aggiorna con data
        g = gobjs[idkey]
        g.update(data)
        #aggiorna documento relativo a graph, passandone le info a bokeh-server
        s.use_doc("%s" %idkey) 
        s.store_document(gdocs["%s" %idkey])
        #salva graph aggiornato in dizionario
        gobjs[idkey] = g
        
    else:  #se il graph non esiste     
        #crea un nuovo graph
        g = gtypes[gtype](idkey)
        g.update(data)
        #crea un nuovo documento
        d = Document()
        gdocs["%s" %idkey] = d
        d.add(g.get_plot())
        #passa le info del documento a bokeh-server
        s.use_doc("%s" %idkey) 
        s.load_document(d)
        push(s, d)
        show(g.get_plot()) 
        #crea nuovi ingressi in dizionari in dizionari
        gobjs[idkey] = g
        gurls.set(idkey, s.object_link(g.get_plot()))
        
    #qui metti controllo su properties