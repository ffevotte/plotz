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

"""This is the python API to PlotZ.

PlotZ is a system to produce TikZ-based plots destined to be seamlessly included
in a LaTeX document.
"""
#pylint: disable=invalid-name

import sys
import math
import re
import numbers
import plotz.utils

__all__ = ["Plot", "Axis", "Legend", "Style", "Line", "Function", "DataFile"]

class Function(object):
    """Data generator for python functions

    Args:
      fun (function): python function
      samples (int):  number of sampled points
      range (tuple):  range of the data
    """
    #pylint: disable=too-few-public-methods

    def __init__(self, fun, samples=100, range=None):
        #pylint: disable=redefined-builtin

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

    # necessary for Python3
    def __next__(self): # pragma: no cover
        return self.next()

    def next(self):
        #pylint: disable=missing-docstring

        if self._i == self._samples:
            raise StopIteration()

        x = self._x0 + self._i*self._dx
        self._i += 1
        return (x, self._fun(x))

def DataFile(filename, sep=re.compile(r"\s+"), comment="#"):
    """ Data generator for an ASCII datafile

    Args:
      filename (str):  path to the data file
      sep (str or re): delimiter for columns
      comment (str):   string indicating the beginning of a comment line
    """
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(comment):
                continue

            try:
                fields = line.split(sep)
            except TypeError:
                fields = sep.split(line)

            for i, f in enumerate(fields):
                try:
                    fields[i] = float(f)
                except ValueError:
                    pass

            yield fields

class Axis(object):
    """Plot axis

    This object stores everything related to plot axes: range, position,
    position of ticks...
    """
    #pylint: disable=too-many-instance-attributes

    def __init__(self, orientation):
        # Internal members
        self._orientation = orientation
        self._setup = True
        self._scale = Axis.linear

        #: Axis label
        self.label = None

        #: True if the label should be rotated
        self.label_rotate = False

        #: Space between the axis and the label
        self.label_shift = 2
        if orientation == 2:
            self.label_shift = 3

        #: Maximum axis value
        #:
        #: This value is computed automatically when plotting data, but can be
        #: changed manually if necessary.
        self.max = float("-inf")
        #: Minimum axis value. (see :py:attr:`max` for details)
        self.min = float("inf")

        #: Position of the axis with respect to the other axis.
        #:
        #: By default, the position will be set to the minimum value of the
        #: other axis. In other words, by default, the *x* and *y* axes are
        #: respectively drawn on the bottom and left part of the plotting area.
        self.pos = None

        #: List of axis ticks, in one of three forms
        #:
        #: 1. *dx*
        #: 2. [*x1*, *x2*, *x3*, ...]
        #: 3. [(*x1*, *label1*), (*x2*, *label2*), ...]
        #:
        #: Detailed explanation:
        #:
        #: 1. Tick positions range from :py:attr:`min` to :py:attr:`max` by
        #:    increments of *dx*. Tick labels are computed by :py:attr:`tick_format`.
        #:
        #: 2. Ticks are placed at positions *x1*, *x2*, *x3*... Labels are
        #:    computed by :py:attr:`tick_format`.
        #:
        #: 3. Ticks are placed at positions *x1*, *x2*, *x3*... Labels are
        #:    defined by *label1*, *label2*, *label3*...
        self.ticks = None

        #: Function called to format tick labels.
        #:
        #: The default behaviour is to label tick as :math:`10^x` in
        #: logarithmic scale, and to pretty-print values in linear scale.
        self.tick_format = self._tick_format

        #: Rotate tick labels by this amount (in degrees)
        self.tick_rotate = 0

        #: Anchor of tick labels
        self.tick_anchor = None

    @property
    def scale(self):
        "Axis scale: :py:class:`linear` or :py:class:`logarithmic`"
        return self._scale

    @scale.setter
    def scale(self, fun):
        if not self._setup:
            sys.stderr.write("Plotz error: can not change axis scale after setup")
            return

        self._scale = fun

    @staticmethod
    def linear(x):
        "Linear scale"
        return 1.0*x

    @staticmethod
    def logarithmic(x):
        "Logarithmic scale"
        return math.log10(x)

    def _tick_format(self, x):
        """Default implementation for the ticks format.
Pretty print regular values and use 10^x in the case of logarithmic scale."""
        if self.scale == Axis.logarithmic:
            label = "$10^{%d}$" % x
        else:
            label = plotz.utils.ppfloat(x)
        return label

    def _update(self):
        self._update_ticks()
        self._update_tick_rotation()

    def _update_ticks(self):
        if self.ticks is None:
            delta = (self.max-self.min)
            factor = 1
            while delta < 10:
                delta *= 10
                factor *= 10
            self.ticks = round(delta/5.) / factor
            self.min = math.floor(self.min*factor) / factor
            self.max = math.ceil(self.max*factor) / factor

        if isinstance(self.ticks, numbers.Number):
            x = self.min
            factor = 1
            while x != round(x) and abs(x) < 0.9:
                x *= 10
                factor *= 10
            x = round(x)/factor
            self.min = min(self.min, x)

            ticks = []
            while x <= self.max:
                ticks.append(x)
                x += self.ticks

            self.ticks = ticks

        def _normalize_tick(tick):
            try:
                (x, label) = tick
            except TypeError:
                x = tick
                label = self.tick_format(x)
            return (x, label)
        self.ticks = [_normalize_tick(t) for t in self.ticks]

    def _update_tick_rotation(self):
        anchor = ["north", "north east",
                  "east", "south east",
                  "south", "south west",
                  "west", "north west"]

        if self.tick_anchor is None:
            rot = (self.tick_rotate + (self._orientation - 1) * 90.) / 45.
            self.tick_anchor = anchor[int(round(rot) % 8)]

        for i, a in enumerate(anchor):
            if self.tick_anchor == a:
                rot = i
                break

        if 90 < self.tick_rotate % 360 < 270:
            self.tick_rotate += 180
            rot += 4

        self.tick_anchor = anchor[int(round(rot) % 8)]


