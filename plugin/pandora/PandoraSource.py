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

"""
  The author would like to extend thanks to Kevin Mehall, author of Pithos,
  an standalone Pandora player written in python, the code of which was
  extraordinarily useful in the creation of this code
"""
from gi.repository import RB
from gi.repository import GObject
from gi.repository import GConf
from gi.repository import Gtk
from gi.repository import GnomeKeyring
from gi.repository import Gst

from time import time
from time import sleep

from pithos.pandora import *;
from pithos.gobject_worker import GObjectWorker

from models import StationsModel
from models import SongsModel

from actions import SongsAction
from actions import StationsAction

from notification_icon import NotificationIcon

import rb
import widgets

GCONF_DIR = '/apps/rhythmbox/plugins/pandora'

GCONF_KEYS = {
        'icon': GCONF_DIR + '/icon'
}

class PandoraSource(RB.StreamingSource):
#    __gproperties__ = {
#            'plugin': (rb.Plugin,
#            'plugin',
#            'plugin',
#            gobject.PARAM_WRITABLE | gobject.PARAM_CONSTRUCT_ONLY)
#    }
      
    def __init__(self):
        RB.StreamingSource.__init__(self,name="PandoraPlugin")
        
    def init(self):
        self.__activated = False
        self.__shell = self.props.shell
        self.__db = self.__shell.props.db
        self.__player = self.__shell.props.shell_player
        self.__plugin = self.props.plugin
        self.__entry_type = self.props.entry_type

        self.gconf = GConf.Client.get_default()
        self.vbox_main = None
        
        self.create_window()
        self.create_popups()
        
        # Pandora
        self.pandora = make_pandora()
        self.worker = GObjectWorker()
        
        self.stations_model = StationsModel(self.__db, self.__entry_type)
        self.songs_model = SongsModel(self.__db, self.__entry_type)
        self.songs_list.set_model(self.songs_model)
        self.props.query_model = self.songs_model # Enables skipping
        
        self.current_station = None
        self.current_song = None
        self.connected = False
        self.request_outstanding = False
        
        self.songs_action = SongsAction(self)
        self.stations_action = StationsAction(self, self.__plugin)
        
        self.notification_icon = NotificationIcon(self.__plugin, self.songs_action)
        self.refresh_notification_icon()
        
        self.connect_all()

        self.retrying = False
        self.waiting_for_playlist = False

    def refresh_notification_icon(self, icon_enabled = None):
        if icon_enabled:
            enabled = icon_enabled
        else:
            enabled = self.gconf.get_bool(GCONF_KEYS['icon'])

        if enabled and self.__player.get_playing_source() == self:
            self.notification_icon.show()
        else:
            self.notification_icon.hide()
            
    def do_selected(self):
        print "do_selected"

    def do_get_status(self, *args):
        """Return the current status of the Pandora source.
        
        Called by Rhythmbox to figure out what to show on the statusbar.
        
        Args:
            args: Unknown
        
        Returns:
            A tuple of:
                the text status to display
                the status to display on the progress bar
                the progress value, if the progress value is less than zero, the progress bar will pulse.
        """
        progress_text = None
        progress = 1
        text = ""

        if self.connected:
            self.error_area.hide()
            num_stations = self.stations_model.get_num_entries()
            if num_stations > 1:
                text =  str(num_stations) + " stations"
            else:
                text =  str(num_stations) + " station"
        else:
            text = "Not connected to Pandora"

        # Display Current Station Info
        if self.__player.get_playing() and self.__player.get_playing_source() == self:
            station_name = self.current_station.name
            text = "Playing " + station_name + ", " + text 
        if self.request_outstanding:
            progress_text = self.request_description
            progress = -1
        return (text, progress_text, progress)

    def do_impl_get_entry_view(self):
        print "do_impl_get_entry_view"
        return self.songs_list

    def do_impl_can_pause(self):
        """Indicate that pausing of source entries is available.
        
        Called by Rhythmbox to determine whether playback of entries from the source can be paused.
        
        Returns:
            True to indicate the pausing is supported.
        """
        return True

    def do_impl_handle_eos(self):
        """Handle End Of Stream event by going to the next song.
        
        Called by Rhythmbox to handle EOS events when playing entries from this source.
        
        Returns:
            The source EOF type indicating to skip to the next song.
        """
        return RB.SourceEOFType(3) # next

    def do_impl_try_playlist(self):
        """Don't try to parse playback URIs in this source as playlists.
        
        Called by Rhythmbox to determine if URIs should be parsed as playlists rather than just played.
        
        Returns:
            False to disable playlist parsing.
        """
        return False

    def do_songs_show_popup(self, view, over_entry):
        if over_entry:
            selected = view.get_selected_entries()
            if len(selected) == 1:
                self.show_single_popup("/PandoraSongViewPopup")

    def do_stations_show_popup(self, view, over_entry):
        if over_entry:
            selected = view.get_selected_entries()
            if len(selected) == 1:
                self.show_single_popup("/PandoraStationViewPopup")
        else:
            self.show_single_popup("/PandoraSourceMainPopup")

    def show_single_popup(self, popup):
        popup = self.__player.props.ui_manager.get_widget(popup)
        popup.popup(None, None, None, None, 3, Gtk.get_current_event_time())

    def playing_source_changed(self, source):
        print "Playing source changed"
        if not self.notification_icon:
            return
        if self != source:
            self.notification_icon.hide()
        else:
            self.notification_icon.show()

    def playing_entry_changed(self, entry):
        print "Playing Entry changed"
        if not self.__db or not entry:
            return
        if entry.get_entry_type() != self.__entry_type:
            return
        self.get_metadata(entry)

        url = entry.get_playback_uri()
        
        self.current_song = self.songs_model.get_song(url)
        if self.songs_model.is_last_entry(entry):
            self.get_playlist()

    def create_window(self):
        if self.vbox_main:
            self.remove(self.vbox_main)
            self.vbox_main.hide_all()
            self.vbox_main = None

        self.stations_list = widgets.StationEntryView(self.__db, self.__player)
        self.songs_list = widgets.SongEntryView(self.__db, self.__player, self.__plugin)
        
        self.vbox_main = Gtk.VBox(False, 5)

        paned = Gtk.VPaned()
        frame1 = Gtk.Frame()
        frame1.set_shadow_type(Gtk.ShadowType.OUT)
        frame1.add(self.stations_list)
        paned.pack1(frame1, True, False)
        frame2 = Gtk.Frame()
        frame2.set_shadow_type(Gtk.ShadowType.OUT)
        frame2.add(self.songs_list)
        paned.pack2(frame2, True, False)
        self.vbox_main.pack_start(paned, True, True, 0)
 
        self.error_area = widgets.ErrorView(self.__plugin, self.do_impl_activate)
        error_frame = self.error_area.get_error_frame()
        self.vbox_main.pack_end(error_frame, False, False, 0)
 
        self.vbox_main.show_all()
        self.error_area.hide()
        self.add(self.vbox_main)


    def connect_all(self):
        self.stations_list.connect('show_popup', self.do_stations_show_popup)
        self.songs_list.connect('show_popup', self.do_songs_show_popup)
        self.songs_action.connect()
        self.stations_action.connect()


    def create_popups(self):
        self.action_group = Gtk.ActionGroup('PandoraPluginActions')
        action = Gtk.Action('SongInfo', _('Song Info...'), _('View song information in browser'), 'gtk-info')
        self.action_group.add_action(action)
        action = Gtk.Action('LoveSong', _('Love Song'), _('I love this song'), 'gtk-about')
        self.action_group.add_action(action)
        action = Gtk.Action('BanSong', _('Ban Song'), _("I don't like this song"), 'gtk-cancel')
        self.action_group.add_action(action)
        action = Gtk.Action('TiredSong', _('Tired of this song'), _("I'm tired of this song"), 'gtk-jump-to')
        self.action_group.add_action(action)
        action = Gtk.Action('Bookmark', _('Bookmark'), _('Bookmark...'), 'gtk-add')
        self.action_group.add_action(action)
        action = Gtk.Action('BookmarkSong', _('Song'), _("Bookmark this song"), None)
        self.action_group.add_action(action)
        action = Gtk.Action('BookmarkArtist', _('Artist'), _("Bookmark this artist"), None)
        self.action_group.add_action(action)

        action = Gtk.Action('AddStation', _('Create a New Station'), _('Create a new Pandora station'), 'gtk-add')
        self.action_group.add_action(action)

        action = Gtk.Action('StationInfo', _('Station Info...'), _('View station information in browser'), 'gtk-info')
        self.action_group.add_action(action)
        action = Gtk.Action('DeleteStation', _('Delete this Station'), _('Delete this Pandora Station'), 'gtk-remove')
        self.action_group.add_action(action)

        manager = self.__player.props.ui_manager
        manager.insert_action_group(self.action_group, 0)
        popup_file = rb.find_plugin_file(self.__plugin, "pandora/pandora-ui.xml")
        self.ui_id = manager.add_ui_from_file(popup_file)
        manager.ensure_update()

     # rhyhtmbox api break up (0.13.2 - 0.13.3)   
    def do_selected(self):
        print "Activating source."
        if not self.__activated:
            try:
                self.username, self.password = self.get_pandora_account_info()
            except AccountNotSetException, (instance):
                # Ask user to configure account
                self.error_area.show(instance.parameter)
                # Retry after the user has put in account information.
                return
            
            self.pandora_connect()
            
            self.__activated = True

    def do_impl_activate(self):
        self.do_selected()

    # TODO: Update UI and Error Msg
    def worker_run(self, fn, args=(), callback=None, message=None, context='net'):
        print "worker_run"
        self.request_outstanding = True
        self.request_description = message
        self.notify_status_changed()

        if isinstance(fn,str):
            fn = getattr(self.pandora, fn)

        def cb(v):
            self.request_outstanding = False
            self.request_description = None
            self.notify_status_changed()
            if callback: callback(v)

        def eb(e):
                
            def retry_cb():
                self.retrying = False
                if fn is not self.pandora.connect:
                    self.worker_run(fn, args, callback, message, context)
            
            self.request_outstanding = False
            self.request_description = None 
            self.waiting_for_playlist = False
            self.connected = False
            self.notify_status_changed()

            if isinstance(e, PandoraAuthTokenInvalid) and not self.retrying:
                self.retrying = True
                print "Automatic reconnect after invalid auth token"
                self.pandora_connect("Reconnecting...", retry_cb)
            elif isinstance(e, PandoraNetError):
                error_message = "Unable to connect. Check your Internet connection."
                detail = e.message
                self.__activated = False
                self.error_area.show(error_message, detail)
                print e.message
            elif isinstance(e, PandoraError):
                error_message = e.message
                self.__activated = False
                self.error_area.show(error_message)
                print "Pandora returned error: ", e.message
            else:
                print e.traceback
                
        self.worker.send(fn, args, cb, eb)

    def get_pandora_account_info(self):
        print "Getting account details..."
        
        error_message = "Account details are needed before you can connect.  Check your settings."
        
        attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(attrs, 'rhythmbox-plugin', 'pandora')
        result, items = GnomeKeyring.find_items_sync(GnomeKeyring.ItemType.GENERIC_SECRET, attrs)
        
        if result == GnomeKeyring.Result.NO_MATCH or len(items) == 0:
            print "Pandora Account Info not found."
            raise AccountNotSetException(error_message)

        secret = items[0].secret
        if secret is "":
            print "Pandora Account Info empty."
            raise AccountNotSetException(error_message)
        return tuple(secret.split('\n'))


    def pandora_connect(self, message="Logging in...", callback=None):
        args = (self.username, self.password)

        def pandora_ready(*ignore):
            print "Pandora connected."
            self.stations_model.clear()

            #TODO: Station already exists
            #FIXME: Leave out QuickMix for now
            #for i in self.pandora.stations:
            #    if i.isQuickMix:
            #        self.stations_model.add_station(i, "QuickMix")
            
            for station in self.pandora.stations:
                if not station.isQuickMix:
                    self.stations_model.add_station(station, station.name)
            self.stations_list.set_model(self.stations_model)
            self.connected = True
            if callback:
                callback()

        self.worker_run('connect', args, pandora_ready, message, 'login')

    def play_station(self, station_entry):
        prev_station = self.current_station

        url = station_entry.get_playback_uri()
        self.current_station = self.stations_model.get_station(url)

        if prev_station != None and prev_station != self.current_station:
            self.songs_model.clear()

        self.get_playlist(start = True)
        print "Station activated %s" %(url)

        now = int(time.time())
        self.__db.entry_set(station_entry, RB.RhythmDBPropType.LAST_PLAYED, now)
        self.__db.commit()

    def get_playlist(self, start = False):
        print "Getting playlist"

        if self.waiting_for_playlist: return

        def callback(songs):
            print "Got playlist"
            first_entry = None
            for song in songs:
                entry = self.songs_model.add_song(song)
                if first_entry == None:
                    first_entry = entry
                print "Title: %s" %(song.title)
                print "URL: %s" %(song.audioUrl)
            self.waiting_for_playlist = False
            if start:
                self.songs_list.scroll_to_entry(first_entry)
                self.__player.play_entry(first_entry, self)

        self.waiting_for_playlist = True
        self.worker_run(self.current_station.get_playlist, (), callback, "Getting songs...")

    def get_metadata(self, entry):
        if entry == None:
            print "Track not found in DB"
            return True
        duration = Gst.CLOCK_TIME_NONE
        try:
            sleep(1) # FIXME: Hack, but seems to be returning 0 immediately after the playing-song-changed signal
            query_success, format, duration_nanos = self.__player.props.player.props.playbin.query_duration(Gst.Format.TIME)
            if query_success and duration_nanos != Gst.CLOCK_TIME_NONE:
                duration_seconds = duration_nanos / 1000000000
                self.__db.entry_set(entry, RB.RhythmDBPropType.DURATION, duration_seconds)
                self.__db.commit()
            
        except Exception,e:
            print "Could not query duration"
            print e
            pass
    
    def get_progress(text, progress):
        print "get_progress"
    
    def get_current_song_entry(self):
        return self.__player.get_playing_entry()

    def next_song(self):
        print "next_song"
        self.__player.do_next()

    def is_current_song(self, song):
        return song is self.current_song

    def is_current_station(self, station):
        return station is self.current_station

GObject.type_register(PandoraSource)

class AccountNotSetException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

