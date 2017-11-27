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
import shutil
import os
import subprocess
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

class LatexOutput:
    def __init__(self):
        self._lines = [r"\makeatletter", [], r"\makeatother"]
        self._index = {}

    def _getKey(self, path):
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

    def append(self, key, a):
        (lines, _) = self._getKey(key)
        lines.append(a)

        return self

    def insert(self, key, before=None, after=None):
        path = key.split("/")
        name = path[-1]
        path = path[:-1]
        (lines, index) = self._getKey(path)

        lines += ["", "%% %s "%key]
        if before is not None:
            lines.append(before)

        index[name] = (len(lines), {})
        lines.append([])

        if after is not None:
            lines.append(after)

        return self

    def replace(self, key, a):
        (lines, index) = self._getKey(key)
        del lines[1:]
        lines += a
        index.clear()

        return self

    def write(self, f, indent=""):
        def _write(f, l, indent):
            if isinstance(l, str):
                f.write(indent+l+"%\n")
            else:
                for ll in l:
                    _write(f, ll, indent+"  ")

        for l in self._lines:
            _write(f, l, indent)


class TikzGenerator(object):
    def __init__(self, plot):
        self._plot = plot

        self._latex = (
            LatexOutput()
            .insert("/header")
            .insert("/header/colors")
            .insert("/header/markers")
            .insert("/header/patterns")
            .insert("/header/thickness")
            .insert("/background", r"\def\plotz@background{", "}")
            .insert("/background/bbox")
            .insert("/background/legend")
            .insert("/lines"     , r"\def\plotz@lines{", "}")
            .insert("/foreground", r"\def\plotz@foreground{", "}")
            .insert("/foreground/axes")
            .insert("/foreground/legend")
            .insert("/legend"    , r"\def\plotz@legend{", "}")
            .insert("/scale"))

        self._color = None
        self._marker = None
        self._pattern = None
        self._thickness = None

        self._legend_shift = iter(range(100))


    def run(self):
        self._style()
        self._size()
        self._legend()
        self._title()

        self._axis(self._plot.x)
        self._axis(self._plot.y)

        for line in self._plot.lines:
            self._line(line)

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
        marker = line.marker
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
            self._latex.append("/legend","".join([
                r"\draw[%s](0,%fem)%s++(2em,0)"
                % (options["style"], shift, options["draw"]),
                r"node[right,inner sep=2pt,black]{%s};"%line.title,
            ]))
            self._latex.append("/legend",
                               "\draw[%s](1em,%fem)%s;"
                               % (options["style"], shift, options["marker"]))

    def _line(self, line):
        options = self._line_options(line)

        self._line_legend(line, options)

        self._latex.append("/lines", r"\draw[%s]" % options["style"])
        for subline in line.points:

            points = iter(subline)
            (x,y) = next(points)
            self._latex.append("/lines",
                               "  (%.15f,%.15f)%s" % (x, y, options["marker"]))

            for (x,y) in points:
                self._latex.append("/lines",
                                   "%s(%.15f,%.15f)%s" % (options["draw"], x, y,
                                                          options["marker"]))

            self._latex.append("/lines", ";")

    def _axis(self, axis):

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
        def coord(x, y):
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
                           % (coord(axis.min, axis.pos), coord(axis.max, axis.pos)))

        # Label
        if axis.label is not None:
            self._latex.append("/foreground/axes",
                               r"\draw(%s)++(%s)"
                               % (coord(0.5*(axis.min+axis.max), axis.pos),
                                  coord(0, "-%fem"%axis.label_shift)) +
                               r"node[%s]{%s};" % (label_options, axis.label))

        # Ticks
        for (x, label) in axis.ticks:
            self._latex.append("/foreground/axes", [
                r"\draw(%s)++(%s)--++(%s)" % (coord(x, axis.pos),
                                              coord(0, "0.5em"),
                                              coord(0, "-1em")),
                r"   node[%s]{%s};" % (tick_options, label)])


    def _legend(self):
        legend = self._plot.legend

        if isinstance(legend.position, str):
            position = "current bounding box." + legend.position
        else:
            position = "%f,%f" % legend.position

        self._latex.append("/background/legend",
                           r"\node(legend)at(%s){};"
                           % (position))
        self._latex.append("/foreground",
                           r"\node[anchor=%s,inner sep=1em]at(legend){\usebox{\plotz@boxlegend}};"
                           % (legend.anchor))

    def _title(self):
        if self._plot.title is not None:
            self._latex.append("/background/legend",
                               r"\node(title)at(current bounding box.north){};")

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
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                                        cwd=tmp)
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
