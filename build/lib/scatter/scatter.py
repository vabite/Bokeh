from bokeh.plotting import figure


class Scatter(object):
        
    def __init__(self, title, maxdata = 500):
        self.maxdata = maxdata
        self.plot = figure(
            plot_width = 800,
            plot_height = 400,
            tools = "reset",
            title = title
        )
        self.plot.circle(
            x = [],
            y = [],
            size = 6,
            color = "blue",
            alpha = 0.2,
            name = "circles"
        )
        self.ds = self.plot.select({"name":"circles"})[0].data_source
           
    def get_plot(self):
        return self.plot

    def update(self, data):
        self.ds.data["x"].append(data[0])
        if len(self.ds.data["x"]) > self.maxdata: 
            self.ds.data["x"] = self.ds.data["x"][-self.maxdata:]
        self.ds.data["y"].append(data[1])
        if len(self.ds.data["y"]) > self.maxdata: 
            self.ds.data["y"] = self.ds.data["y"][-self.maxdata:]
        return [self.ds] #wrap in lista, per poter effettuare estrazione degli oggetti aggiornati in modo generico