from sinister.exceptions import FunctionCreationError
from sinister.ui.widgets import PlotControls, PlotStatusBar
from gi.repository import Gtk, Gdk

class PlotContainer(Gtk.VBox):
    def __init__(self, plot_area):
        super().__init__(False, 0)
        
        self.plot_area = plot_area
        
        self.plot_controls = PlotControls(self.plot_area.viewport)
        
        self.pack_start(self.plot_controls, False, False, 0)
        self.pack_start(Gtk.HSeparator(), False, False, 0)
        self.pack_start(self.plot_area, True, True, 0)
        
        self.pack_start(Gtk.HSeparator(), False, False, 0)
        
        self.status_bar = PlotStatusBar()
        self.pack_start(self.status_bar, False, False, 0)
        
        self.plot_area.connect('motion-notify-event', self.motion_notify_event)
        self.plot_area.connect('leave-notify-event', self.leave_notify_event)
        self.plot_controls.entry_list.connect('entry-update', self.entry_activate)
        self.plot_controls.entry_list.connect('entry-toggle', self.entry_toggle)
        self.plot_controls.entry_list.connect('entry-remove', self.entry_remove)
    
    def motion_notify_event(self, widget, event):
        window_x, window_y = event.x, event.y
        plot_x, plot_y = widget.plot_bg.window_to_plot(window_x, window_y)
        self.status_bar.update_coords(plot_x, plot_y)
        
        return False
    
    def leave_notify_event(self, widget, event):
        self.status_bar.clear_coords()
        
        return False
    
    def entry_toggle(self, widget, entry):
        self.plot_area.emit('refresh')
    
    def entry_activate(self, widget, entry):
        plot = None
        try:
            entry.validate()
        except FunctionCreationError:
            pass
        else:
            if not entry.is_empty():
                plot = entry.create_plot(self.plot_area.viewport)
        
        entry.update_status_icon_and_tooltip()
        
        if plot is not None:
            self.plot_area.update_plot(entry, plot)
        else:
            self.plot_area.remove_plot(entry)
    
    def entry_remove(self, widget, entry):
        self.plot_area.remove_plot(entry)
