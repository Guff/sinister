from gi.repository import GLib, Gio, GObject, Gdk

import os.path
import imp

class WindowConfig(GObject.Object):
    default_width     = GObject.property(type=int, default=500)
    default_height    = GObject.property(type=int, default=400)
    maximize_on_start = GObject.property(type=bool, default=False)

class ViewportConfig(GObject.Object):
    default_min_x = GObject.property(type=float, default=-10.0)
    default_max_x = GObject.property(type=float, default=10.0)
    default_min_y = GObject.property(type=float, default=-10.0)
    default_max_y = GObject.property(type=float, default=10.0)

class FunctionPlotConfig(GObject.Object):
    def get_plot_color(self):
        return self._plot_color
    
    def set_plot_color(self, color):
        if is_valid_color(color):
            self._plot_color = color
        else:
            raise UserWarning('"{}" is not a valid GDK color'.format(color))
    
    plot_color = GObject.property(type=str, default='black',
                                  getter=get_plot_color, setter=set_plot_color)
    
    @staticmethod
    def is_valid_color(color):
        return (Gdk.color_parse(color) is not None)

class NamesConfig(GObject.Object):
    __gsignals__ = {
        'changed': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
    }
    
    def __init__(self):
        super().__init__()
        
        self.names = {}
    
    def emit_changed(method):
        def wrapper(self, *args, **kwargs):
            ret = method(self, *args, **kwargs)
            self.emit('changed')
            return ret
        
        return wrapper
    
    def __getattr__(self, name):
        attr = getattr(self.names, name)
        return emit_changed(attr) if callable(attr) else attr
    
    def __getitem__(self, key):
        return self[key]
    
    @emit_changed
    def __setitem__(self, key, value):
        self.names[key] = value
    
    @emit_changed
    def __delitem__(self, key):
        del self.names[key]

class SinisterConfig(GObject.Object):
    def __init__(self):
        self.conf_dir = os.path.join(GLib.get_user_config_dir(), 'sinister')
        g_conf_dir = Gio.file_parse_name(self.conf_dir)
        if not g_conf_dir.query_exists(None):
            g_conf_dir.make_directory(None)
        
        self.conf_filename = os.path.join(self.conf_dir, 'sinister_config.py')
        g_conf_file = Gio.file_parse_name(self.conf_filename)
        self.conf_file_monitor = g_conf_file.monitor(Gio.FileMonitorFlags.NONE, None)
        
        def monitor_change(config, file_object, new_file_object, event_type):
            config.load_user_config()
        
        self.conf_file_monitor.connect_object('changed', monitor_change, self)
        
        self.names = NamesConfig()
        self.function_plot = FunctionPlotConfig()
        self.window = WindowConfig()
        self.viewport = ViewportConfig()
    
    def load_user_config(self):
        try:
            conf_str = open(self.conf_filename).read()
        except IOError:
            pass
        else:
            code = compile(conf_str, self.conf_filename, 'exec')
            exec(code, {'conf': self})

conf = SinisterConfig()
conf.load_user_config()
