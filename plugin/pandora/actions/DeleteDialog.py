
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

from gi.repository import Gtk

import rb

def NewDeleteDialog(plugin):
    ui_filename = rb.find_plugin_file(plugin, "pandora/actions/DeleteDialog.ui")

    builder = Gtk.Builder()
    builder.add_from_file(ui_filename)    
    dialog = builder.get_object("delete_confirm_dialog")
    return dialog
