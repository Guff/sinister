import os.path

from gi.repository import GLib, Gio

class Setting(object):
    def __init__(self, name, default, desc=None):
        self.name, self.default, self.desc = name, default, desc
    
    def __repr__(self):
        return 'Setting(name={s.name}, default={s.default}, desc={s.desc})'.format(s=self)
    
    def generate_docstring(self):
        doc = '**{setting.name}**: {setting.desc}\n\t*default value*: {setting.default}'
        return doc.format(setting=self)

class ConfigMeta(type):
    def __new__(mclass, class_name, bases, attrs):
        attrs['__doc__'] = mclass.generate_docstring(class_name, attrs['settings'])
        
        return super().__new__(mclass, class_name, bases, attrs)
    
    @staticmethod
    def generate_docstring(class_name, settings):
        first_line = """Available settings are:\n"""
        
        setting_docs = []
        for setting in settings:
            setting_docs.append(setting.generate_docstring())
        
        return first_line + '\n'.join(setting_docs)

class BaseConfig(object, metaclass=ConfigMeta):
    """Base class for sinister's single-instance configuration objects. Each
    subclass overrides BaseConfig's properties attribute in order to specify
    the specific settings and corresponding defaults of the subclass.
    
    The docstring describing the settings for each subclass is automatically
    generated.
    """
    settings = []
    def __init__(self, *args):
        for new_setting in args:
            old_settings = list(self.settings)
            for index, old_setting in enumerate(old_settings):
                if new_setting.name == old_setting.name:
                    self.settings[index] = new_setting
                    break
            else:
                err = '{setting} is not a valid {config.__class__.__name__} setting'
                raise ValueError(err.format(config=self, setting=new_setting))
        
        for setting in self.settings:
            setattr(self, setting.name, setting.default)
    
    def __repr__(self):
        config_string = "{config.__class__.__name__}({params})"
        return config_string.format(config=config, params=', '.join(map(str, self.settings)))
    
class GeneralConfig(BaseConfig):
    settings = [Setting(name='use_cython', default=False)]

class WindowConfig(BaseConfig):
    settings = [Setting(name='default_width', default=500),
                Setting(name='default_height', default=400),
                Setting(name='maximize_on_start', default=False)]

class ViewportConfig(BaseConfig):
    settings = [Setting(name='default_min_x', default=-10.0),
                Setting(name='default_max_x', default=10.0),
                Setting(name='default_min_y', default=-10.0),
                Setting(name='default_max_y', default=10.0)]

class FunctionPlotConfig(BaseConfig):
    settings = [Setting(name='plot_color', default='red')]

class NamesConfig(BaseConfig):
    settings = [Setting(name='names', default={})]

class SinisterConfig(object):
    def __init__(self):
        self.conf_dir = os.path.join(GLib.get_user_config_dir(), 'sinister')
        g_conf_dir = Gio.file_parse_name(self.conf_dir)
        if not g_conf_dir.query_exists(None):
            g_conf_dir.make_directory(None)
        
        self.conf_filename = os.path.join(self.conf_dir, 'sinister_config.py')
        g_conf_file = Gio.file_parse_name(self.conf_filename)
        
        self.general = GeneralConfig()
        self.defined_names = NamesConfig()
        self.function_plot = FunctionPlotConfig()
        self.window = WindowConfig()
        self.viewport = ViewportConfig()
    
    def load_user_config(self):
        try:
            conf_file = open(self.conf_filename)
        except IOError:
            pass
        else:
            conf_str = conf_file.read()
            code = compile(conf_str, self.conf_filename, 'exec')
            exec(code, {'conf': self})
            conf_file.close()

conf = SinisterConfig()
conf.load_user_config()