class Style(object):
    """This object is responsible for storing all settings related to the styling
    of the plot: colors, line patterns, markers..."""
    #pylint: disable=too-few-public-methods

    def __init__(self):
        #: List of colors used in the plot. This might be more easily set using
        #: :py:func:`colormap`
        self.color = []
        self.colormap()

        #: List of TikZ line thicknesses used in the plot
        #:
        #: By default, all lines are *very thick*.
        self.thickness = ["very thick"] * 8

        #: List of dash/dot patterns used in the plot.
        #:
        #: By default, all lines are solid.
        self.pattern = ["solid"] * 8

        #: List of markers used in the plot.
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

    def colormap(self, name=None):
        """ Setup a colormap.

        Predefined colormaps come from colorbrewer2.org:

        *default*
          8-color map with qualitatively varying colors (qualitative, set1)

        *dark*
          8-color map with qualitatively varying colors in darker tones (qualitative, dark2)

        *paired*
          8-color map with paired colors (qualitative, paired)

        *spectralN* (for N=4..8)
          N-color map with diverging colors (diverging, spectral)
        """

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

class Line(object):
    """ A line in the plot.

    Plotted lines are created by :py:meth:`Plot.plot`, but they can be altered
    afterwards.
    """
    #pylint: disable=too-few-public-methods

    def __init__(self):
        #: Title of the line.
        #:
        #: If set, this is what goes in the plot legend.
        self.title = None

        #: True if the line should be drawn.
        self.line = None

        #: Index of the line color in the :py:attr:`Style.color` list.
        self.color = None

        #: Index of the point markers in the :py:attr:`Style.marker` list.
        self.marker = None

        #: Index of the line dash/dot pattern in the :py:attr:`Style.pattern`
        #: list.
        self.pattern = None

        #: Index of the line thickness in the :py:attr:`Style.thickness` list.
        self.thickness = None

        self.points = [[]]

class LineProperties(object):
    """ Manages the cycling through line properties """
    #pylint: disable=too-few-public-methods

    def __init__(self):
        self.color = iter(range(100))
        self.marker = iter(range(100))
        self.pattern = iter(range(100))
        self.thickness = iter(range(100))

class Bar(object):
    """ Models a bar in an histogram """
    #pylint: disable=too-few-public-methods

    def __init__(self):
        self.title = None
        self.color = None
        self.points = []

class Legend(object):
    """ Plot legend """
    #pylint: disable=too-few-public-methods

    def __init__(self):
        #: True if the legend should be drawn on the plot
        self.show = True

        #: Position of the legend in the plot.
        #:
        #: If this is a string (such as "north east"), it is taken to be a
        #: TikZ anchor in the plotting area.
        #:
        #: Otherwise, :py:attr:`position` should be a tuple of coordinates.
        self.position = "north east"

        #: Anchor relatively to which the legend is positioned.

        #: This defines which part of the legend is positioned where defined by
        #: :py:attr:`position`. This should be a string denoting a TikZ anchor
        #: (such as "north east", meaning that the top left corner of the legend
        #: is to be positioned where defined by :py:attr:`position`).
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

class Histogram(object):
    """ Holds all settings related to histograms plotting """
    #pylint: disable=too-few-public-methods

    def __init__(self):
        self.bins = None
        self.gap = 0

