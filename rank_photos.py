#!/usr/bin/env python
"""
Matplotlib based photo ranking system using the Elo rating system.
Reference: http://en.wikipedia.org/wiki/Elo_rating_system
by Nick Hilton
This file is in the public domain.
"""

# Python
import argparse
import glob
import json
import os
import sys
import signal
import subprocess
import random


# 3rd party
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import exifread


class Photo:

    LEFT = 0
    RIGHT = 1

    def __init__(self, filename, score = 1400.0, wins = 0, matches = 0):

        if not os.path.isfile(filename):
            raise ValueError("Could not find the file: %s" % filename)

        self._filename = filename
        self._score = score
        self._wins = wins
        self._matches = matches

        # self._read_and_downsample()


    def data(self):
        return self._data


    def filename(self):
        return self._filename


    def matches(self):
        return self._matches


    def score(self, s = None, is_winner = None):

        if s is None:
            return self._score

        assert is_winner is not None

        self._score = s

        self._matches += 1

        if is_winner:
            self._wins += 1


    def win_percentage(self):
        return (100.0 * float(self._wins) / float(self._matches)) if self._matches != 0 else 0


    def __eq__(self, rhs):
        return self._filename == rhs._filename


    def to_dict(self):

        return {
            'filename' : self._filename,
            'score' : self._score,
            'matches' : self._matches,
            'wins' : self._wins,
        }


    def _read_and_downsample(self):
        """
        Reads the image, performs rotation, and downsamples.
        """

        #----------------------------------------------------------------------
        # read image

        f = self._filename

        data = mpimg.imread(f, 0)

        #----------------------------------------------------------------------
        # downsample

        # the point of downsampling is so the images can be redrawn by the
        # display as fast as possible, this is so one can iterate though the
        # image set as quickly as possible.  No one want's to wait around for
        # the fat images to be loaded over and over.

        # dump downsample, just discard columns-n-rows

        # M, N = data.shape[0:2]

        # MN = max([M,N])

        # step = int(MN / 800)
        # if step == 0: step = 1

        # data = data[ 0:M:step, 0:N:step, :]

        #----------------------------------------------------------------------
        # rotate

        # read orientation with exifread

        with open(f, 'rb') as fd:
            tags = exifread.process_file(fd)

        r = 'Horizontal (normal)'

        try:
            r = str(tags['Image Orientation'])
        except:
            pass

        # rotate as necessary

        if r == 'Horizontal (normal)':
            pass

        elif r == 'Rotated 90 CW':

            data = np.rot90(data, 3)

        elif r == 'Rotated 90 CCW':

            data = np.rot90(data, 1)

        elif r == 'Rotated 180':

            data = np.rot90(data, 2)

        else:
            # raise RuntimeError('Unhandled rotation "%s"' % r)
            pass

        self._data = data

class Slideshow():

    def __init__(self, figsize = None):

        if figsize is None:
            figsize = [20, 12]

        self.figsize = figsize

        self.photoList = table.get_ranked_list()
        self.ind = 0

        self.fig = plt.figure(figsize=self.figsize)
        self.changeImage()

        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()

        plt.show()


    def _on_key_press(self, event):

        if event.key == 'left':
            self.ind -= 1
            plt.clf()
            self.changeImage()
            plt.draw()

        elif event.key == 'right':
            self.ind += 1
            plt.clf()
            self.changeImage()
            plt.draw()

        if event.key == 'up':
            self.ind += 10
            plt.clf()
            self.changeImage()
            plt.draw()

        elif event.key == 'down':
            self.ind -= 10
            plt.clf()
            self.changeImage()
            plt.draw()

        elif event.key == 'escape':
            sys.exit(0)

        elif event.key == ' ':
            subprocess.Popen('explorer /select,"{}"'.format(self.photoList[self.ind]._filename))

    def changeImage(self):
        photo = self.photoList[self.ind]
        assert isinstance(photo, Photo)

        plt.suptitle(photo._filename)
        plt.title("Rank #{}/{} ({:.0f})".format(((self.ind) % (len(self.photoList))) + 1, len(self.photoList), photo._score))

        photo._read_and_downsample()

        plt.imshow(photo.data())

        plt.gca().set_xticklabels([])
        plt.gca().set_yticklabels([])

        plt.gca().set_xticks([])
        plt.gca().set_yticks([])

        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)


