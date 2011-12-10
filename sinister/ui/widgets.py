from sinister.config import conf
from sinister.ui.function_entry import FunctionEntryList

from sys import float_info
from math import floor, ceil, pi
from gi.repository import GObject, Gtk, Gdk

# using a customized HBox rather than a GtkStatusbar because that didn't seem
# to support text formatting and the stacky api was a little clunky for my needs
class PlotStatusBar(Gtk.HBox):
    def __init__(self):
        super().__init__(False, 0)
        
        self.coords_label = Gtk.Label()
        self.pack_start(self.coords_label, True, True, 0)
        self.coords_label.set_halign(Gtk.Align.END)
        self.coords_label.set_use_markup(True)
    
    def update_coords(self, x, y):
        self.coords_label.set_label('<tt>x: {: >14.8G} y: {: >14.8G}</tt>'.format(x, y))
    
    def clear_coords(self):
        self.coords_label.set_label('')

class IntervalControl(Gtk.HBox):
    def __init__(self, name, value):
        super().__init__(False, 2)
        
        adjustment = Gtk.Adjustment(value, -float_info.max, float_info.max, 0.5, 1.0, 0.0)
        self.spin = Gtk.SpinButton()
        self.spin.configure(adjustment, 0.5, 8)
        
        self.label = Gtk.Label(name)
        
        self.pack_start(self.label, True, True, 0)
        self.pack_start(self.spin, False, False, 0)
    
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
                    0, 0)
        
        self.attach(self.max_x_box,
                    1, 2,
                    0, 1,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    0, 0)
        
        self.attach(self.min_y_box,
                    0, 1,
                    1, 2,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    0, 0)
        
        self.attach(self.max_y_box,
                    1, 2,
                    1, 2,
                    Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,
                    0, 0)
        
        self.min_x_box.spin.connect('value-changed', self.change_viewport, 'min_x')
        self.max_x_box.spin.connect('value-changed', self.change_viewport, 'max_x')
        self.min_y_box.spin.connect('value-changed', self.change_viewport, 'min_y')
        self.max_y_box.spin.connect('value-changed', self.change_viewport, 'max_y')
        
        self.viewport.connect('update', self.viewport_update)
    
    def __iter__(self):
        """This is really only defined for the unpacking statement used in
        the viewport_update callback defined in __init__. I know, it's silly"""
        return iter([self.min_x_box, self.max_x_box, self.min_y_box, self.max_y_box])
    
    def viewport_update(self, viewport):
        for box, value in zip(self, viewport):
            box.spin.set_value(value)
    
    def change_viewport(self, widget, control_name):
        widget.emit_stop_by_name('value-changed')
        
        value = widget.get_value()
        value_dict = {control_name: value}
        
        if control_name == 'min_x':
            if value >= self.viewport.max_x:
                value_dict['max_x'] = value + 0.5
                self.max_x_box.spin.set_value(value_dict['max_x'])
        elif control_name == 'max_x':
            if value <= self.viewport.min_x:
                value_dict['min_x'] = value - 0.5
                self.min_x_box.spin.set_value(value_dict['min_x'])
        elif control_name == 'min_y':
            if value >= self.viewport.max_y:
                value_dict['max_y'] = value + 0.5
                self.max_y_box.spin.set_value(value_dict['max_y'])
        elif control_name == 'max_y':
            if value <= self.viewport.min_y:
                value_dict['min_y'] = value - 0.5
                self.min_y_box.spin.set_value(value_dict['min_y'])
        
        self.viewport.update(value_dict)

class PlotControls(Gtk.VBox):
    def __init__(self, viewport):
        super().__init__(False, 0)
        
        self.viewport = viewport
        self.entry_list = FunctionEntryList()
        self.viewport_controls = ViewportControls(self.viewport)
        
        self.pack_start(self.viewport_controls, False, False, 0)
        self.pack_start(self.entry_list, False, False, 0)

