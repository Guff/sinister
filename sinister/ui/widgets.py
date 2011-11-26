from sinister.plotters import FunctionPlot
from sinister.functions import functions

from gi.repository import Gtk as gtk

class PlotStatusBar(gtk.HBox):
    def __init__(self):
        super().__init__(False, 2)
        
        self.coords_label = gtk.Label()
        self.pack_start(self.coords_label, True, True, 2)
        self.coords_label.set_halign(gtk.Align.END)
        self.coords_label.set_use_markup(True)
    
    def update_coords(self, x, y):
        self.coords_label.set_label("<tt>x: {: >14.8G} y: {: >14.8G}</tt>".format(x, y))
    
    def clear_coords(self):
        self.coords_label.set_label("")

class FunctionEntry(gtk.HBox):
    def __init__(self, plot_area):
        super().__init__(False, 0)
        
        self.plot_area = plot_area
        
        self.active = True
        self.plot = None
        
        self.entry = gtk.Entry()
        self.pack_start(self.entry, True, True, 0)
        
        self.set_icon('gtk-yes')
        self.set_icon_tooltip('Click to toggle plotting of this function')
        self.entry.set_icon_activatable(gtk.EntryIconPosition.PRIMARY, True)
        
        self.okay = True
        
        def icon_release(widget, icon, event):
            self.toggle()
        
        def activate(widget):
            self.create_plot()
        
        def focus_out_event(widget, event):
            self.create_plot()
        
        self.entry.connect('icon-release', icon_release)
        self.entry.connect('activate', activate)
        self.entry.connect('focus-out-event', focus_out_event)
    
    def create_plot(self):
        text = self.entry.get_text()
        
        if self.plot is not None:
            self.plot_area.remove_plot(self.plot)
        
        try:
            self.plot = FunctionPlot(eval("lambda x: {}".format(text), functions))
            self.set_icon_tooltip('Click to toggle plotting of this function')
            self.plot_area.add_plot(self.plot)
        
            self.plot_area.refresh()
        except Exception as e:
            self.set_icon('error')
            self.set_icon_tooltip('error creating function: {}'.format(e))
            self.okay = False
    
    def toggle(self):
        if self.plot is not None:
            self.plot.toggle_active()
            self.plot_area.refresh()
        
        self.active = not self.active
        
        if self.active:
            self.set_icon('gtk-yes')
        else:
            self.set_icon('gtk-no')
    
    def set_icon(self, icon_name):
        self.entry.set_icon_from_icon_name(gtk.EntryIconPosition.PRIMARY, icon_name)
    
    def set_icon_tooltip(self, text):
        self.entry.set_icon_tooltip_text(gtk.EntryIconPosition.PRIMARY, text)