class Display(object):
    """
    Given two photos, displays them with Matplotlib and provides a graphical
    means of choosing the better photo.
    Click on the select button to pick the better photo.
    ~OR~
    Press the left or right arrow key to pick the better photo.
    """


    def __init__(self, f1, f2, title = None, figsize = None):

        print(f1.filename())
        print(f2.filename())

        self._choice = None

        assert isinstance(f1, Photo)
        assert isinstance(f2, Photo)

        if figsize is None:
            figsize = [20, 12]

        fig = plt.figure(figsize=figsize)

        h = 10

        ax11 = plt.subplot2grid((h,2), (0,0), rowspan = h - 1)
        ax12 = plt.subplot2grid((h,2), (0,1), rowspan = h - 1)

        ax21 = plt.subplot2grid((h,6), (h - 1, 1))
        ax22 = plt.subplot2grid((h,6), (h - 1, 4))

        kwargs = dict(s = f1.filename(), ha = 'center', va = 'center', fontsize=20)
        kwargs2 = dict(s = f2.filename(), ha = 'center', va = 'center', fontsize=20)

        ax21.text(0.5, 0.5, **kwargs)
        ax22.text(0.5, 0.5, **kwargs2)

        self._fig = fig
        self._ax_select_left = ax21
        self._ax_select_right = ax22

        fig.subplots_adjust(
            left = 0.02,
            bottom = 0.02,
            right = 0.98,
            top = 0.98,
            wspace = 0.05,
            hspace = 0,
        )

        f1._read_and_downsample()
        f2._read_and_downsample()

        ax11.imshow(f1.data())
        ax12.imshow(f2.data())

        for ax in [ax11, ax12, ax21, ax22]:
            ax.set_xticklabels([])
            ax.set_yticklabels([])

            ax.set_xticks([])
            ax.set_yticks([])

        self._attach_callbacks()

        if title:
            fig.suptitle(title, fontsize=14)

        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()

        plt.show()



    def _on_click(self, event):

        if event.inaxes == self._ax_select_left:
            self._choice = Photo.LEFT
            plt.close(self._fig)

        elif event.inaxes == self._ax_select_right:
            self._choice = Photo.RIGHT
            plt.close(self._fig)


    def _on_key_press(self, event):

        if event.key == 'left':
            self._choice = Photo.LEFT
            plt.close(self._fig)

        elif event.key == 'right':
            self._choice = Photo.RIGHT
            plt.close(self._fig)

        elif event.key == 'escape':
            shutdown()


    def _attach_callbacks(self):
        self._fig.canvas.mpl_connect('button_press_event', self._on_click)
        self._fig.canvas.mpl_connect('key_press_event', self._on_key_press)


class EloTable:


    def __init__(self, max_increase = 32.0, smart = False):
        self._K = max_increase
        self._photos = {}
        self._shuffled_keys = []
        self.smart = smart


    def add_photo(self, filename_or_photo):

        if isinstance(filename_or_photo, str):

            filename = filename_or_photo

            if filename not in self._photos:
                self._photos[filename] = Photo(filename)

        elif isinstance(filename_or_photo, Photo):

            photo = filename_or_photo

            if photo.filename() not in self._photos:
                self._photos[photo.filename()] = photo


    def get_ranked_list(self):

        # Convert the dictionary into a list and then sort by score.

        ranked_list = self._photos.values()

        ranked_list = sorted(
            ranked_list,
            key = lambda record : record.score(),
            reverse = True)

        return ranked_list


    def rank_photos(self, n_iterations, figsize):
        """
        Displays two photos using the command "gnome-open".  Then asks which
        photo is better.
        """

        n_photos = len(self._photos)

        keys = list(self._photos.keys())

        if self.smart:

            variation = min(5, n_photos)

            photoList = list(self._photos.values())

            while True:
                photoList.sort(key=lambda k: k._score)
                randNum = random.randint(0, n_photos - variation)
                sublist = photoList[randNum:randNum + variation]
                sublist.sort(key=lambda k: k._matches)

                photo_a = sublist[0]
                photo_b = sublist[1]

                eloRisk = 32 * (1 - (1.0 / (1.0 + 10.0 ** ((photo_b._score - photo_a._score) / 400.0))))

                title = "matches {}:{} | Elo {:.0f}:{:.0f} ({:.1f})".format(photo_a._matches, photo_b._matches, photo_a._score, photo_b._score, eloRisk)

                d = Display(photo_a, photo_b, title, figsize)

                if d._choice == Photo.LEFT:
                    self.__score_result(photo_a, photo_b)
                elif d._choice == Photo.RIGHT:
                    self.__score_result(photo_b, photo_a)
                else:
                    raise RuntimeError("oops, found a bug!")

        else:
            for i in range(n_iterations):

                np.random.shuffle(keys)

                n_matchups = n_photos / 2

                for j in range(0, n_photos - 1, 2):

                    match_up = j / 2

                    title = 'Round %d / %d, Match Up %d / %d' % (
                        i + 1, n_iterations,
                        match_up + 1,
                        n_matchups)



                    photo_a = self._photos[keys[j]]
                    photo_b = self._photos[keys[j+1]]

                    d = Display(photo_a, photo_b, title, figsize)

                    if d._choice == Photo.LEFT:
                        self.__score_result(photo_a, photo_b)
                    elif d._choice == Photo.RIGHT:
                        self.__score_result(photo_b, photo_a)
                    else:
                        raise RuntimeError("oops, found a bug!")


    def __score_result(self, winning_photo, loosing_photo):

        # Current ratings
        R_a = winning_photo.score()
        R_b = loosing_photo.score()

        # Expectation

        E_a = 1.0 / (1.0 + 10.0 ** ((R_b - R_a) / 400.0))

        E_b = 1.0 / (1.0 + 10.0 ** ((R_a - R_b) / 400.0))

        # New ratings
        R_a = R_a + self._K * (1.0 - E_a)
        R_b = R_b + self._K * (0.0 - E_b)

        winning_photo.score(R_a, True)
        loosing_photo.score(R_b, False)


    def to_dict(self):

        rl = self.get_ranked_list()

        rl = [x.to_dict() for x in rl]

        return {'photos' : rl}



