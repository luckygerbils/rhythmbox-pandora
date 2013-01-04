"""
    rhythmbox-pandora plugin for rhythmbox application.
    Copyright (C) 2010  Meng Jun Zheng <mzheng@andrew.cmu.edu>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GConf

from gi.repository import GnomeKeyring

GCONF_DIR = '/apps/rhythmbox/plugins/pandora'

GCONF_KEYS = {
        'icon': GCONF_DIR + '/icon'
}

class PandoraConfigureDialog(object):
    def __init__(self, builder_file, callback):
        self.__builder = Gtk.Builder()
        self.__builder.add_from_file(builder_file)

        self.gconf = GConf.Client.get_default()
        
        self.callback = callback
        self.dialog = self.__builder.get_object('preferences_dialog')
        self.dialog.connect("response", self.close_button_pressed)
        
        self.__keyring_data = {
            'id' : 0,
            'item': None
        }
        
        enable_icon = self.__builder.get_object("enable_icon")
        enable_icon.set_active(self.gconf.get_bool(GCONF_KEYS['icon']))

        self.find_keyring_items()
            
    def get_dialog(self):
        return self.dialog
        
    def close_button_pressed(self, dialog, response):
        if response != Gtk.ResponseType.CLOSE:
            return
        username = self.__builder.get_object("username").get_text()
        password = self.__builder.get_object("password").get_text()
        # TODO: Verify Account
        if self.__keyring_data['item']:
            self.__keyring_data['item'].set_secret('\n'.join((username, password)))
        GnomeKeyring.item_set_info_sync(None, self.__keyring_data['id'], self.__keyring_data['item'])

        enable_icon = self.__builder.get_object("enable_icon")
        enabled =enable_icon.get_active()
        self.gconf.set_bool(GCONF_KEYS['icon'], enabled)
        print "Setting to "
        print enabled

        dialog.hide()
        
        if self.callback:
            #gconf transaction is asynch
            self.callback(enabled)
    
    def fill_account_details(self):
        try:
            if self.__keyring_data['item']:
                username, password = self.__keyring_data['item'].get_secret().split('\n')
        except ValueError: # Couldn't parse the secret, probably because it's empty
            return
        self.__builder.get_object("username").set_text(username)
        self.__builder.get_object("password").set_text(password)
        
    def find_keyring_items(self):
        attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(attrs, 'rhythmbox-plugin', 'pandora')
        result, items = GnomeKeyring.find_items_sync(GnomeKeyring.ItemType.GENERIC_SECRET, attrs)

        if (result is None or result is GnomeKeyring.Result.OK) and len(items) != 0: # Got list of search results
            self.__keyring_data['id'] = items[0].item_id
            result, item = GnomeKeyring.item_get_info_sync(None, self.__keyring_data['id'])
            if result is None or result is GnomeKeyring.Result.OK: # Item retrieved successfully
                self.__keyring_data['item'] = item
                self.fill_account_details()
            else:
                print "Couldn't retrieve keyring item: " + str(result)
                
        elif result == GnomeKeyring.Result.NO_MATCH or len(items) == 0: # No items were found, so we'll create one
            result, id = GnomeKeyring.item_create_sync(
                                None,
                                GnomeKeyring.ItemType.GENERIC_SECRET,
                                "Rhythmbox: Pandora account information",
                                attrs,
                                "", # Empty secret for now
                                True)
            if result is None or result is GnomeKeyring.Result.OK: # Item successfully created
                self.__keyring_data['id'] = id
                result, item = GnomeKeyring.item_get_info_sync(None, id)
                if result is None: # Item retrieved successfully
                    self.__keyring_data['item'] = item
                    self.fill_account_details()
                else:
                    print "Couldn't retrieve keyring item: " + str(result)
            else:
                print "Couldn't create keyring item: " + str(result)
        else: # Some other error occurred
            print "Couldn't access keyring: " + str(result)

