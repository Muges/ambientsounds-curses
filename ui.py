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

class OneLineWidget:
    """
    Abstract class representing a one line widget
    """
    def __init__(self, parent):
        """
        Initialize the widget.

        - parent is the curses.window object in which the widget will be
          drawn
        """
        self.parent = parent

    def draw(self, y, width, selected=False):
        """
        Abstract method used to draw the widget.

        - y is the number of the line at which the widget will be drawn.            
        - selected is a boolean indicating if the widget is selected if
        the parent is a ScrollableList
        """
        raise NotImplementedError()

    def on_key(self, c):
        """
        Method called when the user types the key c and the widget is
        selected.
        """
        return

class VolumeWidget(OneLineWidget):
    """
    Widget used to set the volume of a Volume object
    """
    def __init__(self, parent, volume, namesw):
        """
        Initialize the object.
        
        - parent is the curses.window object in which the widget will be
          drawn
        - volume is a Volume object
        - namesw is the width taken by the names of the Volume objects
        """
        OneLineWidget.__init__(self, parent)
        self.volume = volume
        self.namesw = namesw

    def draw(self, y, width, selected=False):
        # Highlight the name if the widget is selected
        if selected:
            attribute = curses.A_REVERSE
        else:
            attribute = 0

        # Draw the name
        self.parent.addstr(y, 0, " "+self.volume.name+" ", attribute)

        # Position and width of the slider
        slidex = self.namesw+5
        slidew = width-slidex-2-1
        slidewleft = (self.volume.get_volume()*slidew)/100
        slidewright = slidew-slidewleft

        # Draw the slider
        self.parent.addstr(y, slidex-2, "[ ")
        self.parent.addstr(y, slidex+slidew, " ]")

        self.parent.addstr(y, slidex, "#"*slidewleft)
        self.parent.addstr(y, slidex+slidewleft, "-"*slidewright)

    def on_key(self, c):
        if c == curses.KEY_LEFT:
            # Increase the volume
            self.volume.inc_volume(-1)
        elif c == curses.KEY_RIGHT:
            # Decrease the volume
            self.volume.inc_volume(1)

class ScrollableList:
    """
    Object representing a list of OneLineWidgets that can be browsed and
    scrolled through
    """
    def __init__(self):
        self.set_widgets([])
        
        # Number of the line which is at the top of the widget (used for
        # scrolling)
        self.top = 0
        
        self.pad = curses.newpad(1,1)

    def set_widgets(self, widgets, default=0):
        self.widgets = widgets
        self.set_selection(default)
        self.height = len(widgets)

    def get_selection(self):
        try:
            return self.widgets[self.selection]
        except KeyError:
            return None

    def set_selection(self, selection):
        """
        Set the selection, ensuring that the selected widget exists.
        """
        # Ensure that the widget is in the list
        selection = min(selection, len(self.widgets)-1)
        
        if selection < 0:
            selection = 0
        else:
            # If the widget is None, find the first widget before the
            # selection that is not None
            while (selection >= 0 and self.widgets[selection] == None):
                selection -= 1

            if selection < 0:
                # If there isn't one, find the first widget after the
                # selection that is not None
                selection = 0
                while (selection < len(self.widgets) and self.widgets[selection] == None):
                    selection += 1

                # If there still isn't one (all the widgets are equal to
                # None, set the selection to 0
                if selection >= len(self.widgets):
                    selection = 0

        self.selection = selection

    def select_previous_widget(self):
        """
        Select the first widget different to None preceding the current
        selection
        """
        selection = self.selection-1
        
        while (selection >= 0 and self.widgets[selection] == None):
            selection -= 1

        self.set_selection(selection)

    def select_next_widget(self):
        """
        Select the first widget different to None following the current
        selection
        """
        selection = self.selection+1
        
        while (selection < len(self.widgets) and self.widgets[selection] == None):
            selection += 1

        self.set_selection(selection)

    def draw(self, stop, sleft, sbottom, sright):
        """
        Draw the list in the portion of the screen delimited by the
        coordinates (stop, sleft, sbottom, sright)
        """
        height = sbottom-stop
        width = sright-sleft
        
        self.pad.clear()
        self.pad.resize(self.height, width)
        
        # Draw each widget
        y = 0
        for w in self.widgets:
            if w != None:
                w.draw(y, width, y == self.selection)
            y += 1

        ptop = max(0, min(self.selection - height/2, self.height-height-1))
        self.pad.refresh(ptop, 0, stop, sleft, sbottom, sright)
            
    def on_key(self, c):
        if c == curses.KEY_DOWN:
            self.select_next_widget()
        elif c == curses.KEY_UP:
            self.select_previous_widget()
        else:
            selection = self.get_selection()
            if selection != None:
                selection.on_key(c)

class VolumeList(ScrollableList):
    """
    List of VolumeWidgets
    """
    def __init__(self, mastervolume):
        ScrollableList.__init__(self)

        sounds = mastervolume.get_sounds()
        namesw = max(max([len(s.name) for s in sounds]), len(mastervolume.name))
        
        widgets = []
        widgets.append(VolumeWidget(self.pad, mastervolume, namesw))
        widgets.append(None)
        for sound in sounds:
            widgets.append(VolumeWidget(self.pad, sound, namesw))

        self.set_widgets(widgets, 2)
        
class UI:
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

    def update(self):
        """
        Update the screen
        """
        self.screen.clear()
        self.screen.refresh()
        
        self.volumelist.draw(self.vpadding, self.hpadding,
                             self.screenh-self.vpadding-1,
                             self.screenw-self.hpadding-1)

    def run(self, mastervolume):
        """
        Start the main loop
        """
        self.volumelist = VolumeList(mastervolume)
        
        self.resize()
        self.update()

        while True:
            # Wait for user input and handle it
            c = self.screen.getch()
            if c == ord('q'):
                # Quit
                self.end()
                break
            elif c == curses.KEY_RESIZE:
                # The terminal has been resized, update the display
                self.resize()
                self.update()
            else:
                # Propagate the key to the VolumeList
                self.volumelist.on_key(c)

            self.update()

