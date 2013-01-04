
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

class SongsModel(RB.RhythmDBQueryModel):
    MAX = 20
    def __init__(self, db, entry_type):
        RB.RhythmDBQueryModel.__init__(self)
        self.__db = db
        self.__entry_type = entry_type
        self.__last_entry = None
        self.__songs_dict = {} # Map from url to song
        
    def add_song(self, song, duration=None):
        url = song.audioUrl
        entry = RB.RhythmDBEntry.new(self.__db, self.__entry_type, url)
        self.__db.entry_set(entry, RB.RhythmDBPropType.TITLE, str(song.title))
        self.__db.entry_set(entry, RB.RhythmDBPropType.ARTIST, str(song.artist))
        self.__db.entry_set(entry, RB.RhythmDBPropType.ALBUM, str(song.album))
        if duration != None:
            self.__db.entry_set(entry, RB.RhythmDBPropType.DURATION, duration/1000000000)
        if song.rating == 'love':
            self.__db.entry_keyword_add(entry, 'star')
        self.__db.commit()
        self.add_entry(entry, -1)
        self.__last_entry = entry
        
        self.__songs_dict[url] = song
        
        num_entries = self.get_num_entries()
        print "Number of entries: %d" %(num_entries)
             
        if num_entries > SongsModel.MAX:
            self.remove_old_songs()
        
        return entry
    
    def get_song(self, url):
        return self.__songs_dict[url]
    
    def is_last_entry(self, entry):
        return self.__last_entry == entry or self.__last_entry.get_playback_uri() == entry.get_playback_uri()
    
    def get_num_entries(self):
        return self.iter_n_children(None)
    
    def remove_old_songs(self, count = 4):
        removing = []
        if (self.get_num_entries() < count):
            return
        iter = self.get_iter_first()
        entry = self.iter_to_entry(iter)
        removing.append(entry)
        for i in range(count - 1):
            iter = self.iter_next(iter)
            entry = self.iter_to_entry(iter)
            removing.append(entry)
            
        #Remove from the model
        for removing_entry in removing:
            print "Removing Song %s" % (self.__db.entry_get(removing_entry, RB.RhythmDBPropType.TITLE))
            url = removing_entry.get_playback_uri()
            self.delete_song(url)
        self.__db.commit()
    
    def clear(self):
        num_entries = self.get_num_entries()
        if num_entries > 0:
            self.remove_old_songs(num_entries)
        self.__last_entry = None
    
    def delete_song(self, url):
        removing_entry = self.__db.entry_lookup_by_location(url)
        if self.is_last_entry(removing_entry):
            prev = self.get_previous_from_entry(removing_entry)
            if prev is not None:
                self.__last_entry = prev
        del self.__songs_dict[url]
        self.remove_entry(removing_entry)
        self.__db.entry_delete(removing_entry)
        self.__db.commit()
        
            
    #HACK around Python's QueryModel binding problem 
    def iter_to_entry(self, iter):
        db = self.__db
        id = self.get(iter, 0)[0]
        if not id:
            raise Exception('Bad id' + id)
  
        eid = db.entry_get(id, RB.RhythmDBPropType.ENTRY_ID)
        if not eid:
            raise Exception('Bad eid' + eid)
  
        entry = db.entry_lookup_by_id(eid)
  
        if not entry:
            raise Exception('iter_to_entry: bad entry ' + repr(eid) + ' ' + repr(id))

        return entry
