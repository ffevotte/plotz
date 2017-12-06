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

""" Utility functions for PlotZ """
#pylint: disable=invalid-name

import sys
import tempfile
import shutil
import os
import subprocess
import re
import itertools
from difflib import SequenceMatcher

def ppfloat(x, fmt="%f"):
    """Return a pretty string representing the given float.
All useless trailing zeros are removed."""
    res = fmt % x
    if res.find(".") >= 0:
        while res.endswith("0"):
            res = res[0:len(res)-1]
        if res.endswith("."):
            res = res[0:len(res)-1]
    return res

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)



def consumer(func):
    """Transform a generator function into a comsuming co-routine"""
    def wrapper(*args, **kw):
        """Automatically call `next()` a first time when the generator is created."""
        gen = func(*args, **kw)
        next(gen)
        return gen
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

class Markers(object):
    """Groups all built-in marker filters"""
    @staticmethod
    @consumer
    def always():
        """Marker filter that displays a marker for each data point"""
        while True:
            yield True

    @staticmethod
    @consumer
    def oneInN(N, start=0):
        """Marker filter that displays a marker for one data point in N

        Args:
          int N: period of the markers. One data points in *N* gets a marker.
          int start: index of the first data point to have a marker.
        """
        yield
        i = start
        while True:
            if i == 0:
                i = N
                yield True
            else:
                yield False
            i -= 1

    @staticmethod
    @consumer
    def equallySpaced(dX, start=0):
        """Marker filter that displays markers equally spaced (with respect to the *x* coordinate)

        Args:
          float dX: period of the markers. One marker gets displayed each time *x* advances by at
                    least *dX*.
          float start: abscissa of the first displayed marker.
        """
        ret = None

        while True:
            x, _ = yield ret
            if x >= start:
                ret = True
                start += dX
            else:
                ret = False


class StrictPrototype(object):
    """Helper class which enforces a strict prototype

    Each time a non-existing attribute is accessed for writing, an
    AttributeError is raised, along with a help message listing existing
    attributes with similar names.
    """
    #pylint: disable=too-few-public-methods

    def __init__(self):
        object.__setattr__(self, "_init", True)

    def _end_init(self):
        object.__setattr__(self, "_init", False)

    def __setattr__(self, var, val):
        msg = ""
        try:
            if self._init is False:
                self.__getattribute__(var)
            object.__setattr__(self, var, val)
            return
        except AttributeError as e:
            msg = e.args[0]

        attrs = {}
        for attr in self.__dict__:
            attrs[attr] = SequenceMatcher(None, attr, var).ratio()

        fixit = ""
        i = 0
        for attr, val in sorted(attrs.items(), key=lambda x: 1-x[1]):
            i += 1
            if i > 5:
                break
            if val < 0.5:
                break
            fixit += "\n    " + attr

        if fixit != "":
            msg = "\n  Maybe you meant one of the following:" + fixit

        raise AttributeError(msg)


class TmpDir(object):
    """Temporary directory
Useable in a `with` statement. Automatically takes care of deleting itself."""
    #pylint: disable=too-few-public-methods

    def __init__(self):
        self._name = tempfile.mkdtemp(prefix="plotz")

    def __enter__(self):
        return self._name

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._name)

