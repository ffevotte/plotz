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

import sys
import tempfile
import os
import shutil
import subprocess
import math
import re

def ppfloat(x, fmt="%f"):
    """Return a pretty string representing the given float.
ALl useless trailing zeros are removed."""
    res = fmt % x
    if res.find(".") >= 0:
        while res.endswith("0"):
            res = res[0:len(res)-1]
        if res.endswith("."):
            res = res[0:len(res)-1]
    return res

class Axis(object):
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
        return x

    def _tick_format(self, x):
        """Default implementation for the ticks format.
Pretty print regular values and use 10^x in the case of logarithmic scale."""
        if self.scale == math.log10:
            label = "$10^{%d}$" % x
        else:
            label = ppfloat(x)
        return label

class Style:
    def __init__(self):
        self.color = []
        self.thickness = ["thick"] * 8
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
        self.markers = None
        self.pattern = None
        self.thickness = None

class Legend:
    def __init__(self):
        self.show = True
        self.position = "north east"
        self.anchor = "north east"

class Plot:
    def __init__(self):
        self.x = Axis(1)
        self.y = Axis(2)
        self.title = None
        self.size_x = 266.66
        self.size_y = 200.00
        self.scale = 1.0
        self.style = Style()
        self.lines = []
        self.legend = Legend()


    def plot(self, data, col=(0,1), title=None, line=True, markers=False):
        self.x._setup = False
        self.y._setup = False

        if isinstance(data, Function) and data.range is None:
            data.range = (self.x.min, self.x.max)

        l = Line()
        l.title = title
        l.line = line
        l.markers = markers

        l.points = [[]]
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

class Function(object):
    def __init__(self, fun, samples=100, range=None):
        self._fun = fun
        self._samples = samples
        self.range = range

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

def columns(i, j):
    def fun(fields):
        return (fields[i], fields[j])
    return fun


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


def test1():
    import numpy

    N = 100
    data = numpy.zeros((N, 3))
    for i in xrange(N):
        x = (i+0.5)*1/float(N)
        data[i, :] = [x, math.sin(math.pi*x), math.sin(math.pi*x*2)]

    with Plot("test") as plot:
        plot.x.label = "$x$"
        plot.y.label = "$y$"
        plot.y.label_rotate = True

        plot.plot(Function(lambda x: math.sin(0.5*math.pi*x), samples=50, range=(0, 1)),
                  line=False, markers=True,
                  title=r"function $\sin(\frac{\pi x}{2})$")

        plot.tikz(r"""
           \draw[->](0.56,0)
             node[anchor=south west, fill=white]{\texttt{tikz} annotations on the figure}
             -- ++(-1em,-1em);""")

        plot.legend("south west")

if __name__ == "__main__":
    #test1()
    p = Plot()
    p.x.min = 0
    p.x.max = math.pi

    l = p.plot(Function(lambda x: math.sin(0.5*math.pi*x), samples=10),
               line=False, markers=True,
               title=r"function $\sin(\frac{\pi x}{2})$")

    p.x.scale = math.log10

    import pprint
    p.x = p.x.__dict__
    p.y = p.y.__dict__
    p.style = p.style.__dict__
    p.legend = p.legend.__dict__
    for i in xrange(len(p.lines)):
        p.lines[i] = p.lines[i].__dict__
    pprint.pprint(p.__dict__)
