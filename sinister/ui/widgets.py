from sinister.plotters import FunctionPlot
from sinister.predefined_names import names
from sinister.exceptions import FunctionCreationError

from gi.repository import GObject, Gtk, Gdk

class PlotStatusBar(Gtk.HBox):
    def __init__(self):
        super().__init__(False, 2)
        
        self.coords_label = Gtk.Label()
        self.pack_start(self.coords_label, True, True, 2)
        self.coords_label.set_halign(Gtk.Align.END)
        self.coords_label.set_use_markup(True)
    
    def update_coords(self, x, y):
        self.coords_label.set_label('<tt>x: {: >14.8G} y: {: >14.8G}</tt>'.format(x, y))
    
    def clear_coords(self):
        self.coords_label.set_label('')

class FunctionEntry(Gtk.Entry):
    __gsignals__ = {
        'toggle': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    
    def __init__(self):
        super().__init__()
                
        self.valid = True
        self.enabled = True
        self.error = None
        self.function = None
        
        self.icon_pos = Gtk.EntryIconPosition.PRIMARY
        
        self.valid_tooltip = 'Click to disable plotting of this function'
        self.invalid_tooltip = 'error creating function: {}'
        self.disabled_tooltip = 'Click to enable plotting of this function'
        
        self.update_icon_and_tooltip()
        self.set_icon_activatable(Gtk.EntryIconPosition.PRIMARY, True)
        
        def icon_release(widget, icon, event):
            widget.toggle()
            
            return False
        
        def focus_out_event(widget, event):
            widget.emit('activate')
            
            return False
        
        def key_press_event(widget, event):
            if event.keyval == Gdk.KEY_Escape:
                widget.clear()
            
            return False
        
        self.connect('icon-release', icon_release)
        self.connect('focus-out-event', focus_out_event)
        self.connect('key-press-event', key_press_event)
    
    def is_empty(self):
        return (len(self.get_text()) == 0)
    
    def validate(self):
        text = self.get_text()
        
        try:
            self.function = eval('lambda x: {}'.format(text), names)
            self.valid = True
        except Exception as e:
            self.function = None
            self.valid = False
            self.error = e
            raise FunctionCreationError(e)
    
    def toggle(self):
        self.enabled = not self.enabled
        
        if self.enabled:
            self.validate()
        
        self.update_icon_and_tooltip()
        
        self.emit('toggle')
    
    def clear(self):
        self.set_text('')
        self.function = None
        self.valid = True
        self.update_icon_and_tooltip()
        self.emit('activate')
    
    def update_icon_and_tooltip(self):
        if self.enabled:
            if self.valid:
                self.set_icon_from_icon_name(self.icon_pos, 'gtk-yes')
                self.set_icon_tooltip_text(self.icon_pos, self.valid_tooltip)
            else:
                self.set_icon_from_icon_name(self.icon_pos, 'error')
                self.set_icon_tooltip_text(self.icon_pos, self.invalid_tooltip.format(self.error))
        else:
            self.set_icon_from_icon_name(self.icon_pos, 'gtk-no')
            self.set_icon_tooltip_text(self.icon_pos, self.disabled_tooltip)
    
    def create_plot(self, viewport):
        return FunctionPlot(viewport, self.function)
