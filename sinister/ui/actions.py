from gi.repository import Gtk

# i am lazy; this just packs the action tuple with Nones so a callback can be
# connected on creation of the action
def action_with_callback(cb, *args):
    return args + (None,) * (5 - len(args)) + (cb,)

class SinisterActions(Gtk.ActionGroup):
    def __init__(self, activate_cb):
        super().__init__('SinisterActions')
        
        self.add_file_actions(activate_cb)
        self.add_help_actions(activate_cb)
        self.add_edit_actions(activate_cb)
    
    def add_file_actions(self, cb):
        self.add_actions([
            ('FileMenu', None, '_File'),
            action_with_callback(cb, 'Quit', Gtk.STOCK_QUIT)
        ], self)
    
    def add_help_actions(self, cb):
        self.add_actions([
            ('HelpMenu', None, '_Help'),
            action_with_callback(cb, 'About', Gtk.STOCK_ABOUT)
        ], self)
    
    def add_edit_actions(self, cb):
        self.add_actions([
            ('EditMenu', None, '_Edit'),
            action_with_callback(cb, 'Undo', Gtk.STOCK_UNDO, None, '<Control>Z'),
            action_with_callback(cb, 'Redo', Gtk.STOCK_REDO, None, '<Shift><Control>Z')
        ], self)
