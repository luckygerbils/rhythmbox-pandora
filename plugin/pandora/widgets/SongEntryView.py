
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

import rb
from CellRendererStarButton import CellRendererStarButton

class SongEntryView(RB.EntryView):
    """Entry view for displaying the upcoming list of Pandora songs."""
    
    __gsignals__ = {
        'star': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                 (Gtk.TreeModel, Gtk.TreeIter)),
    }
    
    STAR_KEYWORD = RB.RefString.find('star') or RB.RefString.new('star')
    
    def __init__(self, db, player, plugin):
        RB.EntryView.__init__(self, db=db, shell_player=player)
        
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
        
        cell_renderer = CellRendererStarButton()
        cell_renderer.connect('clicked', self.on_star_click)
        
        column = Gtk.TreeViewColumn()
        column.pack_start(cell_renderer, True)
        column.set_cell_data_func(cell_renderer, self.set_star_cell_data)
        column.set_sizing (Gtk.TreeViewColumnSizing.FIXED)
        column.set_fixed_width(self.pixs[0].get_width() + 5)
        self.append_column_custom(column, "", "STAR", lambda x: x, lambda x: x)

        # column properties
        self.set_columns_clickable(False)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    
    def set_star_cell_data(self, column, cell, model, iter, other):
        """ Set the data stored for a cell.
        
        Args:
            column: the tree view column
            cell: the tree view cell
            model: the songs model
            iter: the songs model iter reference
            other: unused data argument
        """
        entry = model.get(iter, 0)[0]
        if self.has_star(entry):
            pixbuf = self.pixs[1]
        else:
            pixbuf = self.pixs[0]
        cell.set_property('pixbuf', pixbuf)

    def on_star_click(self, cell, model, path, iter):
        """ Star the song associated with the clicked cell.
        
        Args:
            cell: the tree view cell that was clicked
            model: the songs model
            path: Unknown
            iter: the songs model iter reference for the clicked song
        """
        entry = model.get(iter, 0)[0]
        if self.has_star(entry):
             # user cannot undo "Like Song"
            return
        else:
            self.add_star(entry)
        model.row_changed(Gtk.TreePath(path), iter)
        self.emit('star', model, iter)

    def has_star(self, entry):
        """ Returns: Whether the given entry has been starred or not. """
        return self.db.entry_keyword_has(entry, self.STAR_KEYWORD)

    def add_star(self, entry):
        """ Adds a star to the given entry. """
        self.db.entry_keyword_add(entry, self.STAR_KEYWORD)
        self.db.commit()

