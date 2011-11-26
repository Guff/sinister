from sinister.ui.widgets import FunctionEntry, PlotStatusBar
from gi.repository import Gtk as gtk, Gdk as gdk

class PlotContainer(gtk.VBox):
    def __init__(self, plot_area):
        super().__init__(False, 0)
        
        self.plot_area = plot_area
        
        self.function_entry = FunctionEntry(self.plot_area)
        
        self.pack_start(self.function_entry, False, False, 0)
        self.pack_start(self.plot_area, True, True, 0)
        
        self.separator = gtk.HSeparator()
        self.pack_start(self.separator, False, False, 0)
        
        self.status_bar = PlotStatusBar()
        self.pack_start(self.status_bar, False, False, 0)
        
        self.plot_area.set_can_focus(True)
        self.plot_area.add_events(gdk.EventMask.LEAVE_NOTIFY_MASK
                                | gdk.EventMask.BUTTON_PRESS_MASK
                                | gdk.EventMask.BUTTON_RELEASE_MASK
                                | gdk.EventMask.POINTER_MOTION_MASK
                                | gdk.EventMask.POINTER_MOTION_HINT_MASK
                                | gdk.EventMask.KEY_PRESS_MASK
                                | gdk.EventMask.KEY_RELEASE_MASK
                                | gdk.EventMask.SCROLL_MASK)
        
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
        
        self.plot_area.connect("motion-notify-event", motion_notify_event)
        self.plot_area.connect("leave-notify-event", leave_notify_event)

