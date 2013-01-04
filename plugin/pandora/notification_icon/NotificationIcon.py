from gi.repository import Gtk

import rb

class NotificationIcon:
    def __init__(self, plugin, songs_action):
        self.plugin = plugin
        self.songs_action = songs_action
        
        self.tray_icon = TrayIcon(rb.find_plugin_file(self.plugin, 'pandora/notification_icon/pandora.png'))
        self.build_context_menu();
        #TODO: Disable actions when they're N/A

    def build_context_menu(self):
        menu = self.tray_icon.popup
        def button(text, action, icon):
            item = Gtk.ImageMenuItem(text)
            image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
            item.set_image(image)
            item.connect('activate', action) 
            item.show()
            menu.append(item)
            print "Added item"
            return item

        # Action callbacks
        def love_song_callback(ignore):
            self.songs_action.love_current_song()
        def ban_song_callback(ignore):
            self.songs_action.ban_current_song()
        def tire_song_callback(ignore):
            self.songs_action.tire_current_song()
        button("_Love Song", love_song_callback, Gtk.STOCK_ABOUT)
        button("_Ban Song", ban_song_callback, Gtk.STOCK_CANCEL)
        button("_Tired of this song", tire_song_callback, Gtk.STOCK_JUMP_TO)
        
        self.tray_icon.set_visible(True)
        
    def hide(self):
        self.tray_icon.set_visible(False)
    
    def show(self):
        self.tray_icon.set_visible(True) 
        #TODO: Clean up

    def destroy(self):
        self.tray_icon.popup.popdown()
        self.tray_icon.set_visible(False)
        self.tray_icon.destroy(); del self.tray_icon
        
class TrayIcon(Gtk.StatusIcon):
    def __init__(self, iconfile):
        Gtk.StatusIcon.__init__(self)
        self.set_from_file(iconfile)        
        self.popup = Gtk.Menu()
        self.bpe_id = self.connect("button-press-event", self.icon_clicked)
        
    def icon_clicked(self, statusicon, event):
        self.popup.popup(None, None, Gtk.StatusIcon.position_menu, event.button, event.time, self)
        
    def destroy(self):
        self.popup.destroy(); del self.popup
        self.disconnect(self.bpe_id)

