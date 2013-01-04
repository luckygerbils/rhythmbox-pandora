
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

class StationsModel(RB.RhythmDBQueryModel):
    def __init__(self, db, entry_type):
        RB.RhythmDBQueryModel.__init__(self)
        self.__db = db
        self.__entry_type = entry_type
        self.__stations_dict = {}
        
        
    def add_station(self, station, name, pos=-1):
        url = station.info_url
        
        entry = RB.RhythmDBEntry.new(self.__db, self.__entry_type, url)
        self.__db.entry_set(entry, RB.RhythmDBPropType.TITLE, str(name))
        self.__db.commit()

        self.add_entry(entry, pos)
        self.__stations_dict[url] = station
        
        return entry
    
    def get_station(self, url):
        print "Number of stations: %d" %(len(self.__stations_dict))
        return self.__stations_dict[url] 
    
    def delete_station(self, url):
        entry = self.__db.entry_lookup_by_location(url)
        self.__db.entry_delete(entry)
        self.remove_entry(entry)
        del self.__stations_dict[url]
        
    def clear(self):
        for url in self.__stations_dict.keys():
            entry = self.__db.entry_lookup_by_location(url)
            self.__db.entry_delete(entry)
            self.remove_entry(entry)
        self.__stations_dict.clear()
    
    def get_num_entries(self):
        return self.iter_n_children(None)
    
    # Get the first station after "QuickMix"
    def get_first_station(self):
        iter = self.get_iter_first()
        #iter = self.iter_next(iter)
        entry = self.iter_to_entry(iter)
        return entry
        
    #HACK around Python's QueryModel binding problem 
    def iter_to_entry(self, iter):
        db = self.__db
        id = self.get(iter, 0)[0]
        if not id:
            raise Exception('Bad id' + id)
  
        eid = db.entry_get(id, rhythmdb.PROP_ENTRY_ID)
        if not eid:
            raise Exception('Bad eid' + eid)
  
        entry = db.entry_lookup_by_id(eid)
  
        if not entry:
            raise Exception('iter_to_entry: bad entry ' + repr(eid) + ' ' + repr(id))

        return entry
