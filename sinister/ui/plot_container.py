from sinister.exceptions import FunctionCreationError
from sinister.ui.widgets import PlotControls, PlotStatusBar
from gi.repository import Gtk, Gdk

class PlotContainer(Gtk.VBox):
    def __init__(self, plot_area):
        super().__init__(False, 0)
        
        self.plot_area = plot_area
        
        self.plot_controls = PlotControls(self.plot_area.viewport)
        scrolled_controls = Gtk.ScrolledWindow()
        scrolled_controls.add_with_viewport(self.plot_controls)
        
        adj = scrolled_controls.get_vadjustment()
        
        vpane = Gtk.VPaned()
        cframe = Gtk.Frame()
        pframe = Gtk.Frame()
        cframe.add(scrolled_controls)
        pframe.add(self.plot_area)
        vpane.pack1(cframe, False, False)
        vpane.pack2(pframe, True, False)
        
        self.pack_start(vpane, True, True, 0)
        
        self.pack_start(Gtk.HSeparator(), False, False, 0)
        
        self.status_bar = PlotStatusBar()
        self.pack_start(self.status_bar, False, False, 0)
        
        def resize_scrolled(widget, event=None):
            scrolled_controls.set_min_content_height(widget.get_allocated_height() + 6)
        
        def scroll_to_entry(widget, event):
            value = adj.get_value()
            page_size = adj.get_page_size()
            alloc = widget.get_allocation()
            
            return False
        
        self.plot_controls.connect('realize', resize_scrolled)
        self.plot_area.connect('motion-notify-event', self.on_motion_notify)
        self.plot_area.connect('leave-notify-event', self.on_leave_notify)
        self.plot_controls.entry_list.connect('entry-update', self.on_entry_update)
        self.plot_controls.entry_list.connect('entry-toggle', self.on_entry_toggle)
        self.plot_controls.entry_list.connect('entry-remove', self.on_entry_remove)
        self.plot_controls.entry_list.connect('entry-color-set', self.on_entry_color_set)
    
    def on_motion_notify(self, widget, event):
        window_x, window_y = event.x, event.y
        plot_x, plot_y = widget.plot_bg.window_to_plot(window_x, window_y)
        self.status_bar.update_coords(plot_x, plot_y)
        
        return False
    
    def on_leave_notify(self, widget, event):
        self.status_bar.clear_coords()
        
        return False
    
    def on_entry_toggle(self, widget, entry):
        self.plot_area.emit('refresh')
    
    def on_entry_color_set(self, widget, entry_row):
        new_rgba = entry_row.color_button.get_rgba()
        
        if entry_row.entry in self.plot_area.plots:
            self.plot_area.plots[entry_row.entry].rgba = new_rgba
            self.plot_area.emit('refresh')
    
    def on_entry_update(self, widget, entry):
        if entry.valid and not entry.is_empty():
            plot = entry.create_plot(self.plot_area.viewport)
            self.plot_area.update_plot(entry, plot)
        else:
            self.plot_area.remove_plot(entry)
    
    def on_entry_remove(self, widget, entry):
        self.plot_area.remove_plot(entry)
