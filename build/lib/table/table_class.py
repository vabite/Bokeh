from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, StringFormatter, NumberFormatter#, DateFormatter
from bokeh.io import hplot

from data.datastream import split_csvline_yf
from data.datahandler import shift_insert


class Table(object):
    
    def __init__(self, row_n = 10):
        self.plot = DataTable(
            source = ColumnDataSource(dict(
                    dates = ["-" for i in range(row_n)], 
                    values = [0 for i in range(row_n)], 
                    deltas = [0 for i in range(row_n)])),
            columns = [TableColumn(field="dates", title="Date", formatter=StringFormatter(text_align = "center")), 
                       TableColumn(field="values", title="Close", formatter=NumberFormatter(format = "0.000")),
                       TableColumn(field="deltas", title="Delta Close", formatter=NumberFormatter(format = "0.000"))],
            width=400,
            height=280,
            row_headers = False
        )
    
    def get_plot(self):
        return hplot(self.plot)
    
    def csvlines_to_datalist_yf(self, csvlineslist):
        if csvlineslist[0] == None: datalist = [None]
        else: datalist = split_csvline_yf(csvlineslist[0], "str")[0::4]
        return datalist       

    def update(self, datalist):
        if datalist != [None]:
            shift_insert(self.plot.source.data["dates"], datalist[0])
            shift_insert(self.plot.source.data["values"], datalist[1])
            shift_insert(self.plot.source.data["deltas"], 
                         self.plot.source.data["values"][-1] - self.plot.source.data["values"][-2])
        return [self.plot.source]