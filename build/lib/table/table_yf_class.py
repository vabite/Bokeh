from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, StringFormatter, NumberFormatter#, DateFormatter
from bokeh.io import hplot

from data.datastream import split_csvline_yf
from data.datahandler import shift_insert


class TableYF(object):
    
    def __init__(self, row_n = 10):
        #inizializzazione plot
        self.plot = DataTable(
            source = ColumnDataSource(dict( #inizializzazione dei dati contenuti nelle celle delle colonne
            #NB: il tipo utilizzato per la inizializzazione conta, siccome per la formattazione delle celle sono usati obj Formatter 
            #Inoltre, per la colonna contenente delta valori, se inizializzata con tipo non numerico non riesce a calcolare il 1o delta
                    dates = ["-" for i in range(row_n)], #colonna contenente date inizializzata con stringa "-"
                    close = [0 for i in range(row_n)], #colonna conenente valori inizializzata con int 0
                    delta = [0 for i in range(row_n)])), #colonna conenente i delta dei valori inizializzata con int 0
            columns = [TableColumn(field="dates", title="Date", formatter = StringFormatter(text_align = "center")), 
                       TableColumn(field="close", title="Close", formatter = NumberFormatter(format = "0.000")),
                       TableColumn(field="delta", title="Delta Close", formatter = NumberFormatter(format = "0.000"))],
            width = 400,
            height = 280,
            row_headers = False #di default, non visualizza la colonna contenente il numero della riga
        )
  
    #ritorna l'oggetto DataTable, wrappato in un oggetto hplot che permette di visualizzarlo tramite server
    def get_plot(self):
        return hplot(self.plot)
    
    #a partire da una linea di un csv di yf aggiorna le sorgenti di dati e ritorna una lista degli oggetti di cui fare push
    def update(self, dataline):
    #supposto che, in caso di arrivo dati non validi o assenza dati, si riceve None
        if dataline != None: #in caso di arrivo dati validi
            datalist = split_csvline_yf(dataline, "str")
            shift_insert(self.plot.source.data["dates"], datalist[0])
            shift_insert(self.plot.source.data["close"], datalist[4])
            shift_insert(self.plot.source.data["delta"], self.plot.source.data["close"][-1] - self.plot.source.data["close"][-2])
        else: #in caso di assenza dati o arrivo dati non validi
            pass #non aggiunge alcun dato alla tabella, aspettando il dato successivo. Il prossimo delta è calcolato tra il primo e
        #non aggiunge alcun dato alla tabella, aspettando il dato successivo. Il prossimo delta è calcolato tra il primo e
        #l'ultimo dato prima che vi sia stata assenza degli stessi
        return [self.plot.source] #ritorna il data source delle colonne, wrappato in lista per poterlo estrarre nel modo più generale