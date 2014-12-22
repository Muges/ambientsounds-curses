#!/usr/bin/env python2
# -*- coding: utf-8 -*-

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

import curses

class SoundsPad:
    """
    Pad containing the list of tracks, and a volume sliders for each
    one of them
    """
    def __init__(self):
        # Width taken by the track titles
        self.namesw = 0

        # Width taken by the volume slider
        self.slidew = 0

        # Index of the selected volume slider
        self.selection = 1
        # First line of the sounds pad
        self.top = 0
        self.maxtop = 0

        # Total height of the pad
        self.height = 1

    def get_selection(self):
        """
        Return the Volume object that is currently selected
        """
        if self.selection == 0:
            return self.mastervolume
        else:
            return self.mastervolume.get_sound(self.selection-1)

    def set_selection(self, index):
        self.selection = max(0, min(index, len(self.mastervolume.get_sounds())))
        self.top = max(0, min(self.selection - self.screenheight/2, self.maxtop))

    def next_track(self):
        self.set_selection(self.selection+1)

    def previous_track(self):
        self.set_selection(self.selection-1)

    def start(self):
        self.pad = curses.newpad(1,1)

    def resize(self, height, width):
        self.screenheight = height
        
        # Position of the sliders
        self.slidex = self.namesw+5
        
        # Width of the sliders
        self.slidew = width-self.namesw-7

        self.pad.resize(self.height, width+1)
        self.maxtop = max(0, self.height-height-1)
        self.top = min(self.top, self.maxtop)

    def run(self, mastervolume):
        self.mastervolume = mastervolume
        
        sounds = mastervolume.get_sounds()
        self.namesw = max(max([len(s.name) for s in sounds]), len(mastervolume.name))
        self.height = len(sounds)+2

    def create_volume_slider(self, y, sound, index):
        """
        Creates a volume slider for the Volume object `sound`
        """
        # Display the name of the sound
        if index == self.selection:
            # Highlight the name of the selected track
            attribute = curses.A_REVERSE
        else:
            attribute = 0

        self.pad.addstr(y, 0, " "+sound.name+" ", attribute)

        # Draw a volume slider : [ ####----- ]
        self.pad.addstr(y, self.slidex-2, "[ ")
        self.pad.addstr(y, self.slidex+self.slidew, " ]")

        slidewleft = (sound.get_volume()*self.slidew)/100
        slidewright = self.slidew-slidewleft
        self.pad.addstr(y, self.slidex, "#"*slidewleft)
        self.pad.addstr(y, self.slidex+slidewleft, "-"*slidewright)

    def update(self, stop, sleft, sbottom, sright):
        """
        Update the pad
        """
        self.pad.clear()

        # Draw the master volume slider
        self.create_volume_slider(0, self.mastervolume, 0)

        # Draw a slider for each sound
        index = 1
        for s in self.mastervolume.get_sounds():
            self.create_volume_slider(index+1, s, index)
            index += 1

        self.pad.refresh(self.top, 0, stop, sleft, sbottom, sright)
        
class UI:
    def __init__(self):
        self.soundspad = SoundsPad()

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

        self.soundspad.start()
        
        self.resize()

        # Display loading text
        text = "Loading sounds..."
        x = (self.screenw-len(text))/2
        y = self.screenh/2
        self.screen.addstr(y, x, text)
        self.screen.refresh()

    def end(self):
        """
        Stop the application
        """
        # End curses
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def resize(self):
        """
        Method executed when the terminal is resized : set some
        constants depending on the screen size
        """
        # Screen size
        self.screenh, self.screenw = self.screen.getmaxyx()
        
        # Horizontal and vertical padding (space between the edge of the
        # terminal and the text)
        if self.screenh > 13 and self.screenw > 60:
            self.hpadding = 5
            self.vpadding = 3
        else:
            self.hpadding = 1
            self.vpadding = 1

        self.soundspad.resize(self.screenh-2*self.vpadding-1, self.screenw-2*self.hpadding-1)

    def update(self):
        """
        Update the screen
        """
        self.screen.clear()
        self.screen.refresh()
        self.soundspad.update(self.vpadding, self.hpadding,
                              self.screenh-self.vpadding-1,
                              self.screenw-self.hpadding-1)

    def run(self, mastervolume):
        """
        Start the main loop
        """
        self.mastervolume = mastervolume
        self.soundspad.run(mastervolume)
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
                self.soundspad.next_track()
                self.update()
            elif c == curses.KEY_UP:
                # Select the previous volume slider
                self.soundspad.previous_track()
                self.update()
            elif c == curses.KEY_LEFT:
                # Increase the volume
                self.soundspad.get_selection().inc_volume(-1)
                self.update()
            elif c == curses.KEY_RIGHT:
                # Decrease the volume
                self.soundspad.get_selection().inc_volume(1)
                self.update()
            elif c == curses.KEY_RESIZE:
                # The terminal has been resized, update the display
                self.resize()
                self.update()

