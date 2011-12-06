from sinister.config import conf
if conf.general.use_cython:
    from sinister.cplotters import FunctionPlot
else:
    from sinister.plotters import FunctionPlot

from sinister.names import names
from sinister.exceptions import FunctionCreationError
from sinister.parse import parse_function

from sys import float_info
from gi.repository import GObject, Gtk, Gdk

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

class FunctionEntry(Gtk.Entry):
    __gsignals__ = {
        'toggle': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'remove-button-press': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
    }
    
    def __init__(self):
        super().__init__()
                
        self.valid = True
        self.enabled = True
        self.error = None
        self.function = None
        
        self.valid_tooltip = 'Click to disable plotting of this function'
        self.invalid_tooltip = 'error creating function: {}'
        self.disabled_tooltip = 'Click to enable plotting of this function'
        
        self.update_status_icon_and_tooltip()
        self.set_icon_activatable(Gtk.EntryIconPosition.PRIMARY, True)
        
        self.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
        
        self.connect('icon-press', FunctionEntry.on_status_icon_press)
        self.connect('icon-press', FunctionEntry.on_remove_icon_press)
        self.connect('focus-out-event', FunctionEntry.on_focus_out_event)
        self.connect('key-press-event', FunctionEntry.on_key_press_event)
    
    def is_empty(self):
        return (len(self.get_text()) == 0)
    
    def validate(self):
        text = self.get_text()
        
        try:
            if not self.is_empty():
                self.function = parse_function(text, names)
            
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
        
        self.update_status_icon_and_tooltip()
        
        self.emit('toggle')
    
    def clear(self):
        self.set_text('')
        self.function = None
        self.valid = True
        self.update_status_icon_and_tooltip()
        self.emit('activate')
    
    def update_status_icon_and_tooltip(self):
        icon_pos = Gtk.EntryIconPosition.PRIMARY
        if self.enabled:
            if self.valid:
                self.set_icon_from_icon_name(icon_pos, 'gtk-yes')
                self.set_icon_tooltip_text(icon_pos, self.valid_tooltip)
            else:
                self.set_icon_from_icon_name(icon_pos, 'error')
                self.set_icon_tooltip_text(icon_pos, self.invalid_tooltip.format(self.error))
        else:
            self.set_icon_from_icon_name(icon_pos, 'gtk-no')
            self.set_icon_tooltip_text(icon_pos, self.disabled_tooltip)
    
    def create_plot(self, viewport):
        return FunctionPlot(viewport, self.function)
    
    def on_status_icon_press(self, icon, event):
        if icon == Gtk.EntryIconPosition.PRIMARY and event.button == 1:
            self.toggle()
        
        return False
    
    def on_focus_out_event(self, event):
        self.emit('activate')
        
        return False
    
    def on_key_press_event(self, event):
        if event.keyval == Gdk.KEY_Escape:
            self.clear()
        
        return False
    
    def on_remove_icon_press(self, icon, event):
        if icon == Gtk.EntryIconPosition.SECONDARY and event.button == 1:
            self.emit('remove-button-press')
        
        return False
    
    def show_remove_icon(self):
        self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'gtk-remove')
    
    def hide_remove_icon(self):
        self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)

class FunctionEntryRow(Gtk.HBox):
    def __init__(self):
        super().__init__(False, 4)
        
        self.entry = FunctionEntry()
        self.entry.set_hexpand(True)
        self.entry.set_margin_left(4)
        
        self.button = Gtk.Button.new_from_stock('gtk-add')
        
        self.pack_start(self.entry, True, True, 2)
        self.pack_start(self.button, False, False, 2)

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

class FunctionEntryList(Gtk.VBox):
    __gsignals__ = {
        'entry-update': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntry,)),
        'entry-remove': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntry,)),
        'entry-toggle': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntry,))
    }
    
    def __init__(self):
        super().__init__(False, 0)
        
        self.entry_rows = []
        
        self.entry_add()
    
    def entry_update(self, entry):
        self.emit('entry-update', entry)
    
    def entry_remove(self, entry, entry_row):
        self.entry_rows.remove(entry_row)
        self.remove(entry_row)
        
        if len(self.entry_rows) == 1:
            row = self.entry_rows[0]
            row.entry.hide_remove_icon()
        
        self.emit('entry-remove', entry)
    
    def entry_toggle(self, entry):
        self.emit('entry-toggle', entry)
    
    def entry_add(self, position=None):
        entry_row = FunctionEntryRow()
        
        self.entry_rows.append(entry_row)
        
        if len(self.entry_rows) > 1:
            for row in self.entry_rows:
                row.entry.show_remove_icon()
        
        self.pack_start(entry_row, True, True, 2)
        
        if position is not None:
            self.reorder_child(entry_row, position)
        
        entry_row.show_all()
        
        def on_button_click(widget):
            value = GObject.Value()
            value.init(int)
            self.child_get_property(entry_row, 'position', value)
            self.entry_add(value.get_int() + 1)
            return False
        
        entry_row.button.connect('clicked', on_button_click)
        entry_row.entry.connect('toggle', self.entry_toggle)
        entry_row.entry.connect('activate', self.entry_update)
        entry_row.entry.connect('remove-button-press', self.entry_remove, entry_row)
        
        return True
    
    def update_add_button_position(self):
        bottom_entry = self.entries[-1]
        
        self.remove(self.add_button)
        self.attach_next_to(self.add_button, bottom_entry, Gtk.PositionType.RIGHT, 1, 1)

class PlotControls(Gtk.VBox):
    def __init__(self, viewport):
        super().__init__(False, 0)
        
        self.viewport = viewport
        self.entry_list = FunctionEntryList()
        self.viewport_controls = ViewportControls(self.viewport)
        
        self.pack_start(self.viewport_controls, False, False, 0)
        self.pack_start(self.entry_list, False, False, 0)
