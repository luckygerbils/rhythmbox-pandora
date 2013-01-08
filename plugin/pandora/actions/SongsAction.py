
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

import webbrowser
from pithos.pandora import *;

class SongsAction(object):
    def __init__(self, pandora_source):
        self.source = pandora_source
        self.songs_list = pandora_source.songs_list
        self.songs_model = pandora_source.songs_model
        self.worker_run = pandora_source.worker_run
        self.action_group = pandora_source.action_group
    
    def connect(self):
        self.songs_list.connect('entry-activated', self.song_activated_cb)
        self.songs_list.connect('star', self.do_star_clicked)
        
        action = self.action_group.get_action('SongInfo')
        action.connect('activate', self.view_song_info)
        action = self.action_group.get_action('LoveSong')
        action.connect('activate', self.love_selected_song)
        action = self.action_group.get_action('BanSong')
        action.connect('activate', self.ban_selected_song)
        action = self.action_group.get_action('TiredSong')
        action.connect('activate', self.tired_selected_song)
        action = self.action_group.get_action('BookmarkSong')
        action.connect('activate', self.bookmark_song)
        action = self.action_group.get_action('BookmarkArtist')
        action.connect('activate', self.bookmark_artist)
    
    def song_activated_cb(self, entry_view, song_entry):
        print "Song activated"
        url = song_entry.get_playback_uri()

    def do_star_clicked(self, entryview, model, iter):
        entry = model.iter_to_entry(iter)
        self.love_song(entry) 
        
    def view_song_info(self, *args):
        song = self.selected_song()
        webbrowser.open(song.songDetailURL)
        
    def selected_song(self):
        selected = self.songs_list.get_selected_entries()
        entry = selected[0]
        url = entry.get_playback_uri()
        song = self.songs_model.get_song(url)
        return song

     # Love song

    def love_song(self, entry):
        url = entry.get_playback_uri()
        song = self.songs_model.get_song(url) 
        def callback(l):
            print "Loved song: %s " %(song.title)
        self.worker_run(song.rate, (pandora.RATE_LOVE,), callback, "Loving song...")

    def love_current_song(self):
        entry = self.source.get_current_song_entry()
        if entry:
            self.songs_list.add_star(entry)
            self.love_song(entry)

    def love_selected_song(self, *args):
        selected = self.songs_list.get_selected_entries()
        for entry in selected:
            if not self.songs_list.has_star(entry):
                self.songs_list.add_star(entry)
                self.love_song(entry)

    # Ban song
    def ban_song(self, song):
        self.delete_song(song)
        def callback(l):
            print "Banned song: %s " %(song.title)
        self.worker_run(song.rate, (pandora.RATE_BAN,), callback, "Banning song...")        
        
    def ban_current_song(self):
        song = self.source.current_song;
        if song:
                self.ban_song(song)        

    def ban_selected_song(self, *args):
        song = self.selected_song()
        self.ban_song(song)
    
    # Tire song
    def tire_song(self, song):
        self.delete_song(song)
        def callback(l):
            print "Tired of song: %s " %(song.title)
        self.worker_run(song.set_tired, (), callback, "Putting song on shelf...")
    
    def tire_current_song(self):
        song = self.source.current_song;
        if song:
            self.tire_song(song)
        
    def tired_selected_song(self, *args):
        song = self.selected_song()
        self.tire_song(song)
        
    def delete_song(self, song):
        url = song.audioUrl
        if self.source.is_current_song(song):
            self.source.next_song()
        # Remove from playlist
        self.songs_model.delete_song(url) 
    
    def bookmark_song(self, *args):
        song = self.selected_song()
        self.worker_run(song.bookmark, (), None, "Bookmarking...")
        print "Bookmarked song: %s" %(song.title)
    
    def bookmark_artist(self, *args):
        song = self.selected_song()
        self.worker_run(song.bookmark_artist, (), None, "Bookmarking...")
        print "Bookmarked artist: %s" %(song.artist)

