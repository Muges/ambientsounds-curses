# Ambientsounds

Curses based ambient sound player inspired by Noizio, A Soft Murmur,
etc...

## Dependencies

The program depends on :

- [python 2](https://www.python.org/)
- [pygame](http://www.pygame.org/news.html) to play the tracks
- [mutagen](https://bitbucket.org/lazka/mutagen) to read the ogg vorbis tags

## Manual

- `Up`/`Down` to change select the master Volume or a track
- `Left`/`Right` to change the volume of the selected track
- `q` to quit

## Sounds

The original sound files are listed below.

- [Stream by mystiscool](http://www.freesound.org/people/mystiscool/sounds/7138/) (CC BY)
- [Thunderstorm by RHumphries](http://www.freesound.org/people/RHumphries/sounds/2523/) (CC BY)
- [Fireplace by inchadney](http://www.freesound.org/people/inchadney/sounds/132534/) (CC0)

To add new sounds, you just need to create an ogg file of a few
minutes (preferably less than 5) that loops seamlessly, set the title
tag correctly, and put it in the `sounds` folder. Creating a seamless
loop is pretty easy with natural sounds, I personally use
[audacity](http://audacity.sourceforge.net/), with
[this method](http://manual.audacityteam.org/o/man/tutorial_looping.html)
to extract a segment that loops without clicking, and if needed,
[this one](http://www.wearytaffer.com/tutorials/tut_loops.html) to
fade the beginning and the end of the track. You can also modify the
tags when you export an ogg file with audacity.

If you want me to add your sound to the program, you can make a pull
request or open an issue. This program is a free software, and will
only contain free sounds, with licenses such as CC0, CC BY, CC BY-SA
(and not CC BY-NC or CC BY-ND).

## TODO

- Add new sounds
- Save and load presets
