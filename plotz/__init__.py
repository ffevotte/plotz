# -*- coding: utf-8 -*-
#
# This file is part of PlotZ, a plotting library
#
# Copyright (C) 2017
#   F. Févotte     <fevotte@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
# The GNU General Public License is contained in the file COPYING.

"""PlotZ"""

import sys
import tempfile
import os
import shutil
import subprocess
import math
import re
import plotz.utils

class Function(object):
    def __init__(self, fun, samples=100, range=None):
        self._fun = fun
        self._samples = samples
        self.range = range

        self._x0 = None
        self._x1 = None
        self._dx = None
        self._i = None

    def __iter__(self):
        self._x0 = self.range[0]
        self._x1 = self.range[1]
        self._dx = float(self._x1-self._x0)/(self._samples-1)
        self._i = 0
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._i == self._samples:
            raise StopIteration()

        x = self._x0 + self._i*self._dx
        self._i += 1
        return (x, self._fun(x))

def DataFile(filename, sep=re.compile(r"\s+"), comment="#"):
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(comment):
                continue

            try:
                fields = line.split(sep)
            except TypeError:
                fields = sep.split(line)

            for i in xrange(len(fields)):
                try:
                    fields[i] = float(fields[i])
                except ValueError:
                    pass

            yield fields

class Axis(object):
    """Axis"""
    def __init__(self, orientation):
        # Internal members
        self._orientation = orientation
        self._setup = True

        # Special members
        self._scale = Axis._linear

        # Public
        self.label = None
        self.label_rotate = False
        if orientation == 1:
            self.label_shift = 2
        else:
            self.label_shift = 3

        self.min = float("inf")
        self.max = float("-inf")
        self.pos = None

        self.tick = None
        self.ticks = None
        self.tick_format = self._tick_format

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, fun):
        if not self._setup:
            sys.stderr.write("Plotz error: can not change axis scale after setup")
            return

        self._scale = fun

    @staticmethod
    def _linear(x):
        return 1.0*x

    def _tick_format(self, x):
        """Default implementation for the ticks format.
Pretty print regular values and use 10^x in the case of logarithmic scale."""
        if self.scale == math.log10:
            label = "$10^{%d}$" % x
        else:
            label = plotz.utils.ppfloat(x)
        return label

    def _update(self):
        if self.tick is None:
            delta = (self.max-self.min)
            factor = 1
            while delta < 10:
                delta *= 10
                factor *= 10
            self.tick = round(delta/5.) / factor
            self.min = math.floor(self.min*factor) / factor
            self.max = math.ceil(self.max*factor) / factor

        if self.ticks is None:
            self.ticks = []

            x = self.min
            factor = 1
            while x != round(x) and abs(x) < 0.9:
                x *= 10
                factor *= 10
            x = round(x)/factor
            self.min = min(self.min, x)

            while x <= self.max:
                self.ticks.append(x)
                x += self.tick

        def normalize_tick(tick):
            try:
                (x, label) = tick
            except:
                x = tick
                label = self.tick_format(x)
            return (x, label)
        self.ticks = [normalize_tick(t) for t in self.ticks]


class Style:
    def __init__(self):
        self.color = []
        self.thickness = ["very thick"] * 8
        self.pattern = ["solid"] * 8
        self.marker = [
            r"$+$",
            r"$\circ$",
            r"$\Box$",
            r"$\triangle$",
            r"$\times$",
            r"$\bullet$",
            r"$\blacksquare$",
            r"$\blacktriangle$",
        ]

        self.colormap()

    def colormap(self, name=None):
        """Setup a colormap"""

        # Default colormap
        c = ["377EB8", "E41A1C", "4DAF4A", "984EA3", "FF7F00", "A65628", "F781BF", "FFFF33"]

        if name == "paired":
            c = ['A6CEE3', '1F78B4', 'B2DF8A', '33A02C', 'FB9A99', 'E31A1C', 'FDBF6F', 'FF7F00']
        if name == "dark":
            c = ['1B9E77', 'D95F02', '7570B3', 'E7298A', '66A61E', 'E6AB02', 'A6761D', '666666']
        if name == "spectral8":
            c = ['D53E4F', 'F46D43', 'FDAE61', 'FEE08B', 'E6F598', 'ABDDA4', '66C2A5', '3288BD']
        if name == "spectral7":
            c = ['D53E4F', 'FC8D59', 'FEE08B', 'FFFFBF', 'E6F598', '99D594', '3288BD']
        if name == "spectral6":
            c = ['D53E4F', 'FC8D59', 'FEE08B', 'E6F598', '99D594', '3288BD']
        if name == "spectral5":
            c = ['D7191C', 'FDAE61', 'FFFFBF', 'ABDDA4', '2B83BA']
        if name == "spectral4":
            c = ['D7191C', 'FDAE61', 'ABDDA4', '2B83BA']

        self.color = c

