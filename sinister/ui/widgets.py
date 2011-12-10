from sinister.config import conf
from sinister.plotters import FunctionPlot
from sinister.names import names
from sinister.exceptions import FunctionCreationError
from sinister.parse import parse_function

from sys import float_info
from math import floor, ceil, pi
from gi.repository import GObject, Gtk, Gdk
import cairo

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
        default_color.parse(conf.function_plot.color)
        
        self.color_button = Gtk.ColorButton.new_with_rgba(default_color)
        
        self.button = Gtk.Button.new_from_stock('gtk-add')
        self.button.set_focus_on_click(False)
        
        self.entry.connect('create-plot', self.on_create_plot)
        
        self.pack_start(self.color_button, False, False, 2)
        self.pack_start(self.entry, True, True, 2)
        self.pack_start(self.button, False, False, 2)
    
    def on_create_plot(self, widget, plot):
        plot.rgba = self.color_button.get_rgba()

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

class Metric(object):
    def __init__(self, metric_name, abbrev, pixels_per_unit, ruler_scale, subdivide):
        self.metric_name, self.abbrev = metric_name, abbrev
        self.pixels_per_unit = pixels_per_unit
        self.ruler_scale, self.subdivide = ruler_scale, subdivide

metrics = [Metric('Pixel', 'Pi', 1.0, [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000], [1, 5, 10, 50, 100]),
           Metric('Inches', 'In', 72.0, [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], [1, 2, 4, 8, 16]),
           Metric('Centimeters', 'Cn', 28.35, [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000], [1, 5, 10, 50, 100])]

class Ruler(Gtk.Widget, Gtk.Orientable):
    def __init__(self, size=14):
        super().__init__()
        
        self.size = size
        self._position = 0.0
        
        sc = self.get_style_context()
        
        sc.add_class('frame')
    
    def get_position(self):
        return self._position
    
    def set_position(self, position):
        self._position = position
        self.queue_draw()
    
    def do_get_preferred_height(self):
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            return (self.size, self.size)
        else:
            return super().do_get_preferred_height()
    
    def do_get_preferred_width(self):
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            return super().do_get_preferred_width()
        else:
            return (self.size, self.size)
    
    def do_draw(self, cr):
        self.draw_rule(cr)
        self.draw_pos(cr)
        
        return False
    
    def draw_rule(self, cr):
        cr.save()
        
        horizontal = self.orientation == Gtk.Orientation.HORIZONTAL
        
        sc = self.get_style_context()
        alloc = self.get_allocation()
        
        orient, subdivs = self.orientation, self.subdivisions
        
        ruler_fg = sc.get_color(Gtk.StateFlags.NORMAL)
        Gdk.cairo_set_source_rgba(cr, ruler_fg)
        
        cr.set_line_width(1.0)
        
        if horizontal:
            span = alloc.width
        else:
            span = alloc.height
        
        # prevents a bit of code duplication
        flip_if_vertical = lambda x, y: (x, y) if horizontal else (y, x)
        
        for tick in range(0, span + 1, self.major_ticks_spacing):
            tick_start = flip_if_vertical(tick + 0.5, 0)
            tick_end = flip_if_vertical(0, (3 * self.size) // 4)
            
            cr.move_to(*tick_start)
            cr.rel_line_to(*tick_end)
            
            for subtick in range(1, subdivs):
                spacing = (subtick * self.major_ticks_spacing) // subdivs
                
                if subdivs % 2 == 0 and subtick == subdivs // 2:
                    subtick_size = self.size // 2
                else:
                    subtick_size = (3 * self.size) // 8
                
                subtick_start = flip_if_vertical(tick + spacing + 0.5, 0)
                subtick_end = flip_if_vertical(0, subtick_size + 0.5)
                
                cr.move_to(*subtick_start)
                cr.rel_line_to(*subtick_end)
            
        cr.stroke()
        
        end = alloc.width if horizontal else alloc.height
        coords_start = flip_if_vertical(0, self.size - 2)
        coords_end = flip_if_vertical(end, self.size - 2)
        
        Gtk.render_line(sc, cr, *(coords_start + coords_end))
        
        cr.restore()
    
    def draw_pos(self, cr):
        cr.save()
        
        sc = self.get_style_context()
        
        horizontal = self.orientation == Gtk.Orientation.HORIZONTAL
        
        x, y = self.position - self.size // 4, self.size // 2 - 2
        x, y = (x, y) if horizontal else (y, x)
        Gtk.render_arrow(sc,
                         cr,
                         pi if horizontal else pi / 2,
                         x,
                         y,
                        # we need to ensure the arrow size is even,
                        # so it doesn't get blurrified
                         (self.size + (-self.size % 4)) // 2)
                
        cr.restore()
    
    def do_realize(self):
        self.set_realized(True)
        
        alloc = self.get_allocation()
        
        attr_mask = Gdk.WindowAttributesType.X
        attr_mask |= Gdk.WindowAttributesType.Y
        attr_mask |= Gdk.WindowAttributesType.VISUAL
        
        attrs = Gdk.WindowAttr()
        attrs.window_type = Gdk.WindowType.CHILD
        attrs.x, attrs.y = alloc.x, alloc.y
        attrs.width, attrs.height = alloc.width, alloc.height
        attrs.wclass = Gdk.WindowWindowClass.OUTPUT
        attrs.visual = self.get_visual()
        attrs.event_mask = self.get_events()
        attrs.event_mask |= Gdk.EventMask.EXPOSURE_MASK
        attrs.event_mask |= Gdk.EventMask.POINTER_MOTION_MASK
        attrs.event_mask |= Gdk.EventMask.POINTER_MOTION_HINT_MASK
        
        window = Gdk.Window(self.get_parent_window(), attrs, attr_mask)
        window.set_user_data(self)
        self.set_window(window)
        
        sc = self.get_style_context()
        sc.set_background(window)
    
    def do_motion_notify_event(self, event):
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            self.position = event.x
        else:
            self.position = event.y
        
        if event.is_hint:
            event.request_motions()
    
    orientation = GObject.property(type=Gtk.Orientation, default=Gtk.Orientation.HORIZONTAL)
    position = GObject.property(type=float, getter=get_position, setter=set_position)
    size = GObject.property(type=int)
    major_ticks_spacing = GObject.property(type=int, default=100)
    subdivisions = GObject.property(type=int, default=10)

GObject.type_register(Ruler)

class HRuler(Ruler):
    def __init__(self, size=None):
        if size is not None:
            super().__init__(size)
        else:
            super().__init__()
        
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

GObject.type_register(HRuler)

class VRuler(Ruler):
    def __init__(self, size=None):
        if size is not None:
            super().__init__(size)
        else:
            super().__init__()
        
        self.set_orientation(Gtk.Orientation.VERTICAL)

GObject.type_register(VRuler)
