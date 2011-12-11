from sinister.config import conf
from sinister.viewport import Viewport
from sinister.plotters import PlotBg
from sinister.history import History
from sinister.ui.plot_area import PlotArea
from sinister.ui.plot_container import PlotContainer
from sinister.ui.actions import SinisterActions

import os.path
import sys

from gi.repository import Gtk

class SinisterMainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title='sinister')
        
        self.viewport = Viewport(conf.viewport.default_min_x,
                                 conf.viewport.default_max_x,
                                 conf.viewport.default_min_y,
                                 conf.viewport.default_max_y)
        
        plot_bg = PlotBg(self.viewport)
        plot_area = PlotArea(self.viewport, plot_bg)
        plot_container = PlotContainer(plot_area)
        
        try:
            ui_file = open(os.path.join('data', 'sinister.ui'))
        except IOError:
            ui_file = open(os.path.join(sys.path, 'share', 'sinister', 'sinister.ui'))
        
        ui_info = ui_file.read()
        
        action_group = SinisterActions(self.on_action_activate)
        
        manager = Gtk.UIManager()
        manager.insert_action_group(action_group, 0)
        manager.add_ui_from_string(ui_info)
        
        self.add_accel_group(manager.get_accel_group())
        
        self.history = History(list(self.viewport))
        
        self.viewport.connect('update', self.on_viewport_update)
        
        menu_bar = manager.get_widget('/MenuBar')
        
        vbox = Gtk.VBox(False, 0)
        vbox.pack_start(menu_bar, False, False, 0)
        vbox.pack_start(plot_container, True, True, 0)
        
        self.add(vbox)
        
        if conf.window.maximize_on_start:
            self.maximize()
        else:
            self.set_default_size(conf.window.default_width, conf.window.default_height)
        
        self.connect('delete-event', Gtk.main_quit)
    
    def show_about_dialog(self):
        about = Gtk.AboutDialog(parent=self,
                                program_name='sinister',
                                version='0.0.1',
                                copyright='Copyright ©2011 guff',
                                website='https://github.com/Guff/sinister',
                                comments='a simple plotting application',
                                authors=['guff'],
                                title='About sinister')
        
        about.connect('response', lambda widget, response_id: widget.destroy())
        about.show()
    
    def on_viewport_update(self, viewport, record):
        if record:
            self.history.append(list(viewport))
    
    def on_undo_action(self, action):
        self.viewport.handler_block_by_func(self.on_viewport_update)
        self.viewport.update(self.history.undo())
        self.viewport.handler_unblock_by_func(self.on_viewport_update)
    
    def on_redo_action(self, action):
        self.viewport.handler_block_by_func(self.on_viewport_update)
        self.viewport.update(self.history.redo())
        self.viewport.handler_unblock_by_func(self.on_viewport_update)
    
    def on_action_activate(self, action):
        name = action.get_name()
        if name == 'Quit':
            Gtk.main_quit()
        elif name == 'About':
            self.show_about_dialog()
        elif name == 'Undo':
            self.on_undo_action(action)
        elif name == 'Redo':
            self.on_redo_action(action)