class Line:
    def __init__(self):
        self.title = None
        self.line = None
        self.color = None
        self.marker = None
        self.pattern = None
        self.thickness = None

        self.points = [[]]

    color = iter(xrange(100))
    marker = iter(xrange(100))
    pattern = iter(xrange(100))
    thickness = iter(xrange(100))

class Legend:
    def __init__(self):
        self.show = True
        self.position = "north east"
        self.anchor = None

    def _update(self):
        if self.anchor is None:
            if isinstance(self.position, str):
                self.anchor = self.position
            else:
                self.anchor = "center"

    def __call__(self, position, anchor=None):
        self.position = position
        self.anchor = anchor

        if anchor is None:
            if isinstance(position, str):
                self.anchor = position
            else:
                self.anchor = "center"


class Plot:
    """Plot"""
    def __init__(self, output):
        self.output = output
        """Basename of the output figure"""

        self.x = Axis(1)
        """x :py:class:`Axis`"""

        self.y = Axis(2)
        self.title = None
        self.size_x = 266.66
        self.size_y = 200.00
        self.scale = 1.0
        self.style = Style()
        self.lines = []
        self.legend = Legend()


    def plot(self, data, col=(0,1), title=None, line=True, markers=False,
             color=None, pattern=None, thickness=None):
        self.x._setup = False
        self.y._setup = False

        if isinstance(data, Function) and data.range is None:
            data.range = (self.x.min, self.x.max)

        l = Line()
        l.title = title
        l.line = line

        if markers is True:
            l.marker = Line.marker.next()
        elif not isinstance(markers, bool):
            l.marker = markers

        if color is None:
            l.color = Line.color.next()
        else:
            l.color = color

        if line:
            if pattern is None:
                l.pattern = Line.pattern.next()
            else:
                l.pattern = pattern

            if thickness is None:
                l.thickness = Line.thickness.next()
            else:
                l.thickness = thickness


        for row in data:
            x = row[col[0]]
            y = row[col[1]]

            try:
                x = self.x.scale(x)
                y = self.y.scale(y)

                l.points[-1].append((x,y))

                self.x.min = min(x, self.x.min)
                self.x.max = max(x, self.x.max)

                self.y.min = min(y, self.y.min)
                self.y.max = max(y, self.y.max)
            except:
                l.points.append([])

        self.lines.append(l)
        return l

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return

        self.legend._update()
        self.x._update()
        self.y._update()

        if self.x.pos is None:
            self.x.pos = self.y.min

        if self.y.pos is None:
            self.y.pos = self.x.min

        plotz.utils.TikzGenerator(self).run()

if __name__ == "__main__":
    def test():
        with Plot("test") as p:
            p.title = "PlotZ figure"

            p.x.label = "$x$"
            p.x.min = 0
            p.x.max = math.pi

            p.y.label = "$y$"

            l = p.plot(Function(lambda x: math.sin(0.5*math.pi*x), samples=100),
                       line=False, markers=True,
                       title=r"function $\sin(\frac{\pi x}{2})$")

            p.plot(Function(lambda x: math.sin(math.pi*x), samples=100),
                   title=r"$\sin(\pi x)$")

            p.legend("east", "west")


    test()
