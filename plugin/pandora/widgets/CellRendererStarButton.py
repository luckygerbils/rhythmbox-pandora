"""
  rhythmbox-shoutcast plugin for rhythmbox application.
  Copyright (C) 2009  Alexey Kuznetsov <ak@axet.ru>
  
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
from gi.repository import GObject
from gi.repository import GdkPixbuf

class CellRendererStarButton(Gtk.CellRendererPixbuf):
  __gsignals__ = {
      'clicked': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                  (Gtk.TreeModel, str, Gtk.TreeIter)),
  }

  def __init__(self):
    Gtk.CellRendererPixbuf.__init__(self)
    self.set_property('mode', Gtk.CellRendererMode.ACTIVATABLE)

  def do_activate(self, event, widget, path, background_area, cell_area, flags):
    """ React to activation of this cell (via click)."""
    model = widget.get_model()
    iter = model.get_iter(path)
    self.emit('clicked', model, path, iter)
    return True

GObject.type_register(CellRendererStarButton)

