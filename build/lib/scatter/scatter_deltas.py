from bokeh.plotting import figure

from data.datastream import split_csvline_yf


class ScatterDeltas(object):
        
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
        
    #ritorna l'oggetto Plot    
    def get_plot(self):
        return self.plot

    #IN:lista (wrap effettuato per rendere la sintassi del metodo uguale per i vari chart) in cui ogni elemento è:
    #A) una linea del csv risultante da una query a YF, se dato valido. 
    #B) None, se simulato arrivo dato invalido o assenza dati
    #Nel caso specifico due linee:
    #indice 0: linea del csv relativa a titolo x; indice 1: linea del csv relativa a titolo y
    #OUT: lista dei valori da passare al metodo update() per aggiornare il grafico
    #A) indice 0: valore per calcolo delta titolo x, indice 1: valore per calcolo delta titolo y; se dato valido
    #B) None, se simulato arrivo dato invalido o assenza dati
    def csvlines_to_data_yf(self, csvlines):
        data = [None, None]
        for i in range(2):
            if csvlines[i] != None: data[i] = split_csvline_yf(csvlines[i], "byte")[4] #utilizza close
            else: pass
        return data
    
    #CLASSE NON SPECIFICA PER DATI YF. NON IMPLEMENTA CONTROLLO SULLA DATA DEGLI INPUT, ASSUMENDO CHE ESSA SIA UGUALE.
    #TALE CONTROLLO, SE NECESSARIO, VA EFFETTUATO DALLA APPLICAZIONE CHE PASSA I DATI
    def update(self, data):
        if data[0] == None or data[1] == None: #caso in cui si ha assenza di dati di almeno un titolo
        #suppone che, se per un titolo un giorno non ci sono dati, al posto della linea da esso attesa riceve None
        #Se riceve None, cancella la memoria dei dati dei titoli x e y relativi al tick temporale precedente (per 
        #calcolare un delta valido servono due dati validi consecutivi sia del titolo x che del titolo y)
            self.x_olddata = None
            self.y_olddata = None
        else: #casi in cui entrambi i dati x e y ricevuti al corrente tick temporale sono validi
        #se è la prima volta che riceve dei dati non appende alcun dato al ds del plot (non si può calcolare un delta)
        #ma semplicemente salva tali dati per calcolare il delta alla ricezione dei successivi dati (se validi)
            x_data = data[0]
            y_data = data[1]
            if self.x_olddata != None: #caso in cui anche i dati x e y ricevuti al tick temporale precedente sono validi
            #Appende al ds del plot un punto con ascissa pari al delta tra il valore del titolo x ricevuto a questo tick
            #temporale e al tick temporale precedente, e ordinata calcolata analogamente con i dati del titolo y
                self.ds.data["x"].append(x_data-self.x_olddata)
                self.ds.data["y"].append(y_data-self.y_olddata)
            #dati ricevuti memorizzati come relativi al tick temporale precedente alla prossima chiamata
            self.x_olddata = x_data
            self.y_olddata = y_data
            #ritorna il ds del plot aggiornato con ascissa e ordinata del punto da plottare calcolate dai dati forniti
        return [self.ds] #wrap in lista, per poter effettuare l'estrazione degli oggetti aggiornati nel modo più generico