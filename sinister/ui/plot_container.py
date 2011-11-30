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
        
        self.plot_area.set_can_focus(True)
        self.plot_area.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK
                                | Gdk.EventMask.BUTTON_PRESS_MASK
                                | Gdk.EventMask.BUTTON_RELEASE_MASK
                                | Gdk.EventMask.POINTER_MOTION_MASK
                                | Gdk.EventMask.POINTER_MOTION_HINT_MASK
                                | Gdk.EventMask.KEY_PRESS_MASK
                                | Gdk.EventMask.KEY_RELEASE_MASK
                                | Gdk.EventMask.SCROLL_MASK)
        
        # realize that this callback is called by the plot area widget, not
        # the plot container widget. otherwise, accessing the status bar would
        # be a hassle
        def motion_notify_event(widget, event):
            window_x, window_y = event.x, event.y
            plot_x, plot_y = widget.plot_bg.window_to_plot(window_x, window_y)
            self.status_bar.update_coords(plot_x, plot_y)
            
            return False
        
        # same as above
        def leave_notify_event(widget, event):
            self.status_bar.clear_coords()
            
            return False
        
        def entry_activate(widget):
            plot = None
            try:
                widget.validate()
            except FunctionCreationError:
                pass
            else:
                if not widget.is_empty():
                    plot = widget.create_plot(self.plot_area.viewport)
            
            widget.update_icon_and_tooltip()
            
            self.plot_area.update_plot(widget, plot)
            
            self.plot_area.refresh()
        
        def entry_toggle(widget):
            self.plot_area.refresh()
        
        self.plot_area.connect("motion-notify-event", motion_notify_event)
        self.plot_area.connect("leave-notify-event", leave_notify_event)
        self.plot_controls.entry.connect("activate", entry_activate)
        self.plot_controls.entry.connect("toggle", entry_toggle)
