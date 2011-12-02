from sinister.plotters import FunctionPlot
from sinister.names import names
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
        'toggle': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
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
            if not self.is_empty():
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

class IntervalControl(Gtk.HBox):
    def __init__(self, name, value):
        super().__init__(False, 2)
        
        adjustment = Gtk.Adjustment(value, -float_info.max, float_info.max, 0.5, 1.0, 0.0)
        self.spin = Gtk.SpinButton()
        self.spin.configure(adjustment, 0.5, 8)
        
        self.label = Gtk.Label(name)
        
        self.pack_start(self.label, True, True, 2)
        self.pack_start(self.spin, False, False, 2)
    
class ViewportControls(Gtk.Table):
    def __init__(self, viewport):
        super().__init__(2, 2, True)
        
        min_x, max_x, min_y, max_y = viewport
        
        self.viewport = viewport
        
        self.min_x_box = IntervalControl('x min', min_x)
        self.max_x_box = IntervalControl('x max', max_x)
        self.min_y_box = IntervalControl('y min', min_y)
        self.max_y_box = IntervalControl('y max', max_y)
        
        self.attach(self.min_x_box,
                    0, 1,
                    0, 1,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        self.attach(self.max_x_box,
                    1, 2,
                    0, 1,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        self.attach(self.min_y_box,
                    0, 1,
                    1, 2,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        self.attach(self.max_y_box,
                    1, 2,
                    1, 2,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    6, 4)
        
        def change_viewport(widget, control_name):
            widget.emit_stop_by_name('value-changed')
            
            value = widget.get_value()
            value_dict = {control_name: value}
            
            if control_name == 'min-x':
                if value >= self.viewport.get_property('max-x'):
                    value_dict['max-x'] = value + 0.5
                    self.max_x_box.spin.set_value(value_dict['max-x'])
            elif control_name == 'max-x':
                if value <= self.viewport.get_property('min-x'):
                    value_dict['min-x'] = value - 0.5
                    self.min_x_box.spin.set_value(value_dict['min-x'])
            elif control_name == 'min-y':
                if value >= self.viewport.get_property('max-y'):
                    value_dict['max-y'] = value + 0.5
                    self.max_y_box.spin.set_value(value_dict['max-y'])
            elif control_name == 'max-y':
                if value <= self.viewport.get_property('min-y'):
                    value_dict['min-y'] = value - 0.5
                    self.min_y_box.spin.set_value(value_dict['min-y'])
            
            self.viewport.update(value_dict)
        
        def viewport_update(controls):
            min_x_box, max_x_box, min_y_box, max_y_box = controls
            min_x, max_x, min_y, max_y = controls.viewport
            
            min_x_box.spin.handler_block_by_func(change_viewport)
            max_x_box.spin.handler_block_by_func(change_viewport)
            min_y_box.spin.handler_block_by_func(change_viewport)
            max_y_box.spin.handler_block_by_func(change_viewport)
            
            min_x_box.spin.set_value(min_x)
            max_x_box.spin.set_value(max_x)
            min_y_box.spin.set_value(min_y)
            max_y_box.spin.set_value(max_y)
            
            min_x_box.spin.handler_unblock_by_func(change_viewport)
            max_x_box.spin.handler_unblock_by_func(change_viewport)
            min_y_box.spin.handler_unblock_by_func(change_viewport)
            max_y_box.spin.handler_unblock_by_func(change_viewport)
        
        self.min_x_box.spin.connect('value-changed', change_viewport, 'min-x')
        self.max_x_box.spin.connect('value-changed', change_viewport, 'max-x')
        self.min_y_box.spin.connect('value-changed', change_viewport, 'min-y')
        self.max_y_box.spin.connect('value-changed', change_viewport, 'max-y')
        
        self.viewport.connect_object('update', viewport_update, self)
    
    def __iter__(self):
        """This is really only defined for the unpacking statement used in 
        the viewport_update callback defined in __init__. I know, it's silly"""
        return iter([self.min_x_box, self.max_x_box, self.min_y_box, self.max_y_box])

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
