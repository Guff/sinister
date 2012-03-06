from sinister.config import conf
from sinister.exceptions import FunctionCreationError
from sinister.parse import Parser
from sinister.plotters import FunctionPlot
from sinister.names import names

from gi.repository import GObject, Gdk, Gtk

class FunctionEntry(Gtk.Entry):
    __gsignals__ = {
        'toggle': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'remove-button-press': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'create-plot': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object,))
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
        self.connect('activate', FunctionEntry.on_activate)
    
    def is_empty(self):
        return (len(self.get_text()) == 0)
    
    def validate(self):
        if self.is_empty():
            self.valid = True
            return
        
        text = self.get_text()
        
        try:
            self.function = Parser(text, names).create_function()
            
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
        plot = FunctionPlot(viewport, self.function)
        self.emit('create-plot', plot)
        return plot
    
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
    
    def on_activate(self):
        try:
            self.validate()
        except FunctionCreationError:
            pass
        
        self.update_status_icon_and_tooltip()
    
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
        
        default_color = Gdk.RGBA()
        default_color.parse(conf.function_plot.plot_color)
        
        self.color_button = Gtk.ColorButton.new_with_rgba(default_color)
        
        self.button = Gtk.Button.new_from_stock('gtk-add')
        self.button.set_focus_on_click(False)
        
        self.entry.connect('create-plot', self.on_create_plot)
        
        self.pack_start(self.color_button, False, False, 2)
        self.pack_start(self.entry, True, True, 2)
        self.pack_start(self.button, False, False, 2)
    
    def on_create_plot(self, widget, plot):
        plot.rgba = self.color_button.get_rgba()

class FunctionEntryList(Gtk.VBox):
    __gsignals__ = {
        'entry-update': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntry,)),
        'entry-remove': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntry,)),
        'entry-toggle': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntry,)),
        'entry-row-focus': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntryRow,)),
        'entry-color-set': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (FunctionEntryRow,))
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
    
    def entry_color_set(self, widget, param, row):
        self.emit('entry-color-set', row)
    
    def entry_add(self, position=None):
        entry_row = FunctionEntryRow()
        
        self.entry_rows.append(entry_row)
        
        if len(self.entry_rows) > 1:
            for row in self.entry_rows:
                row.entry.show_remove_icon()
        
        self.pack_start(entry_row, True, True, 2)
        
        if position is not None:
            self.reorder_child(entry_row, position)
        
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
        entry_row.color_button.connect('notify::rgba', self.entry_color_set, entry_row)
        
        entry_row.show_all()
        
        entry_row.entry.grab_focus()
        
        return True
