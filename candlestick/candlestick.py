import time

from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter

from data.datastream import split_csvline_yf


class Candlestick(object):
    
    #le variabili del plot non inizializzate (titolo, etc.) sono comunque accassibili dall'esterno
    def __init__(self, candle_visualized_n = 15, quadwidth_percentual = 0.5, tmstep = 1): #step tra due dati in gg
        #inizializza dati per plot
        #tmstep rappresenta la distanza temporale attesa tra due dati.
        #Con tale passo temporale è shiftato l'asse x in caso assenza dati (modellato con arrivo None), definita
        #l'ampiezza dell'asse x mostrata, e scalata l'ampiezza x dei glifi. E' convertita in in ms, udm usata da Bokeh
        #Possibile anche ricavarlo dinamicamente da dati ricevuti se si suppone intervallo tra due dati possa variare
        self.tmstep = tmstep * 24 * 60 * 60 * 1000
        #quadwidth ampiezza dei rettangoli reale. quadwidth_percentual ampiezza dei retangoli relativa al tmstep
        self.quadwidth = quadwidth_percentual * self.tmstep 
        self.candle_visualized_n = candle_visualized_n #numero di candele da visualizzare sul grafico
        #inizializza plot
        self.plot = figure(plot_width = 900, plot_height = 300)
        self.plot.xaxis[0].formatter = DatetimeTickFormatter(
            formats = dict(
                hours = ["d %b %Y"], #numero giorno, sigla mese, ora come intero da 00 a 23
                days = ["%d %b %Y"], #numero giorno, sigla mese, numero anno
                months = ["%d %b %Y"], #numero giorno, sigla mese, numero anno
                years = ["%d %b %Y"]) #numero giorno, sigla mese, numero anno
            )
        #grafico inizializzato vuoto inizializzando tutti i data source come liste vuote
        self.plot.quad(top = [], bottom = [], left = [], right = [], fill_color = [], name = "quads") 
        self.plot.segment(x0 = [], x1 = [], y0 = [], y1 = [], name = "segments")
        #estremi dell'instervallo in x mostrato inizializzati dal costruttore in quanto, se il primo dato è None, 
        #in update non riesce ad inizializzarli dovendo sommare un intero ad un None. Di default inizializzati 
        #all'istante attuale (se si fosse inizializzato a 0 sarebbero stati inizializzati alla epoch; tuttavia ho 
        #dal test pare non cambi molto, non visualizzando lui il range degli assi fino a che non visualizza un glifo)
        self.plot.x_range.start = time.time() * 1000 
        self.plot.x_range.end = time.time() * 1000
        self.ds_quads = self.plot.select({"name":"quads"})[0].data_source
        self.ds_segments = self.plot.select({"name":"segments"})[0].data_source

    #ritorna l'oggetto Plot
    def get_plot(self):
        return self.plot        

    #IN:lista (wrap effettuato per rendere la sintassi del metodo uguale per i vari chart) in cui ogni elemento è:
    #A) una linea del csv risultante da una query a YF, se dato valido
    #B) None, se simulato arrivo dato invalido o assenza dati
    #Nel caso specifico la lista contiene un solo elemento relativo all'unico titolo della query
    #OUT: lista dei valori da passare al metodo update() per aggiornare il grafico
    #A) [data in millisecondi a partire da epoch, apertura, massimo, minimo, chiusura]; se dato valido
    #B) None, se simulato arrivo dato invalido o assenza dati
    def csvlines_to_data_yf(self, csvlines):
        if csvlines[0] == None: data = [None]
        else: data = split_csvline_yf(csvlines[0], "int")[0:5]
        return data
    
    #aggiorna i ds e ritorna una lista degli oggetti di cui fare push a partire da una linea csv formattata come da YF
    def update(self, data):
        #recupera una nuova lista di dati che suppone strutturata come segue:
        #indice 0: data in millisecondi a partire da epoch
        #indice 1: apertura
        #indice 2: massimo
        #indice 3: minimo
        #indice 4: chiusura
        #L'arrivo di dati non validi o l'assenza di dati è simulata come arrivo di None
        if data != [None]: #caso arrivo valido
            #aggiorna dati quad
            self.ds_quads.data["top"].append(data[4])
            self.ds_quads.data["bottom"].append(data[1])
            self.ds_quads.data["left"].append(data[0] - self.quadwidth / 2)
            self.ds_quads.data["right"].append(data[0] + self.quadwidth / 2)
            if data[4] > data[1]: self.ds_quads.data["fill_color"].append("green")
            else: self.ds_quads.data["fill_color"].append("red")
            #aggiorna dati segment
            self.ds_segments.data["x0"].append(data[0])
            self.ds_segments.data["x1"].append(data[0])
            self.ds_segments.data["y0"].append(data[3])
            self.ds_segments.data["y1"].append(data[2])
            #aggiorna i dati x_range di plot
            #in caso di arrivo dato valido, definisce un intervallo di visualizzazione ponendo la candela del dato in
            #arrivo a mezzo tmstep dal bordo dx del grafico e a candle_visualized_n + 0.5 tmstep dal bordo sx
            self.plot.x_range.start = data[0] - (self.candle_visualized_n - 0.5) * self.tmstep
            self.plot.x_range.end = data[0] + 0.5 * self.tmstep
        else: #caso ricezione dato non valido
            #shifta di un tmstep a sx l'intervallo di visualizzazione nell'asse x e non aggiunge candele al grafico
            #NB: mentre in caso arrivo dati validi stabilisce il range di visualizzazione in base all'ascissa del dato
            #arrivato, qui effettua lo shift con tmstep.Se tmstep non è preso esattamente pari alla distanza temporale
            #tra l'arrivo di due dati:
            #arrivo dati validi: mostra un intervallo in x non esattamente uguale a quello desiderato
            #arrivo dati non validi o asenza dati: qui accumula ritardo o anticipo rispetto ai dati attuali
            self.plot.x_range.start += self.tmstep 
            self.plot.x_range.end += self.tmstep
        #ritorna una lista degli oggetti di cui fare push: data sources dei glifi e x_range di plot
        return [self.ds_quads, self.ds_segments, self.plot.x_range]