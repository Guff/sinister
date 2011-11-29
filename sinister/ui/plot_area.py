from sinister.plotters import PlotBg
from gi.repository import Gtk

class PlotArea(Gtk.DrawingArea):
    def __init__(self, viewport, plot_bg):
        super().__init__()
        
        self.viewport = viewport
        self.plot_bg = plot_bg
        
        self.dimensions = None
        
        self.plots = {}
        
        def draw_event(widget, cr):
            widget.plot(cr)
            
            return False
        
        def configure_event(widget, event):
            if widget.dimensions == (event.width, event.height):
                return True
            
            widget.dimensions = (event.width, event.height)
            
            widget.resize_window()
            widget.refresh()
            return False
        
        def viewport_update(viewport_obj, prop):
            self.refresh()
        
        self.connect("configure-event", configure_event)
        self.connect("draw", draw_event)
        self.viewport.connect_after("notify", viewport_update)
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for entry, plot in self.plots.items():
            if entry.enabled:
                plot.plot(cr)
    
    def resize_window(self):
        self.plot_bg.resize(self.dimensions)
        self.plot_bg.draw()
        
        for entry, plot in self.plots.items():
            plot.resize(self.dimensions)
            plot.draw()
    
    def update_plot(self, entry, plot):
        if plot is None:
            if entry in self.plots:
                del self.plots[entry]
        else:
            plot.resize(self.dimensions)
            plot.draw()
            
            self.plots[entry] = plot
    
    def refresh(self):
        self.queue_draw()
