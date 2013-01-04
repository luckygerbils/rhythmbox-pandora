
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

class StationEntryView(RB.EntryView):
    def __init__(self, db, player):
        RB.EntryView.__init__(self, None, None)
        self.load_columns()
    
    def load_columns(self):
        self.append_column(RB.EntryViewColumn.TITLE, True)
        self.append_column(RB.EntryViewColumn.LAST_PLAYED, True)
        
        # column properties
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
