from sinister.plotters import PlotBg
from gi.repository import Gtk

class PlotArea(Gtk.DrawingArea):
    def __init__(self, viewport):
        super().__init__()
        
        self.viewport = viewport
        
        self.width, self.height = None, None
        
        self.plot_bg = PlotBg()
        self.plot_bg.set_viewport(self.viewport)
        
        self.plots = {}
        
        def delete_event(widget, event):
            Gtk.main_quit()
            return False
        
        def draw_event(widget, cr):
            widget.plot(cr)
            
            return False
        
        def configure_event(widget, event):
            if event.width == widget.width or event.height == widget.height:
                return True
            
            widget.width = event.width
            widget.height = event.height
            
            widget.resize_window()
            widget.refresh()
            return False
        
        self.connect("configure-event", configure_event)
        self.connect("draw", draw_event)
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for entry, plot in self.plots.items():
            if entry.enabled:
                plot.plot(cr)
    
    def resize_window(self):
        self.plot_bg.resize(self.width, self.height)
        self.plot_bg.draw()
        
        for entry, plot in self.plots.items():
            plot.resize(self.width, self.height)
            plot.draw()
    
    def update_plot(self, entry, plot):
        if plot is None:
            del self.plots[entry]
        else:
            plot.viewport = self.viewport
            
            if self.width is not None and self.height is not None:
                plot.resize(self.width, self.height)
                plot.draw()
            
            self.plots[entry] = plot
    
    def refresh(self):
        self.queue_draw()
    
    def remove_plot(self, plot):
        try:
            self.plots.remove(plot)
            self.refresh()
        except ValueError:
            pass
