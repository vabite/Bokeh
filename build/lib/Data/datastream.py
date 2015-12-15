import zmq

from calendar import timegm
import datetime
from dateutil.relativedelta import relativedelta

from urllib.request import urlopen
from urllib.parse import urlencode

from data.datahandler import yield_from_last


#crea una socket REQ legata all'indirizzo e al contesto argomento, invia il ping (byte \x01) all'indirizzo,
#attende pong su indirizzo e, quando riceve un messaggio:
#se messaggio di pong corretto (byte \x02), allora ritorna 0
#se messaggio di pong incorretto, allora ritorna -1
#Se non è fornito un contesto argomento, crea un oggetto Context di classe, e lega ad esso la socket REP
def ping(url_ping, context = None):
    
    context = context or zmq.Context.instance()
    s_pingreq = context.socket(zmq.REQ)
    s_pingreq.connect(url_ping)
    
    s_pingreq.send(b'\x01')
    if s_pingreq.recv() == b'\x02':
        s_pingreq.close()
        return 0
    else:
        s_pingreq.close()
        return -1
    
#crea una socket REP legata all'indirizzo e al contesto argomento, attende ping su url_pong e, quando riceve un messaggio:
#se messaggio di ping corretto (byte \x01), allora invia messaggio pong (byte '\x02') su indirizzo e ritorna 0
#se messaggio di ping incorretto, allora non invia messaggio di errore (b'\x03') e ritorna -1
#Se non è fornito un contesto argomento, crea un oggetto Context di classe, e lega ad esso la socket REP
def pong(url_pong, context = None):
    
    context = context or zmq.Context.instance()
    s_pongrep = context.socket(zmq.REP)
    s_pongrep.bind(url_pong)

    if s_pongrep.recv() == b'\x01':
        s_pongrep.send(b'\x02')
        s_pongrep.close()
        return 0
    else:
    #l'invio di un messaggio di errore permette al metodo ping() eventualmente in sospeso di chiudersi con errore
        s_pongrep.send(b'\x03') 
        s_pongrep.close()
        return -1

#Effettua una query al sito di Yahoo Finance ritornando un oggetto FancyURLOpener associato ad un file csv contenente i
#valori del titolo con id argomento all'interno dell'intervallo temporale argomento, con uno step temporale tra dati 
#successivi argomento (opzionale; se omesso presi dati giornalmente)
#base_url è la url di base cui effettuare query a Yahoo per csv dati finanziari
#query_param sono i parametri stringa di query a Yahoo relativa ai dati contenuti nel csv ritornato
#s: sigla rappresentante il titolo richiesto
#a, b, c: mese - 1, giorno, anno di inizio dati
#d, e, f: mese - 1, giorno, anno di fine dati
#g: distanza temporale tra due dati successivi ("d", "w", "y")
def queryinput_to_csv_yf(quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step = "d" ):
    
    base_url = "http://ichart.yahoo.com/table.csv" 
    query_string = urlencode({
            "s" : quote_id,
            "a" : start_m - 1,
            "b" : start_d,
            "c" : start_y,
            "d" : stop_m - 1,
            "e" : stop_d,
            "f" : stop_y,
            "g": step,
        })

    return urlopen(base_url + "?" + query_string)

#a partire dai dati argomento della query da effettuare a YF, effettua la query e ritorna un generatore dei risultati il quale
#ad ogni chiamata di next(), ritorna il successivo dato in ordine cronologico contenuto nel csv (NB: il generatore non effettua
#alcun controllo sulla data dei dati ritornati, se qualche data manca perchè non presente nel csv, lui non ne sa nulla)
def queryinput_to_gen_yf(quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step = "d", headers = False):
    FancyURLOpener_obj = queryinput_to_csv_yf(quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step)
    headersline = FancyURLOpener_obj.readline() #basterebbe file.readline() per buttare via la 1a linea
    antichrono_linelist = FancyURLOpener_obj.readlines()
    if headers: antichrono_linelist.append(headersline)
    chrono_linegen = yield_from_last(antichrono_linelist)
    FancyURLOpener_obj.close()
    return chrono_linegen

#a partire da una sequenza di quote_ids, da una data di partenza, da una data di termine, da uno step temporale e da un flag headers
#effettua una query a Yahoo Finance ottenendo i csv dei dati storici relativi al valore dei titoli nella sequenza quote_ids, 
#all'interno dell'intervallo temporale specificato e con lo step temporale specificato e ritorna un generatore. Alla chiamata del 
#metodo next(), tale generatore ritorna una lista di dati associati ad una particolare data (a partire da quella iniziale della 
#query, con step temporale argomento. Ciascun dato della lista è:
#A) la linea del csv relativo alla quote_id con la stessa posizione nella lista quote_ids passata, se nel relativo csv vi è una linea 
#associata all'attuale data cui il generatore è arrivato
#B) None, se nel relativo csv non vi è una linea associata all'attuale data cui il generatore è arrivato
#Il generatore ritornato alza l'eccezione StopIteration quando i dati di almeno una delle quote_id sono terminati
def queriesinput_to_syncgens_yf(quote_ids, start_y, start_m, start_d, stop_y, stop_m, stop_d, step = "d", headers = False):  
    
#nel caso lo step della query sia 1mese, pone come data iniziale della query il primo giorno dell'anno e mese passati per la query
    if step == "m": 
        current_date = datetime.date(start_y, start_m, 1)
        timestep = relativedelta(months = 1)
