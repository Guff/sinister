from sinister.config import conf
from sinister.plotters import PlotBg

from gi.repository import GObject, Gtk, Gdk

class PlotArea(Gtk.DrawingArea):
    __gsignals__ = {
        'refresh': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
    }
    
    def __init__(self, viewport, plot_bg):
        super().__init__()
        
        self.viewport = viewport
        self.plot_bg = plot_bg
        
        self.button_press_mode = conf.plot_area.button_press_mode
        self.zoom_rect = None
        
        self.dimensions = None
        
        self.plots = {}
        
        self.set_can_focus(True)
        self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK
                      | Gdk.EventMask.BUTTON_PRESS_MASK
                      | Gdk.EventMask.BUTTON_RELEASE_MASK
                      | Gdk.EventMask.POINTER_MOTION_MASK
                      | Gdk.EventMask.POINTER_MOTION_HINT_MASK
                      | Gdk.EventMask.KEY_PRESS_MASK
                      | Gdk.EventMask.KEY_RELEASE_MASK
                      | Gdk.EventMask.SCROLL_MASK)
        
        self.connect('configure-event', PlotArea.on_configure_event)
        self.connect('draw', PlotArea.on_draw_event)
        # make sure the plots et al. have all handled the viewport update
        # before we redraw
        self.viewport.connect_after('update', self.on_viewport_update)
        self.connect('button-press-event', PlotArea.on_button_2_press)
        self.connect('button-press-event', PlotArea.on_button_press)
    
    def on_draw_event(self, cr):
        self.plot(cr)
        if self.zoom_rect is not None:
            self.draw_zoom_rect(cr)
        return False
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for entry, plot in self.plots.items():
            if entry.enabled:
                plot.plot(cr)
    
    def draw_zoom_rect(self, cr):
        cr.save()
        
        cr.rectangle(*self.zoom_rect)
        cr.clip_preserve()
        
        cr.set_source_rgba(0.1, 0.3, 0.7, 0.7)
        cr.set_line_width(4)
        cr.stroke_preserve()
        cr.set_source_rgba(0.1, 0.3, 0.9, 0.4)
        cr.fill()
        cr.restore()
    
    def on_button_press(self, event):
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_PRESS:
            if self.button_press_mode == 'drag':
                self.button_press_drag(event)
            elif self.button_press_mode == 'zoom-rect':
                self.button_press_zoom_rect(event)
        
        return False
    
    def button_press_zoom_rect(self, event):
        allocation = self.get_allocation()
        width, height = allocation.width, allocation.height
        
        x, y = event.x, event.y
        
        def on_motion_notify(widget, event):
            if widget.zoom_rect is not None:
                # invalidate the region where the old rectangle was
                widget.queue_draw_area(*widget.zoom_rect)
            
            x0, y0 = x, y
            x1, y1 = event.x, event.y
            
            x0, x1 = (x0, x1) if x1 > x0 else (x1, x0)
            y0, y1 = (y0, y1) if y1 > y0 else (y1, y0)
            
            # gdk uses doubles for pointer coordinates, but apparently ints
            # (or truncated doubles) for clip regions
            x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
            
            widget.zoom_rect = (x0, y0, x1 - x0, y1 - y0)
            
            widget.queue_draw_area(*widget.zoom_rect)
            
            return False
        
        def on_button_release(widget, event, handles):
            if event.button != 1:
                return False
            
            x0, y0 = x, y
            x1, y1 = event.x, event.y
            
            x0, x1 = (x0, x1) if x1 > x0 else (x1, x0)
            y0, y1 = (y0, y1) if y1 > y0 else (y1, y0)
            
            min_x, min_y = widget.plot_bg.window_to_plot(x0, y1)
            max_x, max_y = widget.plot_bg.window_to_plot(x1, y0)
            
            widget.viewport.update({'min_x': min_x,
                                    'max_x': max_x,
                                    'min_y': min_y,
                                    'max_y': max_y})
            
            widget.handler_disconnect(handles['motion'])
            widget.handler_disconnect(handles['release'])
            
            widget.zoom_rect = None
            
            return False
        
        # passing a mutable container (a dict in this case), which is then
        # updated to hold the handle IDs, to the release handler was the best
        # way i could think of to be able to disconnect the handles
        handles = {}
        
        handles['release'] = self.connect('button-release-event', on_button_release, handles)
        handles['motion'] = self.connect('motion-notify-event', on_motion_notify)
    
    def button_press_drag(self, event):
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))
        
        allocation = self.get_allocation()
        width, height = allocation.width, allocation.height
        prev_coords = {'x': event.x, 'y': event.y}
        
        viewport_width = self.viewport.max_x - self.viewport.min_x
        viewport_height = self.viewport.max_y - self.viewport.min_y
        
        x_ratio = viewport_width / width
        y_ratio = viewport_height / height
        
        def on_motion_notify(widget, event):
            x, y = event.x, event.y
            dx = x_ratio * (x - prev_coords['x'])
            dy = y_ratio * (y - prev_coords['y'])
            widget.viewport.translate(dx, dy)
            
            prev_coords['x'] = x
            prev_coords['y'] = y
        
        def on_button_release(widget, event, handles):
            if event.button == 1:
                widget.get_window().set_cursor(None)
                widget.handler_disconnect(handles['motion'])
                widget.handler_disconnect(handles['release'])
                return True
            else:
                return False
        
        # passing a mutable container (a dict in this case), which is then
        # updated to hold the handle IDs, to the release handler was the best
        # way i could think of to be able to disconnect the handles
        handles = {}
        
        handles['release'] = self.connect('button-release-event', on_button_release, handles)
        handles['motion'] = self.connect('motion-notify-event', on_motion_notify)
    
    def on_button_2_press(self, event):
        if event.button != 1 or event.type != Gdk.EventType._2BUTTON_PRESS:
            return False
        
        min_x0, max_x0, min_y0, max_y0 = self.viewport
        plot_width = max_x0 - min_x0
        plot_height = max_y0 - min_y0
        
        plot_x, plot_y = self.plot_bg.window_to_plot(event.x, event.y)
        plot_x = min(max(plot_x, min_x0 + plot_width / 4), max_x0 - plot_width / 4)
        plot_y = min(max(plot_y, min_y0 + plot_height / 4), max_y0 - plot_height / 4)
        
        new_limits = {'min_x': plot_x - plot_width / 4,
                      'max_x': plot_x + plot_width / 4,
                      'min_y': plot_y - plot_height / 4,
                      'max_y': plot_y + plot_height / 4}
        
        self.viewport.update(new_limits)
        
        return True
    
    def on_configure_event(self, event):
        if self.dimensions == (event.width, event.height):
            return False
        
        self.dimensions = (event.width, event.height)
        
        self.resize_window()
        
        return False
    
    def resize_window(self):
        self.plot_bg.resize(self.dimensions)
        
        for plot in self.plots.values():
            plot.resize(self.dimensions)
    
    def update_plot(self, entry, plot):
        plot.resize(self.dimensions)
            
        self.plots[entry] = plot
        
        self.emit('refresh')
    
    def remove_plot(self, entry):
        if entry in self.plots:
            del self.plots[entry]
            self.emit('refresh')
    
    def on_viewport_update(self, viewport):
        self.emit('refresh')
    
    def do_refresh(self):
        self.queue_draw()
