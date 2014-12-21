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

import pygame
pygame.mixer.init(frequency=48000)

import os.path
import json
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
        
        self.sound = None
        
    def _set_volume(self):
        if self.sound == None:
            # Load the sound
            self.sound = pygame.mixer.Sound(self.filename)
            self.sound.play(-1)
            
        self.sound.set_volume((self.mastervolume.get_volume()*self.get_volume())/10000.)

class Preset:
    def __init__(self, filename, master):
        self.filename = filename
        self.master = master
        self.volumes = {}

    def apply(self):
        for sound in self.master.get_sounds():
            if self.volumes.has_key(sound.name):
                sound.set_volume(self.volumes[sound.name])
            else:
                sound.set_volume(0)

    def save(self):
        for sound in self.master.get_sounds():
            volume = sound.get_volume()
            if volume == 0:
                self.volumes.pop(sound.name)
            else:
                self.volumes[sound.name] = volume

    def read(self):
        # TODO : handle errors
        with open(self.filename, "r") as f:
            self.volumes = json.load(f)

    def write(self):
        # TODO : handle errors
        with open(self.filename, "w") as f:
            json.dump(self.volumes, f)

class MasterVolume(Volume):
    confdirs = [os.path.dirname(os.path.realpath(__file__)),
                "/usr/share/ambientsounds/",
                os.path.expanduser("~/.config/ambientsounds/")]

    def __init__(self):
        Volume.__init__(self, "Volume", 100)

        # Get the sounds
        self.sounds = []
        for dirname in self.confdirs:
            sounddir = os.path.join(dirname, "sounds")
            if os.path.isdir(sounddir):
                for filename in os.listdir(sounddir):
                    self.sounds.append(Sound(os.path.join(sounddir, filename), self))

        pygame.mixer.set_num_channels(len(self.sounds))

        # Get the presets
        self.presets = []
        for dirname in self.confdirs:
            presetdir = os.path.join(dirname, "presets")
            if os.path.isdir(presetdir):
                for filename in os.listdir(presetdir):
                    self.presets.append(Preset(os.path.join(presetdir, filename), self))

    def get_sounds(self):
        return self.sounds

    def get_presets(self):
        return self.presets

    def _set_volume(self):
        """
        Update the volume of all the sounds
        """
        for sound in self.sounds:
            sound._set_volume()