class LatexOutput(object):
    """Collection of LaTeX lines

    This object allows progressively build a LaTeX document by inserting lines
    in an initially empty skeleton.
    """
    def __init__(self):
        self._lines = [r"\makeatletter", [], r"\makeatother"]
        self._index = {}

    def _get_key(self, path):
        if isinstance(path, str):
            path = path.split("/")

        lines = self._lines[1]
        index = self._index
        for component in path:
            if component == "":
                continue
            (i, d) = index[component]
            lines = lines[i]
            index = d

        return (lines, index)

    def insert(self, key, before=None, after=None):
        """Add an insertion point in the LaTeX document.

        This insertion point is identified by its key. LaTeX lines can be appended to it.

        Args:
          str key:    identifier for the insertion point
          str before: optional string inserted before the actual contents
          str after:  optional string inserted after the actual contents

        Returns:
          the LatexOutput object itself, in order to be able to chain method calls.
        """
        path = key.split("/")
        name = path[-1]
        path = path[:-1]
        (lines, index) = self._get_key(path)

        lines += ["", "%% %s "%key]
        if before is not None:
            lines.append(before)

        index[name] = (len(lines), {})
        lines.append([])

        if after is not None:
            lines.append(after)

        return self

    def append(self, key, contents):
        """Add LaTeX contents at an insertion point

        Args:
          str key:  identifier for the insertion point
          contents: LaTeX line(s). Can be either a string, or an array of
                      strings (which be interpreted as lines)
        """
        (lines, _) = self._get_key(key)
        lines.append(contents)

        return self

    def write(self, stream):
        """Write the LaTeX document to a stream.

        Args:
          stream: open stream where the LaTeX document is to be written
        """
        def _write(stream, l, indent):
            if isinstance(l, str):
                stream.write(indent+l+"%\n")
            else:
                for ll in l:
                    _write(stream, ll, indent+"  ")

        for l in self._lines:
            _write(stream, l, "")


