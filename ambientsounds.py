#!/usr/bin/env python2

# Copyright (c) 2014-2015 Muges
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygame
pygame.mixer.init(frequency=48000)

import curses
import os.path
import traceback
from mutagen.oggvorbis import OggVorbis

class Volume:
    """
    Abstract class, used to represent a named object whose volume can
    be changed
    """
    def __init__(self, name, volume=0):
        self.volume = volume
        self.name = name

    def get_volume(self):
        return self.volume

    def _set_volume(self):
        """
        Method that should be implemented by the subclasses, which
        actually sets the volume (for example set the volume of a pygame
        sound)
        """
        raise NotImplementedError()

    def set_volume(self, volume):
        """
        Set the volument
        """
        self.volume = min(max(0, volume), 100)
        self._set_volume()

    def inc_volume(self, step):
        """
        Increment the volume (or decrement it, the step may be
        negative)
        """
        self.set_volume(self.volume+step)

class Sound(Volume):
    def __init__(self, filename, mastervolume):
        self.filename = filename

        # Read the title in the ogg vorbis tags
        tags = OggVorbis(filename)
        try:
            name = tags["title"][0]
        except KeyError:
            basename = os.path.basename(filename)
            name, ext = os.path.splitext(basename)
        Volume.__init__(self, name)

        # Link with the MasterVolume object
        self.mastervolume = mastervolume
        self.mastervolume.add_sound(self)
        
        self.sound = None
        
    def _set_volume(self):
        if self.sound == None:
            # Load the sound
            self.sound = pygame.mixer.Sound(self.filename)
            self.sound.play(-1)
            
        self.sound.set_volume((self.mastervolume.get_volume()*self.get_volume())/10000.)

class MasterVolume(Volume):
    def __init__(self):
        Volume.__init__(self, "Volume", 100)
        self.sounds = []

    def add_sound(self, sound):
        """
        Add a sound that will be controlled by the master volume
        """
        self.sounds.append(sound)

    def _set_volume(self):
        """
        Update the volume of all the sounds
        """
        for sound in self.sounds:
            sound._set_volume()

class UI:
    def __init__(self):
        # Horizontal and vertical padding (space between the edge of the
        # terminal and the text)
        self.hpadding = 5
        self.vpadding = 3

        # Width taken by the track titles
        self.namesw = 0

        # Width taken by the volume slider
        self.slidew = 0

        self.selection = 1

    def start(self):
        """
        Start the application
        """
        # Initialize curses
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        curses.curs_set(0)

        self.resize()

        # Display loading text
        text = "Loading sounds..."
        x = (self.screenw-len(text))/2
        y = self.screenh/2
        self.screen.addstr(y, x, text)
        self.screen.refresh()

    def end(self):
        # End curses
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def resize(self):
        # Set some constants depending on the screen size
        self.screenh, self.screenw = self.screen.getmaxyx()
        self.slidex = self.hpadding+self.namesw+5
        self.slidew = self.screenw-2*self.hpadding-self.namesw-6

    def create_volume_slider(self, y, sound, index):
        # Display the name of the sound
        if index == self.selection:
            # Highlight the name of the selected track
            attribute = curses.A_REVERSE
        else:
            attribute = 0
        self.screen.addstr(self.vpadding+y, self.hpadding, " "+sound.name+" ", attribute)

        # Draw a volume slider : [ ####----- ]
        self.screen.addstr(self.vpadding+y, self.slidex - 2, "[ ")
        self.screen.addstr(self.vpadding+y, self.slidex + self.slidew, " ]")

        slidewleft = (sound.get_volume()*self.slidew)/100
        slidewright = self.slidew - slidewleft
        self.screen.addstr(self.vpadding+y, self.slidex, "#"*slidewleft)
        self.screen.addstr(self.vpadding+y, self.slidex+slidewleft, "-"*slidewright)        

    def update(self):
        self.screen.clear()

        # Draw the master volume slider
        self.create_volume_slider(0, self.mastervolume, 0)

        # Draw a slider for each sound
        index = 1
        for s in self.sounds:
            self.create_volume_slider(index+1, s, index)
            index += 1

        self.screen.refresh()

    def getSelection(self):
        """
        Return the Volume object that is currently selected
        """
        if self.selection == 0:
            return self.mastervolume
        else:
            return self.sounds[self.selection-1]

    def run(self, mastervolume, sounds):
        self.mastervolume = mastervolume
        
        self.sounds = sounds        
        self.namesw = max(max([len(s.name) for s in self.sounds]), len(self.mastervolume.name))
        self.resize()

        self.update()

        while True:
            # Wait for user input
            c = self.screen.getch()
            if c == ord('q'):
                # Quit
                self.end()
                break
            elif c == curses.KEY_DOWN:
                # Select the next volume slider
                if self.selection < len(self.sounds):
                    self.selection += 1
                    self.update()
            elif c == curses.KEY_UP:
                # Select the previous volume slider
                if self.selection > 0:
                    self.selection -= 1
                    self.update()
            elif c == curses.KEY_LEFT:
                # Increase the volume
                self.getSelection().inc_volume(-1)
                self.update()
            elif c == curses.KEY_RIGHT:
                # Decrease the volume
                self.getSelection().inc_volume(1)
                self.update()
            elif c == curses.KEY_RESIZE:
                # The terminal has been resized, update the display
                self.resize()
                self.update()

ui = UI()

try:
    ui.start()

    volume = MasterVolume()

    # Get the sounds
    sounds = []
    for filename in os.listdir("sounds"):
        sounds.append(Sound(os.path.join("sounds", filename), volume))

    pygame.mixer.set_num_channels(len(sounds))

    ui.run(volume, sounds)
except:
    ui.end()
    traceback.print_exc()
