import time

from bokeh.plotting import figure, show, cursession


class Scatterplot(object):
        
    #inizializza plot. Le variabili del plot non inizializzate (titolo, etc.) sono comunque accessibili dall'esterno
    def __init__(self):
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
           
    def get_plot(self):
        return self.plot

    def update(self, data):
        if data[0] != None and data[1] != None: #se entrambi i dati passati non sono invalidi (None)
            self.ds.data["x"].append(data[0]) #appende al ds di x il primo elemento della lista passata
            self.ds.data["y"].append(data[1]) #appende al ds di y il primo elemento della lista passata
        return [self.ds] #wrap in lista, per poter effettuare estrazione degli oggetti aggiornati in modo generico