from bokeh.plotting import figure

from data.datastream import split_csvline_yf



class ScatterplotDeltasYF(object):
        
    #inizializza dplot. Le variabili del plot non inizializzate (titolo, etc.) sono comunque accessibili dall'esterno
    def __init__(self): #step tra due dati in gg
        #inizializza plot
        self.plot = figure(
            plot_width = 600,
            plot_height = 600,
        )
        self.plot.circle(
            x = [],
            y = [],
            size = 6,
            color = "navy",
            alpha = 0.5,
            name = "scatter"
        )
        self.ds = self.plot.select({"name":"scatter"})[0].data_source
        #in questa variabile viene salvato il dato utilizzato per calcolare il delta relativo al tick temporale precedente
        self.x_olddata = None 
        self.y_olddata = None
        
        
    def get_plot(self):
        return self.plot
    
    #NON AVENDO LA POSSIBILITA' DI SCEGLIERE SE LEGGERE SOLO I DATI X O Y, NON IMPLEMENTA CONTROLLO SULLA DATA DEGLI
    #INPUT, ASSUMENDO CHE ESSA SIA UGUALE (x_datalist[0] == y_datalist[0]). TALE CONTROLLO, SE NECESSARIO, VA 
    #EFFETTUATO DALLA APPLICAZIONE CHE PASSA I DATI
    def update(self, x_dataline, y_dataline):
        if x_dataline == None or y_dataline == None: #caso in cui si ha assenza di dati di almeno un titolo
        #suppone che, se per un titolo un giorno non ci sono dati, al posto della linea da esso attesa riceve None
        #Se riceve None, cancella la memoria dei dati dei titoli x e y relativi al tick temporale precedente (per 
        #calcolare un delta valido servono due dati validi consecutivi sia del titolo x che del titolo y)
            self.x_olddata = None
            self.y_olddata = None
        else: #casi in cui entrambi i dati x e y ricevuti al corrente tick temporale sono validi
        #se è la prima volta che riceve dei dati non appende alcun dato al ds del plot (non si può calcolare un delta)
        #ma semplicemente salva tali dati per calcolare il delta alla ricezione dei successivi dati (se validi)
            x_datalist = split_csvline_yf(x_dataline)
            y_datalist = split_csvline_yf(y_dataline)
            if self.x_olddata != None: #caso in cui anche i dati x e y ricevuti al tick temporale precedente sono validi
            #Appende al ds del plot un punto con ascissa pari al delta tra il valore del titolo x ricevuto a questo tick
            #temporale e al tick temporale precedente, e ordinata calcolata analogamente con i dati del titolo y
                self.ds.data["x"].append(x_datalist[4]-self.x_olddata)
                self.ds.data["y"].append(y_datalist[4]-self.y_olddata)
            #dati ricevuti memorizzati come relativi al tick temporale precedente alla prossima chiamata
            self.x_olddata = x_datalist[4] 
            self.y_olddata = y_datalist[4]
            #ritorna il ds del plot aggiornato con ascissa e ordinata del punto da plottare calcolate dai dati forniti
        return [self.ds] #wrap in lista, per poter effettuare l'estrazione degli oggetti aggiornati nel modo più generico