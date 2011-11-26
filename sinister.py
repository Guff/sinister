#!/usr/bin/env python

from gi.repository import Gtk as gtk, Gdk as gdk
import cairo

from math import sin, gamma, lgamma

class Viewport(object):
    def __init__(self, min_x, max_x, min_y, max_y, x_ticks, y_ticks):
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
        self.x_ticks, self.y_ticks = x_ticks, y_ticks

class PlotConf(object):
    def __init__(self, width, height, min_step=0.5, max_step=3):
        self.width, self.height = width, height
        self.min_step, self.max_step = min_step, max_step

class Plottable(object):
    def __init__(self):
        self.viewport = None
        self.width, self.height = None, None      
        
        self.active = True  
        
        self.surface = None
    
    def toggle_active(self):
        self.active = not self.active
    
    def draw(self):
        pass
    
    def set_viewport(self, viewport):
        self.viewport = viewport
    
    def resize(self, width, height):
        if self.width == width and self.height == height:
            return
        
        self.width, self.height = width, height
        
        if self.surface is not None:
            self.surface.finish()
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
    
    def plot(self, cr):
        if not self.active:
            return
        
        cr.set_source_surface(self.surface)
        cr.paint()
    
    def plot_to_window(self, px, py):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        width, height = self.width, self.height
        
        wx = (px - min_x) * width / (max_x - min_x)
        wy = (py - max_y) * height / (min_y - max_y)
        
        return (wx, wy)
    
    def window_to_plot(self, wx, wy):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        width, height = self.width, self.height
        
        px = (max_x - min_x) * wx / width + min_x
        py = (min_y - max_y) * wy / height + max_y
        
        return (px, py)

class FunctionPlot(Plottable):
    def __init__(self, func):
        super().__init__()
        
        self.func = func
    
    def draw(self):
        cr = cairo.Context(self.surface)
        cr.set_line_width(1.0)
        
        for window_x in range(self.width + 1):
            window_y = self(window_x)
            if window_y is None:
                continue
            
            cr.line_to(window_x, window_y)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
    
    def derivative(self, x):
        x_scale = self.width / (self.max_x - self.min_x)
        delta = x_scale * self.min_step / 2
        
        try:
            return (self.func(x + delta) - self.func(x - delta)) / (2 * delta)
        except:
            return None
    
    def get_value_and_step(self, x):
        y = None
        try:
            y = self.func(x)
        except:
            return (None, self.min_step)
        
        y_scale = self.height / (self.max_y - self.min_y)
        aspect = self.width / self.height
        dy = abs(self.derivative(self, x))
        
        if dy > y_scale * self.max_step:
            return (y, self.min_step)
        else:
            return (y, self.max_step)
    
    def __call__(self, window_x):
        plot_x, _ = self.window_to_plot(window_x, 0)
        try:
            plot_y = self.func(plot_x)
            _, y = self.plot_to_window(0, plot_y)
            return y
        except:
            return None

class PlotBg(Plottable):
    def draw(self):
        origin_x, origin_y = self.plot_to_window(0, 0)
        
        cr = cairo.Context(self.surface)
        
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        
        cr.move_to(0, origin_y)
        cr.line_to(self.width, origin_y)
        
        cr.move_to(origin_x, 0)
        cr.line_to(origin_x, self.height)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
        
        self.draw_ticks(cr)
    
    def draw_ticks(self, cr):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        x_ticks = self.viewport.x_ticks
        y_ticks = self.viewport.y_ticks
        
        x = min_x - (min_x % x_ticks)
        while x <= max_x:
            window_x, window_y = self.plot_to_window(x, 0)
            cr.move_to(window_x, window_y - 4)
            cr.line_to(window_x, window_y + 4)
            x += x_ticks
        
        y = min_y - (min_y % y_ticks)
        while y <= max_y:
            window_x, window_y = self.plot_to_window(0, y)
            cr.move_to(window_x - 4, window_y)
            cr.line_to(window_x + 4, window_y)
            y += y_ticks
        
        cr.set_line_width(1)
        cr.stroke()