def main():

    description = """\
Uses the Elo ranking algorithm to sort your images by rank.  The program globs
for .jpg images to present to you in random order, then you select the better
photo.  After n-rounds, the results are reported.
Click on the "Select" button or press the LEFT or RIGHT arrow to pick the
better photo.
"""
    parser = argparse.ArgumentParser(description = description)

    parser.add_argument(
        "-r",
        "--n-rounds",
        type = int,
        default = 3,
        help = "Specifies the number of rounds to pass through the photo set (3)"
    )

    parser.add_argument(
        "-s",
        "--slideshow",
        action='store_true',
        help = "Start a slideshow from top ranked to least ranked"
    )

    parser.add_argument(
        "-S",
        "--smart",
        action='store_true',
        help = "Instead of random images, selects good matchups for best results."
    )

    parser.add_argument(
        "-f",
        "--figsize",
        nargs = 2,
        type = int,
        default = [20, 12],
        help = "Specifies width and height of the Matplotlib figsize (20, 12)"
    )

    parser.add_argument(
        "-d",
        "--data",
        help = "Directory where to save and read data from"
    )

    parser.add_argument(
        "photo_dir",
        help = "The photo directory to scan for .jpg images",
        nargs = '+'
    )

    args = parser.parse_args()

    commPath = os.path.commonpath(args.photo_dir) if len(args.photo_dir) > 1 else args.photo_dir[0]
    dataLocation = args.data if args.data else commPath

    assert os.path.isdir(dataLocation)
    for path in args.photo_dir:
        assert os.path.isdir(path)

    os.chdir(commPath)

    global ranking_table_json
    global ranked_txt
    ranking_table_json = os.path.join(dataLocation, 'ranking_table.json')
    ranked_txt         = os.path.join(dataLocation, 'ranked.txt')

    # Create the ranking table and add photos to it.

    global table
    table = EloTable(smart = args.smart)

    #--------------------------------------------------------------------------
    # Read in table .json if present

    sys.stdout.write("Reading in photos and downsampling ...")
    sys.stdout.flush()

    if os.path.isfile(ranking_table_json):
        with open(ranking_table_json, 'r') as fd:
            d = json.load(fd)

        # read photos and add to table

        for p in d['photos']:

            photo = Photo(**p)

            table.add_photo(photo)

    if args.slideshow:
        Slideshow(args.figsize)
        return

    #--------------------------------------------------------------------------
    # glob for files, to include newly added files

    for path in args.photo_dir:
        pathNorm = path.replace(commPath + "\\", "") if len(args.photo_dir) > 1 else ""
        filelist = glob.glob(os.path.join(pathNorm, '*.jpg'))
        filelist.extend(glob.glob(os.path.join(pathNorm, '*.png')))
        filelist.extend(glob.glob(os.path.join(pathNorm, '*.gif')))

        for f in filelist:
            table.add_photo(f)

    #def sorting(kv):
    #    return kv[1]._matches
    #
    #table._photos = dict(sorted(table._photos.items(), key=sorting))
    #
    #for k in table._photos:
    #    print(k)

    print(" done!")

    #--------------------------------------------------------------------------
    # Rank the photos!

    signal.signal(signal.SIGINT, shutdown)

    table.rank_photos(args.n_rounds, args.figsize)

    shutdown()


def shutdown():

    print('Shutting Down')
    
    #--------------------------------------------------------------------------
    # save the table

    with open(ranking_table_json, 'w', encoding="utf-8") as fd:

        d = table.to_dict()

        jstr = json.dumps(d, indent = 4, separators=(',', ' : '))

        fd.write(jstr)

    #--------------------------------------------------------------------------
    # dump ranked list to disk

    with open(ranked_txt, 'w', encoding="utf-8") as fd:

        ranked_list = table.get_ranked_list()

        heading_fmt = "%4d    %4.0f    %7d    %7.2f    %s\n"

        heading = "Rank    Score    Matches    Win %    Filename\n"

        fd.write(heading)

        for i, photo in enumerate(ranked_list):

            line = heading_fmt %(
                i + 1,
                photo.score(),
                photo.matches(),
                photo.win_percentage(),
                photo.filename())

            fd.write(line)

    #--------------------------------------------------------------------------
    # dump ranked list to screen

    print("Final Ranking:")

    with open(ranked_txt, 'r', encoding="utf-8") as fd:
        text = fd.read()

    print(text)
    sys.exit(0)

table = None
ranking_table_json = None
ranked_txt = None

if __name__ == "__main__": main()