class Plot(object):
    """ Master object to create a PlotZ figure.

    This object is supposed to be used in a ``with`` statement::

        with Plot("myname") as p:
            p.plot(...)

            # the plot is actually generated at the end of the block
    """
    #pylint: disable=too-many-instance-attributes,too-few-public-methods

    def __init__(self, output):
        #: Basename of the output figure
        #:
        #: Plotz will generate two files
        #:   - ``<output>.tex``: the actual PlotZ figure, which you can include in
        #:     any LaTeX document using the ``plotz`` command.
        #:   - ``<output>.pdf``: a rendered pdf version of the figure.
        self.output = output

        #: x :py:class:`Axis`
        self.x = Axis(1)

        #: y :py:class:`Axis`
        self.y = Axis(2)

        #: Plot title
        self.title = None

        #: Plot width
        #:
        #: This defines the default width of the plotting area (*i.e* excluding
        #: axis labels, title, legend...) It is used when producing the pdf
        #: output, and as a default size when including the plot in a LaTeX
        #: document. This size can be changed in LaTeX using
        #: ``\plotz[width=...]{}``
        #:
        #: The default aspect ratio of the plotting area is 4:3
        self.size_x = 266.66

        #: Plot height (see :py:attr:`size_x` for more details)
        self.size_y = 200.00

        #: Plot scale.
        #:
        #: This is a convenient way to adjust the default size of the plot
        #: without affecting its aspect ratio. Both :py:attr:`size_x` and
        #: :py:attr:`size_y` are multiplied by :py:attr:`scale` to determine the
        #: default plot size.
        self.scale = 1.0

        #: Plot :py:class:`Style`
        self.style = Style()

        #: Plot :py:class:`Legend`
        self.legend = Legend()

        self.data_series = []
        self.histogram = Histogram()
        self.line = LineProperties()
        self.line_type = Line
        self.bar_type = Bar

    def plot(self, data, col=(0, 1), filter=None,
             title=None, line=True, markers=False,
             color=None, pattern=None, thickness=None):
        """ Plot a curve

        Args:
          data: data generator (see :py:class:`Function` and :py:class:`DataFile`)
          tuple col:  tuple of column indices to plot
          str title: line title
          bool line: ``True`` if the line should be drawn
          markers: - ``False``: avoid drawing point markers
                   - ``True``: use the next available marker
                   - *int*: index of the marker to use
          int color, pattern, thickness: see the relevant :py:class:`Line`
             attributes. If these are not specified, line attributes indices advance
             by one for each plotted line.

        Returns:
          the drawn :py:class:`Line`, which can be modifed afterwards as needed.
        """
        #pylint: disable=too-many-arguments, protected-access

        self.x._setup = False
        self.y._setup = False

        if isinstance(data, Function) and data.range is None:
            self._update_histogram()
            data.range = (self.x.min, self.x.max)

        l = Line()
        l.title = title
        l.line = line

        if markers is True:
            l.marker = next(self.line.marker)
        elif not isinstance(markers, bool):
            l.marker = markers

        if color is None:
            l.color = next(self.line.color)
        else:
            l.color = color

        if line:
            if pattern is None:
                l.pattern = next(self.line.pattern)
            else:
                l.pattern = pattern

            if thickness is None:
                l.thickness = next(self.line.thickness)
            else:
                l.thickness = thickness


        for row in data:
            try:
                x = self.x.scale(row[col[0]])
                y = self.y.scale(row[col[1]])

                l.points[-1].append((x, y))

                self.x.min = min(x, self.x.min)
                self.x.max = max(x, self.x.max)

                self.y.min = min(y, self.y.min)
                self.y.max = max(y, self.y.max)
            except (TypeError, IndexError):
                if l.points[-1] != []:
                    l.points.append([])

        if l.points[-1] == []:
            del l.points[-1]

        self.data_series.append(l)
        return l

    def hist(self, data, col=0, title=None, color=None):
        """Plot a histogram

        Args:
          data: data generator (see :py:class:`Function` and :py:class:`DataFile`)
          int col: column index (if data has multiple columns)
          str title: line title
          int color: color of the bars. If left unspecified, the next color in
            the list is taken

        Returns:
          the drawn :py:class:`Bar`, which can be modifed afterwards as needed.
        """
        #pylint: disable=blacklisted-name

        bar = Bar()
        bar.title = title

        if color is None:
            bar.color = next(self.line.color)
        else:
            bar.color = color

        for y in data:
            if isinstance(y, numbers.Number):
                bar.points.append(y)
            else:
                bar.points.append(y[col])

            self.y.min = min(y, self.y.min)
            self.y.max = max(y, self.y.max)

        self.data_series.append(bar)
        return bar

    def _update_histogram(self):
        if self.histogram.bins is None:
            for obj in self.data_series:
                if isinstance(obj, Bar):
                    nbins = len(obj.points)
                    self.histogram.bins = [i-0.5 for i in range(nbins + 1)]
                    break

        if self.histogram.bins is not None:
            self.x.min = min(self.x.min, self.histogram.bins[0])
            self.x.max = max(self.x.max, self.histogram.bins[-1])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #pylint: disable=protected-access

        if exc_type is not None:
            return

        self._update_histogram()

        self.legend._update()
        self.x._update()
        self.y._update()

        if self.x.pos is None:
            self.x.pos = self.y.min

        if self.y.pos is None:
            self.y.pos = self.x.min

        plotz.utils.TikzGenerator(self).run()
