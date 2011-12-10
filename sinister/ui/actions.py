from gi.repository import Gtk

class SinisterActions(Gtk.ActionGroup):
    def __init__(self, activate_cb):
        super().__init__('SinisterActions')
        
        self.add_file_actions()
        self.add_help_actions()
        
        for action in self.list_actions():
            action.connect('activate', activate_cb)
    
    def add_file_actions(self):
        self.add_actions([
            ('FileMenu', None, '_File'),
            ('Quit', Gtk.STOCK_QUIT)
        ])
        
    
    def add_help_actions(self):
        self.add_actions([
            ('HelpMenu', None, '_Help'),
            ('About', Gtk.STOCK_ABOUT)
        ])
