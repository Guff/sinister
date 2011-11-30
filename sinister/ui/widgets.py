from sinister.plotters import FunctionPlot
from sinister.predefined_names import names
from sinister.exceptions import FunctionCreationError

from sys import float_info
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
        
        def icon_press(widget, icon, event):
            widget.toggle()
            
            return False
        
        def focus_out_event(widget, event):
            widget.emit('activate')
            
            return False
        
        def key_press_event(widget, event):
            if event.keyval == Gdk.KEY_Escape:
                widget.clear()
            
            return False
        
        self.connect('icon-press', icon_press)
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
            try:
                self.validate()
            except FunctionCreationError:
                pass
        
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

def create_interval_control(value):
    adjustment = Gtk.Adjustment(value, -float_info.max, float_info.max, 0.5, 1.0, 0.0)
    
    return Gtk.SpinButton.new(adjustment, 0.5, 8)
        
class ViewportControls(Gtk.Table):
    def __init__(self, viewport):
        super().__init__(2, 2, True)
        
        min_x, max_x = viewport.min_x, viewport.max_x
        min_y, max_y = viewport.min_y, viewport.max_y
        
        self.viewport = viewport
        
        self.min_x_spin = create_interval_control(min_x)
        self.max_x_spin = create_interval_control(max_x)
        self.min_y_spin = create_interval_control(min_y)
        self.max_y_spin = create_interval_control(max_y)
        
        self.attach(self.min_x_spin,
                    0, 1,
                    0, 1,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        self.attach(self.max_x_spin,
                    1, 2,
                    0, 1,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        self.attach(self.min_y_spin,
                    0, 1,
                    1, 2,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        self.attach(self.max_y_spin,
                    1, 2,
                    1, 2,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        def viewport_changed(widget, control_name):
            print(self.viewport.get_property(control_name))
            self.viewport.set_property(control_name, widget.get_value())
            print(self.viewport.get_property(control_name))
        
        self.min_x_spin.connect('value-changed', viewport_changed, 'min-x')
        self.max_x_spin.connect('value-changed', viewport_changed, 'max-x')
        self.min_y_spin.connect('value-changed', viewport_changed, 'min-y')
        self.max_y_spin.connect('value-changed', viewport_changed, 'max-y')

class PlotControls(Gtk.Table):
    def __init__(self, viewport):
        super().__init__(2, 1, False)
        
        self.viewport = viewport
        self.entry = FunctionEntry()
        self.viewport_controls = ViewportControls(self.viewport)
        
        self.attach(self.entry,
                    0, 1,
                    0, 1,
                    Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
                    Gtk.AttachOptions.SHRINK,
                    8, 4)
        
        self.attach(self.viewport_controls,
                    1, 2,
                    0, 1,
                    Gtk.AttachOptions.SHRINK,
                    Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL,
                    8, 4)
