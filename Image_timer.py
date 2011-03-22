# -*- coding: utf-8 -*-

#   This file is part of emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import gtk
import gobject
import random
import string
import Plugin

class MainClass( Plugin.Plugin ):
    description = _('Every time interval, picks an image from a selected folder.V 0.2b')
    authors = { 'liuggio' : 'liuggio YAHOO' }
    website = ''
    displayName = _('Image Timer')
    name = 'Image_Timer'
    
    def __init__( self, controller, msn ):
        Plugin.Plugin.__init__( self, controller, msn )

        self.description = _('Every time interval, picks an image from a selected folder.V 0.2')
        self.authors = { 'liuggio' : 'liuggio YAHOO' }
        self.website = ''
        self.displayName = _('Image Timer')
        self.name = 'Image_Timer'
        self.config = controller.config
        self.config.readPluginConfig(self.name)
        #Fixed by marramao @ emesene forum
        self.controller = controller
        self.checking = False
        self.thedir = self.config.getPluginValue( self.name, 'user_folder', self.controller.config.getAvatarsCachePath() )
        self.random=bool(int(self.config.getPluginValue(self.name, "random", False)))
        self.order=bool(int(self.config.getPluginValue(self.name, "order", False)))
        self.Indexoflist=-1
        self.recursive =1

    def start( self ):
        self.enabled = True
        self.source_id =0
        ''' list of all file in the directory  not(yet) RECURSIVE  '''
        if self.recursive>0:
            self.imagefilenames=[f for f in os.listdir(self.thedir) if ( os.path.isfile(os.path.join(self.thedir, f)) and ( string.lower(f).endswith('.jpg') or string.lower(f).endswith('.gif') or    string.lower(f).endswith('.png')    or string.lower(f).endswith('.bmp') ) )]
            if self.order:
                self.imagefilenames.sort(reverse=True)
                print self.name + " : order by DESC "
            else:
                self.imagefilenames.sort()
                print self.name + " : order by ASC "
            self.imagedirlen=len(self.imagefilenames)
            #for index, item in enumerate(self.imagefilenames):
            #	print index, item
            print "Loaded " + str(self.imagedirlen) + "files"		
            if self.imagedirlen>0:
                self.Image_Timer(0)
                self.interval = 1000*int(self.config.getPluginValue( self.name, 'time', '20' ))
                self.source_id = gobject.timeout_add(self.interval, self.Image_Timer, 0)
            else:
                print self.name + " : ("+self.thedir+") dir is empty "
                        

    
    def Image_Timer( self ,  data=0):
        if data is None:
            data = 0     
        self.imagedirlen=len(self.imagefilenames)
        ''' check if list is not empty '''
        if self.imagedirlen>0:
            if self.random:
                #random choice
                element = random.choice(self.imagefilenames)
            else: 
                #sequential choice  
                self.Indexoflist=self.Indexoflist+1
                if self.imagedirlen<=self.Indexoflist:           
                    self.Indexoflist=0      
                element=self.imagefilenames[self.Indexoflist]
            nimg=string.lower(element)
            '''only if jpg/gif/png/bmp '''
            pa=os.path.join(self.thedir,element)
            try:
                self.controller.changeAvatar(pa)
            except:
                print self.name + " : changeAvatar failure " + nimg + " index:" + str(self.Indexoflist)
                self.imagefilenames.remove(element)
                #print len(self.imagefilenames)
                return self.Image_Timer( data+1 )
            else:
                print self.name + " : Avatar changed " + nimg + " index:" + str(self.Indexoflist)
                return True
        else:
            print self.name + " : Folder doesn't not has images  "
            self.stop()
            return False 
      
   
    def stop( self ):
        self.enabled = False
        gobject.source_remove(self.source_id)

    def check( self ):
        return ( True, 'Ok' )

    def configure( self ):
        dataM = []
        dataM.append(Plugin.Option('time', str, _('Change every [sec]:'), '',\
            self.config.getPluginValue( self.name, 'time', '20' )) )
        dataM.append( Plugin.Option( 'user_folder', str, 'Image folder:', '',\
            self.config.getPluginValue( self.name, 'user_folder',self.controller.config.getAvatarsCachePath())) )
        dataM.append(Plugin.Option("random", bool, "Random ?", \
            '', bool(int(self.config.getPluginValue(self.name, "random", False)))))
        dataM.append(Plugin.Option("order", bool, "Order files descending ?", \
            '', bool(int(self.config.getPluginValue(self.name, "order", False)))))

        self.confW = Plugin.ConfigWindow(_('Image Timer config'), dataM)
        
        r = self.confW.run()
        
        if r is not None:
            needtostart=0
            OLDt=self.config.getPluginValue( self.name, 'time', '20' )
            OLDuf=self.config.getPluginValue( self.name, 'user_folder',self.controller.config.getAvatarsCachePath())
            OLDrnd=bool(int(self.config.getPluginValue(self.name, "random", False)))
            OLDord=bool(int(self.config.getPluginValue(self.name, "order", False)))

            if(OLDt != r['time'].value or OLDuf != r['user_folder'].value) or OLDrnd!=r['random'].value or OLDord!=r['order'].value:
                needtostart=1
            
            if (r['random'].value and r['order'].value):
                if ((not OLDrnd) and (not OLDord)):
                	r['random'].value=False
                if ((OLDrnd) and (OLDord)):
                	r['random'].value=False
                if ((OLDrnd) and (not OLDord)):
                	r['random'].value=False
                if ((not OLDrnd) and (OLDord)):
                	r['order'].value=False

            if (OLDord!=r['order'].value):
                self.Indexoflist=0
                self.order=r['order'].value

            self.config.setPluginValue(self.name, 'time', r['time'].value)
            self.config.setPluginValue(self.name, 'user_folder', r['user_folder'].value)
            self.config.setPluginValue(self.name, 'random', str(int(r['random'].value)) )
            self.config.setPluginValue( self.name, 'order', str(int(r['order'].value)) )

            if (needtostart>0):
                print self.name + " : restarting  "
                self.thedir = self.config.getPluginValue( self.name, 'user_folder',\
		    self.controller.config.getAvatarsCachePath() )
		self.random=r['random'].value;
		if not self.random:
		    self.Indexoflist=0;		    
		self.stop()
		self.start()
	    return True