#nel caso lo step della query sia 1week, pone come data iniziale della query il lunedì della settimana della data passata per la query
    elif step == "w":
        current_date = datetime.date(start_y, start_m, start_d)
        current_date -= datetime.timedelta(days = current_date.weekday())
        timestep = datetime.timedelta(weeks = 1)
#nel caso lo step della query sia 1day (sia esplicita, che passata, che pasata ma diversa dai valori possibili: "m", "w", "d"), pone 
#come data iniziale della query il lunedì della settimana della data passata come argomento
    else:
        current_date = datetime.date(start_y, start_m, start_d)
        timestep = datetime.timedelta(days = 1)

    #ottiene una lista in cui ciascun elemento è il generatore dei dati in ordine cronologico relativi a un titolo passato (query_id)
    genslist = [queryinput_to_gen_yf(quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step, headers) 
                for quote_id in quote_ids]
    #ogni elemento di tale lista dice se i dati della quote_id con la stessa posizione sono sincronizzati con la data corrente alla
    #quale si ritoneranno i dati a questa chiamata di next() sul generatore ritornato da queriesinput_to_syncgens_yf() o no.
    currentinputlines_list = [None for i in range(len(quote_ids))]
    currentinputsync_list = [True for gen in genslist] ##;print(current_date, genslist, currentinputsync_list, currentinputlines_list)
    if headers == True:
        #se sono stati richiesti gli headers, alla prima chiamata di next() ritorna una lista contenente le prima linea contenente 
        #il primo dato di ogni generatore (a sua volta ottenuto mantenendo l'header nelle query effettuate)
        yield [next(gen) for gen in genslist] 
    
    #una volta entrato nel loop relativo a uno step temporale ci rimane. Se si ha intenzione di dare la possibilità di 
    #cambiare lo step temporale di query, è possibile porre un unico while fuori dagli if (anche se così effettua i 
    #controlli della condizione più esterna ad ogni iterazione)
    while True:
    #effettua una iterazione ad ogni chiamata di next(). Alla prima interazione, mette in currentinputlines_list degli input delle 
    #singole quotes la prima linea ritornata da ogni relativo generatore. Alle iterazioni successive, mantiene currentinputlines_list
    #le linee delle quote_id che al passo precedente non erano sincronizzate con la data ritornata (linee dati contenenti data 
    #successiva a quella ritornata), mentre mette in currentinputlines_list il dato ritornato dal rispettivo generatore delle 
    #quote_id che al passo precedente erano sincronizzate con la data ritornata
        try: 
            for i in range(len(genslist)):
                if currentinputsync_list[i]: 
                    currentinputlines_list[i] = next(genslist[i])
            currentinputsync_list = [] ##;print(currentinputlines_list)
        except(StopIteration): 
            break #si ferma non appena terminano i dati di un csv. Potrebbe essere migliorato dicendo di andare avanti con gli altri
        
        currentoutputlines_list = [] #questa lista è quella che vrrà ritornata quando verrà chiamato il metodo next()
        #per ciascuna quote_id, se la data della linea corrente relativa a quella quote_id è sincronizzata con la data ritornata
        #allora a questa chiamata di next() per tale quote_id verrà ritornata la linea relativa alla quote_id stessa e settato
        #il relativo flag di sincronizzazione in urrentinputsync_list a True; viceversa a questa chiamata di next() per tale quote_id 
        #verrà ritornato None e settato il relativo flag di sincronizzazione in urrentinputsync_list a False
        for currentinputline in currentinputlines_list:
            currentinputline_date = datetime.date(*split_csvline_yf(currentinputline, "list")[0])
            ##print(currentinputline_date, current_date)
            if current_date <= currentinputline_date < current_date + timestep:
                currentinputsync_list.append(True)
                currentoutputlines_list.append(currentinputline)
            else:
                currentinputsync_list.append(False)
                currentoutputlines_list.append(None)
        #aggiorna la data relativa ai dati ritornati, aggiungendo il timestep argomento a quella della chiamata precedente
        current_date += timestep 
        yield currentoutputlines_list #ritorna lista delle linee relative ai dati delle quote_id sincronizzati con la data ritornata
        
#prende un bytearray formattato come una linea del csv risultato delle query effettuate a Yahoo Finance
#ritorna una lista i cui valori sono:
#indice 0: tempo formattato in base al parametro tm_format argomento ("byte" per bytearray, "str" per stringa, "list" per lista [anno, mese, giorno], "int" per intero rappresentante la data in ms a partire da 'epoch')
#indice 1: open
#indice 2: highest
#indice 3: lowest
#indice 4: close
#indice 5: volume
#indice 6: adj_close
def split_csvline_yf(line, tm_format = "int"):
    
    line_split = line.split(b',')
    
    if tm_format == "byte":
        tm = line_split[0]
    elif tm_format == "str":
        tm = line_split[0].decode()
    elif tm_format == "list":
        tm = line_split[0].split(b'-')
        tm = [int(tm[0]), int(tm[1]), int(tm[2])]
    elif tm_format == "int":
        tm = line_split[0].split(b'-')
        tm = 1000 * timegm((int(tm[0]), int(tm[1]), int(tm[2]), 0, 0, 0, 0, 0, -1))
    else:
        tm = -1
    
    open_ = float(line_split[1])
    highest = float(line_split[2])
    lowest = float(line_split[3])
    close = float(line_split[4])
    volume = float(line_split[5])
    adj_close = float(line_split[6].rstrip(b"\n"))
       
    return [tm, open_, highest, lowest, close, volume, adj_close]

