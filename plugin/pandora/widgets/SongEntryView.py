
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
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GObject

from cellpixbufbutton import *
import rb

class SongEntryView(RB.EntryView):
    __gsignals__ = {
        'star': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                 (Gtk.TreeModel, Gtk.TreeIter)),
    }
    
    def __init__(self, db, player, plugin):
        RB.EntryView.__init__(self, None, None)
        
        self.db = db
        self.plugin = plugin

        self.pixs = [GdkPixbuf.Pixbuf.new_from_file(rb.find_plugin_file(self.plugin, 'pandora/widgets/star-off.png')),
                     GdkPixbuf.Pixbuf.new_from_file(rb.find_plugin_file(self.plugin, 'pandora/widgets/star-on.png'))]

        self.load_columns()
        
        
    def load_columns(self):
        self.append_column(RB.EntryViewColumn.TITLE, True)
        self.append_column(RB.EntryViewColumn.ARTIST, True)
        self.append_column(RB.EntryViewColumn.ALBUM, True)
        self.append_column(RB.EntryViewColumn.DURATION, True)

        cell_render = CellPixbufButton()
        cell_render.connect('clicked', self.star_click)
        column = Gtk.TreeViewColumn()
        column.pack_start(cell_render, True)
        column.set_cell_data_func(cell_render, self.star_func)
        #column.set_sizing (Gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(self.pixs[0].get_width() + 5)
        self.append_column_custom(column, "", "STAR", lambda x: x, lambda x: x)

        # column properties
        self.set_columns_clickable(False)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    
    def star_func(self, column, cell, model, iter):
        print "Star func called."
#        entry = model.iter_to_entry(iter)
#        star = self.has_star(entry)

#        if star:
#            pixbuf = self.pixs[1]
#        else:
#            pixbuf = self.pixs[0]

#        cell.set_property('pixbuf', pixbuf)
#        
#        
    def star_click(self, cell, model, path, iter):
        print "Clicked star."
#        entry = model.iter_to_entry(iter)
#        star = self.has_star(entry)
#        if star:
#            # user cannot undo "Like Song"
#            return
#        else:
#            self.add_star(entry)
#        
#        self.db.commit()
#        model.row_changed(path, iter)
#        print "Clicked star"
#    
#        self.emit('star', model, iter)
#        
#    def has_star(self, entry):
#        return self.db.entry_keyword_has(entry, 'star')
#    
#    def add_star(self, entry):
#        self.db.entry_keyword_add(entry, 'star')
        
