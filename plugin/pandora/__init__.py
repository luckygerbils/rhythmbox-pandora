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
from gi.repository import RB
from gi.repository import Peas
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GdkPixbuf

import rb
import logging

import sys

from PandoraConfigureDialog import PandoraConfigureDialog
from PandoraSource import PandoraSource

class ConsoleHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        print self.format(record)

logging.getLogger().addHandler(ConsoleHandler())
logging.getLogger().setLevel(logging.WARN)

class PandoraPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'PandoraPlugin'
    object = GObject.property(type=GObject.Object)
    
    def __init__(self):
        super(PandoraPlugin, self).__init__()
    
    def do_activate(self):
        """Activate the pandora plugin. Called when checked within the Rhythmbox plugin pane."""
        print "Activating pandora plugin."
        
        shell = self.object
        db = shell.props.db
        entry_type = PandoraEntryType()
        db.register_entry_type(entry_type)
        
        _, width, height = Gtk.icon_size_lookup(Gtk.IconSize.LARGE_TOOLBAR)
        pandora_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(rb.find_plugin_file(self, "pandora.png"), width, height)
        
        self.source = GObject.new(
            PandoraSource,
            shell=shell,
            name="Pandora",
            plugin=self,
            pixbuf=pandora_icon,
            entry_type=entry_type)
        library_group = RB.DisplayPageGroup.get_by_id("library")
        shell.append_display_page(self.source, library_group)
        shell.register_entry_type_for_source(self.source, entry_type)

        # hack, should be done within gobject constructor
        self.source.init();
        
        self.pec_id = shell.props.shell_player.connect_after('playing-song-changed', self.playing_entry_changed)
        self.psc_id = shell.props.shell_player.connect_after('playing-source-changed', self.playing_source_changed)

    def do_deactivate(self):
        """Deactivate the Pandora plugin. Called when unchecked within the Rhythmbox plugin pane."""
        print "Deactivating pandora plugin."
        shell = self.object
        shell.props.shell_player.disconnect (self.pec_id)
        shell.props.shell_player.disconnect (self.psc_id)
        self.source.delete_thyself()
        self.source = None
        
    def create_configure_dialog(self, dialog=None, callback=None):
        def dialog_closed_callback(icon_enabled):
            self.source.refresh_notification_icon(icon_enabled)
            if callback:
                callback()

        if not dialog:
            builder_file = rb.find_plugin_file(self, "pandora-prefs.ui")
            dialog_wrapper = PandoraConfigureDialog(builder_file, dialog_closed_callback)
            dialog = dialog_wrapper.get_dialog()
        dialog.present()
        return dialog

    def playing_entry_changed(self, sp, entry):
        self.source.playing_entry_changed(entry)

    def playing_source_changed(self, player, source):
        self.source.playing_source_changed(source)

class PandoraEntryType(RB.RhythmDBEntryType):
    def __init__(self):
        RB.RhythmDBEntryType.__init__(self, name='PandoraEntryType')

