from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, StringFormatter, NumberFormatter#, DateFormatter
from bokeh.io import hplot

from data.datastream import split_csvline_yf
from data.datahandler import shift_insert


class TableDeltas(object):
    
    def __init__(self, row_n = 10):
        #inizializzazione plot
        self.plot = DataTable(
            source = ColumnDataSource(dict(
                    dates = ["-" for i in range(row_n)], 
                    values = [0 for i in range(row_n)], 
                    #se inizializzazione deltas in tipo non numerico non riesce a calcolare il primo delta.
                    #così il primo delta sarà pari al primo value
                    deltas = [0 for i in range(row_n)])),
            columns = [TableColumn(field="dates", title="Date", formatter=StringFormatter(text_align = "center")), 
                       TableColumn(field="values", title="Close", formatter=NumberFormatter(format = "0.000")),
                       TableColumn(field="deltas", title="Delta Close", formatter=NumberFormatter(format = "0.000"))],
            width=400,
            height=280,
            row_headers = False
        )
    
    #ritorna l'oggetto DataTable, wrappato in un oggetto hplot che permette di visualizzarlo tramite server
    def get_plot(self):
        return hplot(self.plot)
    
    #IN:lista (wrap effettuato per rendere la sintassi del metodo uguale per i vari chart) in cui ogni elemento è:
    #A) una linea del csv risultante da una query a YF, se dato valido
    #B) None, se simulato arrivo dato invalido o assenza dati
    # Nello specifico la lista contiene un solo elemento relativo alle info dell'unico titolo
    #OUT: lista dei valori presi dal metodo update per aggiornare il grafico
    #A) indice 0: data in formato stringa, indice 1: valore da utilizzare (close); se dato valido
    #B) None, se simulato arrivo dato invalido o assenza dati
    def csvlines_to_data_yf(self, csvlines):
        if csvlines[0] == None: data = [None]
        else: data = split_csvline_yf(csvlines[0], "str")[0::4] #sottolista con data formato str e close
        return data      
    
    #prende linea di un csv di yf da cui aggiorna sorgenti di dati e ritorna lista degli oggetti di cui fare push
    def update(self, data):
    #supposto che, in assenza di dati per quella data, si riceve None. In questo caso non effettua niente, aspettando
    #il dato successivo (e il prossimo delta è calcolato tra primo e ultimo dato prima che vi sia stata assenza 
    #degli stessi)
        if data != [None]:
            shift_insert(self.plot.source.data["dates"], data[0])
            shift_insert(self.plot.source.data["values"], data[1])
            shift_insert(self.plot.source.data["deltas"], 
                         self.plot.source.data["values"][-1] - self.plot.source.data["values"][-2])
        return [self.plot.source]