class PlotArea(gtk.DrawingArea):
    def __init__(self, viewport):
        super().__init__()
        
        self.viewport = viewport
        
        self.width, self.height = None, None
        
        self.plot_bg = PlotBg()
        self.plot_bg.set_viewport(self.viewport)
        
        self.plots = []
        
        def delete_event(widget, event):
            gtk.main_quit()
            return False
        
        def draw_event(widget, cr):
            widget.plot(cr)
            
            return False
        
        def configure_event(widget, event):
            if event.width == widget.width or event.height == widget.height:
                return True
            
            widget.width = event.width
            widget.height = event.height
            
            widget.resize_window()
            return False
        
        self.connect("configure-event", configure_event)
        self.connect("draw", draw_event)
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for plot in self.plots:
            plot.plot(cr)
    
    def resize_window(self):
        self.plot_bg.resize(self.width, self.height)
        self.plot_bg.draw()
        
        for plot in self.plots:
            plot.resize(self.width, self.height)
            plot.draw()
    
    def add_plot(self, plot):
        plot.viewport = self.viewport
        
        if self.width is not None and self.height is not None:
            plot.resize(self.width, self.height)
            plot.draw()
        
        self.plots.append(plot)
    
    def refresh(self):
        self.queue_draw()
    
    def remove_plot(self, plot):
        try:
            self.plots.remove(plot)
            self.refresh()
        except ValueError:
            pass

class PlotStatusBar(gtk.HBox):
    def __init__(self):
        super().__init__(False, 2)
        
        self.coords_label = gtk.Label()
        self.pack_start(self.coords_label, True, True, 2)
        self.coords_label.set_halign(gtk.Align.END)
        self.coords_label.set_use_markup(True)
    
    def update_coords(self, x, y):
        self.coords_label.set_label("<tt>x: {: >14.8G} y: {: >14.8G}</tt>".format(x, y))
    
    def clear_coords(self):
        self.coords_label.set_label("")

class FunctionEntry(gtk.HBox):
    def __init__(self, plot_area):
        super().__init__(False, 0)
        
        self.plot_area = plot_area
        
        self.active = True
        self.plot = None
        
        self.entry = gtk.Entry()
        self.pack_start(self.entry, True, True, 0)
        
        self.set_icon('gtk-yes')
        self.set_icon_tooltip('Click to toggle plotting of this function')
        self.entry.set_icon_activatable(gtk.EntryIconPosition.PRIMARY, True)
        
        self.okay = True
        
        def icon_release(widget, icon, event):
            self.toggle()
        
        def activate(widget):
            self.create_plot()
        
        def focus_out_event(widget, event):
            self.create_plot()
        
        self.entry.connect('icon-release', icon_release)
        self.entry.connect('activate', activate)
        self.entry.connect('focus-out-event', focus_out_event)
    
    def create_plot(self):
        text = self.entry.get_text()
        
        if self.plot is not None:
            self.plot_area.remove_plot(self.plot)
        
        try:
            self.plot = FunctionPlot(eval("lambda x: {}".format(text)))
            self.set_icon_tooltip('Click to toggle plotting of this function')
            self.plot_area.add_plot(self.plot)
        
            self.plot_area.refresh()
        except Exception as e:
            self.set_icon('error')
            self.set_icon_tooltip('error creating function: {}'.format(e))
            self.okay = False
    
    def toggle(self):
        if self.plot is not None:
            self.plot.toggle_active()
            self.plot_area.refresh()
        
        self.active = not self.active
        
        if self.active:
            self.set_icon('gtk-yes')
        else:
            self.set_icon('gtk-no')
    
    def set_icon(self, icon_name):
        self.entry.set_icon_from_icon_name(gtk.EntryIconPosition.PRIMARY, icon_name)
    
    def set_icon_tooltip(self, text):
        self.entry.set_icon_tooltip_text(gtk.EntryIconPosition.PRIMARY, text)

class PlotConfig(gtk.VBox):
    def __init__(self, plot_area):
        super().__init__(False, 0)
        
        self.plot_area = plot_area

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

if __name__ == '__main__':
    viewport = Viewport(-10, 10, -10, 10, 1, 1)
    
    window = gtk.Window()
    window.set_default_size(400, 300)
    
    plot = PlotArea(viewport)
    
    plot_container = PlotContainer(plot)
    
    window.add(plot_container)
    
    window.connect("delete-event", gtk.main_quit)
    
    #func = FunctionPlot(gamma)
    #plot.add_plot(func)
    
    #func2 = FunctionPlot(sin)
    #plot.add_plot(func2)
    
    #window.maximize()
    window.show_all()
    
    gtk.main()