class TikzGenerator(object):
    """ Plot renderer: this helper class generates the TikZ code for a plot """
    #pylint: disable=too-few-public-methods, too-many-instance-attributes

    def __init__(self, plot):
        self._plot = plot

        self._latex = (
            LatexOutput()
            .insert("/header")
            .insert("/header/colors")
            .insert("/header/markers")
            .insert("/header/patterns")
            .insert("/header/thickness")
            .insert("/background",
                    r"\def\plotz@background{", "}")
            .insert("/background/bbox")
            .insert("/background/grid")
            .insert("/background/legend")
            .insert("/lines",
                    r"\def\plotz@lines{", "}")
            .insert("/foreground",
                    r"\def\plotz@foreground{", "}")
            .insert("/foreground/axes")
            .insert("/foreground/legend")
            .insert("/legend",
                    r"\def\plotz@legend{", "}")
            .insert("/legendmargin",
                    r"\def\plotz@legendmargin{", "}")
            .insert("/scale"))

        self._color = None
        self._marker = None
        self._pattern = None
        self._thickness = None

        self._legend_shift = iter(range(100))

        self._nbars = None


    def run(self):
        """Actually generate the TikZ code for a plot, and compile it to produce a pdf preview"""
        self._style()
        self._size()
        self._title()

        self._axis(self._plot.x)
        self._axis(self._plot.y)

        self._grid()

        self._nbars = self._plot.histogram.gap
        for obj in self._plot.data_series:
            if isinstance(obj, self._plot.bar_type):
                self._nbars += 1

        ibar = iter(range(100))
        for obj in self._plot.data_series:
            if isinstance(obj, self._plot.line_type):
                self._line(obj)

            if isinstance(obj, self._plot.bar_type):
                self._bar(obj, next(ibar))

        self._legend()
        self._compile()


    def _style(self):
        self._define_style(self._plot.style.color,
                           "/header/colors",
                           r"\definecolor{color%s}{HTML}{%s}")

        self._define_style(self._plot.style.marker,
                           "/header/markers",
                           r"\def\marker%s{%s}")

        self._define_style(self._plot.style.pattern,
                           "/header/patterns",
                           r"\tikzstyle{pattern%s}=[%s]")

        self._define_style(self._plot.style.thickness,
                           "/header/thickness",
                           r"\tikzstyle{thick%s}=[%s]")

    def _define_style(self, list, path, definition):
        #pylint: disable=redefined-builtin
        self._latex.append(path, [
            definition % (self._index(i), val)
            for (i, val) in enumerate(list)
        ])

    def _line_options(self, line):

        # Style
        style = ["color%s" % self._index(line.color)]
        if line.line:
            style += [
                "pattern%s" % self._index(line.pattern),
                "thick%s" % self._index(line.thickness),
            ]


        # Draw line or not
        draw = "  "
        if line.line:
            draw = "--"


        # Marker
        marker = line.markers
        if marker is not None:
            marker = r"node{\marker%s}" % self._index(marker)
        else:
            marker = ""


        # Options
        return {
            "style": ",".join(style),
            "draw": draw,
            "marker": marker,
        }

    def _line_legend(self, line, options):
        if line.title:
            shift = -1.5 * next(self._legend_shift)
            self._latex.append("/legend", "".join([
                r"\draw[%s](0,%fem)%s++(2em,0)"
                % (options["style"], shift, options["draw"]),
                r"node[right,inner sep=2pt,black]{%s};"%line.title,
            ]))
            self._latex.append("/legend",
                               r"\draw[%s](1em,%fem)%s;"
                               % (options["style"], shift, options["marker"]))

    def _line(self, line):
        options = self._line_options(line)

        self._line_legend(line, options)

        self._latex.append("/lines", r"\draw[%s]" % options["style"])
        for subline in line.points:

            points = iter(subline)
            (x, y) = next(points)

            marker = options["marker"]
            if line.markers_filter.send((x, y)) is False:
                marker = ""

            self._latex.append("/lines",
                               "  (%.15f,%.15f)%s" % (x, y, marker))

            for (x, y) in points:
                marker = options["marker"]
                if line.markers_filter.send((x, y)) is False:
                    marker = ""
                self._latex.append("/lines",
                                   "%s(%.15f,%.15f)%s" % (options["draw"], x, y,
                                                          marker))

            self._latex.append("/lines", ";")


    def _bar_legend(self, bar, style):
        #pylint: disable=blacklisted-name

        if bar.title:
            shift = -1.5 * next(self._legend_shift)
            self._latex.append("/legend", "".join([
                r"\draw[%s](0,%fem)++(0,-0.5em)rectangle++(2em,1em)++(0,-0.5em)"
                % (style, shift),
                r"node[right,inner sep=2pt,black]{%s};" % bar.title,
            ]))

    def _bar(self, bar, index):
        #pylint: disable=blacklisted-name

        plot = self._plot
        histogram = plot.histogram
        bins = histogram.bins

        style = "fill=color%s" % self._index(bar.color)
        self._bar_legend(bar, style)

        for i, y in enumerate(bar.points):
            dx = (bins[i+1] - bins[i]) / self._nbars
            x0 = bins[i] + dx * (index + 0.5 * histogram.gap)
            x1 = x0 + dx

            self._latex.append("/lines", "".join([
                r"\draw[%s]" % style,
                "(%.15f,%.15f)" % (x0, plot.y.min),
                "rectangle(%.15f,%.15f);" % (x1, y)]))

    def _axis(self, axis):
        #pylint: disable=protected-access

        # Options
        tick_options = "rotate=%f,anchor=%s" % (axis.tick_rotate, axis.tick_anchor)

        if axis._orientation == 1:
            label_options = "anchor=north"
            if axis.label_rotate:
                label_options += ",rotate=90,anchor=east,inner sep=1em"
        else:
            label_options = "anchor=east"
            if axis.label_rotate:
                label_options += ",rotate=90,anchor=south,inner sep=1em"

        # Coordinates rotation
        def _coord(x, y):
            if isinstance(x, float):
                x = "%.15f" % x
            if isinstance(y, float):
                y = "%.15f" % y

            if axis._orientation == 1:
                return "%s,%s" % (x, y)
            return "%s,%s" % (y, x)

        # Axis
        self._latex.append("/foreground/axes",
                           r"\draw(%s)--(%s);"
                           % (_coord(axis.min, axis.pos), _coord(axis.max, axis.pos)))

        # Label
        if axis.label is not None:
            self._latex.append("/foreground/axes",
                               r"\draw(%s)++(%s)"
                               % (_coord(0.5*(axis.min+axis.max), axis.pos),
                                  _coord(0, "-%fem"%axis.label_shift)) +
                               r"node[%s]{%s};" % (label_options, axis.label))

        # Ticks
        for (x, label) in axis.ticks:
            self._latex.append("/foreground/axes", [
                r"\draw(%s)++(%s)--++(%s)" % (_coord(x, axis.pos),
                                              _coord(0, "0.5em"),
                                              _coord(0, "-1em")),
                r"   node[%s]{%s};" % (tick_options, label)])

    def _grid(self):
        plot = self._plot

        if plot.grid_x:
            for x, _ in plot.x.ticks:
                self._latex.append("/background/grid", [
                    r"\draw[help lines](%f,%f)--(%f,%f);" % (x, plot.y.min, x, plot.y.max)
                ])

        if plot.grid_y:
            for y, _ in plot.y.ticks:
                self._latex.append("/background/grid", [
                    r"\draw[help lines](%f,%f)--(%f,%f);" % (plot.x.min, y, plot.x.max, y)
                ])

    def _legend(self):
        legend = self._plot.legend

        if legend.show is False:
            return

        if isinstance(legend.position, str):
            position = "current bounding box." + legend.position
        else:
            position = "%f,%f" % legend.position

        self._latex.append("/background/legend",
                           r"\coordinate(legend)at(%s);"
                           % (position))
        self._latex.append("/foreground", [
            r"\node[anchor=%s,inner sep=0]at(legend){" % (legend.anchor),
            r"  \usebox{\plotz@boxlegend}",
            r"};"
        ])

        self._latex.append("/legendmargin",
                           r"\draw[opacity=0](current bounding box.%s)circle[radius=%fem];"
                           % (legend.anchor, legend.margin))

    def _title(self):
        if self._plot.title is not None:
            self._latex.append("/background/legend",
                               r"\coordinate(title)at(current bounding box.north);")

            self._latex.append("/foreground",
                               r"\draw(title)++(0,1em)node[anchor=south]{%s};"
                               % self._plot.title)


    def _size(self):
        plot = self._plot

        self._latex.append("/background/bbox",
                           r"\fill[white](%f,%f)rectangle(%f,%f);"%(
                               plot.x.min, plot.y.min,
                               plot.x.max, plot.y.max
                           ))

        self._latex.append("/scale", r"\def\plotz@scalex{%f}"
                           % (plot.size_x*plot.scale / (plot.x.max-plot.x.min)))
        self._latex.append("/scale", r"\def\plotz@scaley{%f}"
                           % (plot.size_y*plot.scale / (plot.y.max-plot.y.min)))

    def _compile(self):
        with TmpDir() as tmp:
            with open(os.path.join(tmp, "standalone.tex"), "w") as f:
                f.write("%\n".join([
                    r"\errorstopmode",
                    r"\documentclass{standalone}",
                    r"\usepackage{plotz}",
                    r"\begin{document}",
                    r"\plotz{plotz}",
                    r"\end{document}",
                ]))

            with open(os.path.join(tmp, "plotz.tex"), "w") as f:
                self._latex.write(f)

            subprocess.call(["cp",
                             os.path.join(tmp, "plotz.tex"),
                             self._plot.output+".tex"])

            pdflatex = subprocess.Popen(["pdflatex", "-file-line-error", "standalone.tex"],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        stdin=subprocess.PIPE, cwd=tmp)
            pdflatex.stdin.close()

            context = 0
            error = re.compile(r"^.+:\d+: ")
            for line in pdflatex.stdout:
                line = line.decode()
                if error.match(line):
                    context = max(context, 3)
                if context > 0:
                    sys.stderr.write(line)
                    context -= 1

            if os.path.exists(os.path.join(tmp, "standalone.pdf")):
                subprocess.call(["cp",
                                 os.path.join(tmp, "standalone.pdf"),
                                 self._plot.output+".pdf"])


    @staticmethod
    def _index(index):
        return chr(ord('A')+index)
