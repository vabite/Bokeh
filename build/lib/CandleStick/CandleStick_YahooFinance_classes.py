import calendar
import time
from bokeh.plotting import figure, show, Session, cursession, output_server
from bokeh.models import DatetimeTickFormatter
from Data.DataHandler import yield_from_last
from Data.DataStream import query_yahoo_finance, csvline_to_queryresult_yahoo_finance


class CandleStick_YF(object):
    
    def __init__(self, quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step = "d", candle_visualized_n = 15, quadwidth_percentual = 0.5):
        #inizializza dati per plot
        if step == "m": self.tmscale = 1000*60*60*24*30 #30 giorni in ms
        elif step == "w": self.tmscale = 1000*60*60*24*7 #30 giorni in ms
        else: self.tmscale = 1000*60*60*24 #1 giorno in ms
        self.quadwidth = self.tmscale * quadwidth_percentual
        self.chrono_linegen = self.file_to_datagen(query_yahoo_finance(quote_id, start_y, start_m, start_d, stop_y, stop_m, stop_d, step))
        #inizializza plot
        self.plot = figure(plot_width = 1000, plot_height = 500)
        self.plot.xaxis[0].formatter = DatetimeTickFormatter(
            formats = dict(
                hours = ["d %b %Y"], #numero giorno, sigla mese, ora come intero da 00 a 23
                days = ["%d %b %Y"], #numero giorno, sigla mese, numero anno
                months = ["%d %b %Y"], #numero giorno, sigla mese, numero anno
                years = ["%d %b %Y"]) #numero giorno, sigla mese, numero anno
            )
        self.plot.quad(top = [], bottom = [], left = [], right = [], fill_color = [], name = "quads")
        self.plot.segment(x0 = [], x1 = [], y0 = [], y1 = [], name = "segments")
        self.ds_quads = self.plot.select({"name":"quads"})[0].data_source
        self.ds_segments = self.plot.select({"name":"segments"})[0].data_source
    
    #a partire dai dati della query da effettuare a YF, effettua la query e ritorna un generatore dei risultati
    def file_to_datagen(self, file):
        headerlist = file.readline().rstrip(b"\n").split(b',')#basterebbe file.readline() per buttare via la 1a linea
        antichrono_linelist = file.readlines()
        chrono_linegen = yield_from_last(antichrono_linelist)
        file.close()
        return chrono_linegen
    
    #ritorna l'oggetto Plot
    def get_plot(self):
        return self.plot   
    
    #aggiorna le sorgenti di dati e ritorna una lista degli oggetti di cui fare push
    def update(self):
        #recupera una nuova lista di dati
        datalist = csvline_to_queryresult_yahoo_finance(next(self.chrono_linegen))##; print(datalist)
        #aggiorna dati quad
        self.ds_quads.data["top"].append(datalist[4])
        self.ds_quads.data["bottom"].append(datalist[1])
        self.ds_quads.data["left"].append(datalist[0] - self.quadwidth / 2)
        self.ds_quads.data["right"].append(datalist[0] + self.quadwidth / 2)
        if datalist[4] > datalist[1]: self.ds_quads.data["fill_color"].append("green")
        else: self.ds_quads.data["fill_color"].append("red")
        #aggiorna dati segment
        self.ds_segments.data["x0"].append(datalist[0])
        self.ds_segments.data["x1"].append(datalist[0])
        self.ds_segments.data["y0"].append(datalist[3])
        self.ds_segments.data["y1"].append(datalist[2])
        #aggiorna i dati x_range di plot
        self.plot.x_range.start = datalist[0] - (candle_visualized_n + 1) * self.tmscale
        self.plot.x_range.end = datalist[0] + self.tmscale
        #ritorna una lista degli oggetti di cui fare push: data sources dei glifi e x_range di plot
        return [self.ds_quads, self.ds_segments, self.plot.x_range] 