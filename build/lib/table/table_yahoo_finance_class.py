import time
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, StringFormatter, NumberFormatter#, DateFormatter
from bokeh.io import hplot
from bokeh.plotting import Session, cursession, output_server, show
from Data.DataStream import  query_yahoo_finance, csvline_to_queryresult_yahoo_finance
from Data.DataHandler import yield_from_last, shift_insert


class Table_YF(object):
    
    def __init__(self, quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step = "d", row_n = 10):
        #dati per plot
        self.chrono_linegen = self.file_to_datagen(query_yahoo_finance(quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step))
        #plot
        self.plot = DataTable(
            source = ColumnDataSource(dict(
                    dates = ["-" for i in range(row_n)], 
                    close = [0 for i in range(row_n)], 
                    delta = [0 for i in range(row_n)])), #se inizializzazione in tipo non numerico non riesce a calcolare il primo delta
            columns = [TableColumn(field="dates", title="Date", formatter = StringFormatter(text_align = "center")), 
                       TableColumn(field="close", title="Close", formatter=NumberFormatter(format = "0.000")),
                       TableColumn(field="delta", title="Delta Close", formatter=NumberFormatter(format = "0.000"))],
            width=400,
            height=280,
            row_headers = False
        )
    
    #a partire dai dati della query da effettuare a YF, effettua la query e ritorna un generatore dei risultati
    def file_to_datagen(self, file):
        headerlist = file.readline().rstrip(b"\n").split(b',') #basterebbe file.readline() per buttare via la 1a linea
        antichrono_linelist = file.readlines()
        chrono_linegen = yield_from_last(antichrono_linelist)
        file.close()
        return chrono_linegen
    
    #ritorna l'oggetto DataTable, wrappato in un oggetto hplot che permette di visualizzarlo tramite server
    def get_plot(self):
        return self.plot
    
    #aggiorna le sorgenti di dati e ritorna una lista degli oggetti di cui fare push
    def update(self):
        datalist = csvline_to_queryresult_yahoo_finance(next(self.chrono_linegen), "str")
        shift_insert(self.plot.source.data["dates"], datalist[0])
        shift_insert(self.plot.source.data["close"], datalist[4])
        shift_insert(self.plot.source.data["delta"], self.plot.source.data["close"][-1] - self.plot.source.data["close"][-2])
        return [self.plot.source]