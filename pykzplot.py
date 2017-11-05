#!/usr/bin/python

import math
import subprocess
import tempfile
import shutil
import os


class TmpDir(object):
    """Temporary directory
Useable in a `with` statement. Automatically takes care of deleting itself."""
    #pylint: disable=too-few-public-methods

    def __init__(self):
        self._name = tempfile.mkdtemp(prefix="pykzplot")

    def __enter__(self):
        return self._name

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._name)


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


class Line(object):
    "Drawn line. To be used to draw the legend."
    #pylint: disable=too-few-public-methods

    def __init__(self, index, title, line, points):
        self.index = index
        self.title = title
        self.line = line
        self.points = points


class Axis(object):
    "Plot axis"
    #pylint: disable=too-many-instance-attributes

    def __init__(self, plot, orientation):
        """Constructor
plot: Plot instance to which this axis belongs;
orientation: 1 for x, 2 for y."""
        self._plot = plot
        self._orientation = orientation

        self.min = 0
        self.max = 10

        self.scale = "rect"
        self.tick = 1
        self.ticks = None
        self.label = None
        self.label_rotate = False
        self.tick_size = 5
        self.subtick = 0
        self.tick_format = self._tick_format

        if orientation == 1:
            self.label_shift = 18
        else:
            self.label_shift = 24

    def _coord(self, s, t):
        """Exchange s, t coordinates depending on the axis orientation.
s here is always taken to be along the axis, and
t in the orthogonal direction."""
        if isinstance(s, float):
            s = "%.15f" % s
        if isinstance(t, float):
            t = "%.15f" % t

        if self._orientation == 1:
            return "%s,%s" % (s, t)
        return "%s,%s" % (t, s)

    def _tick_format(self, x):
        """Default implementation for the ticks format.
Pretty print regular values and use 10^x in the case of logarithmic scale."""
        if self.scale == "log":
            label = "$10^{%d}$" % x
        else:
            label = ppfloat(x)
        return label

    def points(self, samples):
        """Return a list of regularly spaced points along the array"""
        dx = float(self.max - self.min) / samples

        if self.scale == "log":
            return [10**(self.min+i*dx) for i in xrange(samples+1)]
        return [self.min+i*dx for i in xrange(samples+1)]

    def update(self):
        """Update ticks position.
This function must be called once the axis has been set up, but before anything
depending on it is drawn."""
        if self.ticks is None:
            self.ticks = []
            x = 0
            while x <= self.max:
                self.ticks.append(x)
                x += self.tick
            x = -self.tick
            while x >= self.min:
                self.ticks.append(x)
                x -= self.tick

        def normalize_tick(tick):
            try:
                (x, label) = tick
            except:
                x = tick
                label = self.tick_format(x)
            return (x, label)
        self.ticks = [normalize_tick(t) for t in self.ticks]

    def draw(self, position):
        """Output the necessary TikZ code to draw the axis"""
        orientation = self._orientation
        out = ["%%\n%% AXIS %d " % orientation]

        if orientation == 1:
            tick_position = "below"
            label_position = "below"
            scale = r"\pykz@Y"
        else:
            tick_position = "left"
            label_position = "left"
            if self.label_rotate:
                label_position += ",rotate=90,anchor=south,inner sep=1em"
            scale = r"\pykz@X"

        tick_size = self.tick_size
        label_shift = self.label_shift

        # Axis
        out += [
            r"\draw(%s)" % self._coord(self.min, position),
            r"   --(%s);" % self._coord(self.max, position)]

        # Label
        if self.label is not None:
            out += [
                r"\node at (%s)"
                % self._coord(0.5*(self.min+self.max),
                              "%.15f-%.15f/%s" % (position, label_shift, scale)),
                r"   [%s]{%s};" % (label_position, self.label)]

        # Ticks
        for (x, label) in self.ticks:
            out += [
                r"\draw(%s)" % self._coord("%.15f"%x,
                                           "%.15f+%.15f/%s"
                                           %(position, tick_size, scale)),
                r"   --(%s)" % self._coord("%.15f"%x,
                                           "%.15f-%.15f/%s"
                                           %(position, tick_size, scale)),
                r"   node[%s]{%s};" % (tick_position, label)]

        # Subticks
        if self.subtick > 0:
            x = self.min
            while x <= self.max:
                label = self.tick_format(x)
                out += [
                    r"\draw[style=help lines]",
                    r"   (%s)"   % self._coord(x, position+tick_size/2),
                    r" --(%s)," % self._coord(x, position-tick_size/2)]
                x += self.subtick

        self._plot._layer["foreground"] += out

class Plot(object):
    """2D plot"""

    def __init__(self, output):
        """Constructor"""
        self.scale = [1.5, 1]

        self.x = Axis(self, 1)
        self.y = Axis(self, 2)

        self._output = output
        self.line = 0
        self._lines = []
        self._layer = {"background": [],
                       "lines": [],
                       "foreground": []}

        self._layer["header"] = [
            r"\tikzstyle{lineA}=[very thick, color1]",
            r"\tikzstyle{lineB}=[dashed, dash pattern=on 0.55em off 0.55em, very thick, color2]",
            r"\tikzstyle{lineC}=[very thick, color3]",
            r"\tikzstyle{lineD}=[very thick, color4]",
            r"\tikzstyle{lineE}=[very thick, color5]",
            r"\tikzstyle{lineF}=[very thick, color6]",
            r"\tikzstyle{lineG}=[very thick, color7]",
            r"\tikzstyle{lineH}=[very thick, color8]",
            "",
            r"\def\markerA{$+$}",
            r"\def\markerB{$\circ$}",
            r"\def\markerC{$\Box$}",
            r"\def\markerD{$\triangle$}",
            r"\def\markerE{$\times$}",
            r"\def\markerF{$\bullet$}",
            r"\def\markerG{$\blacksquare$}",
            r"\def\markerH{$\blacktriangle$}",
        ]
        self.colormap()

    def _axes(self):
        self.x.draw(self.y.min)
        self.y.draw(self.x.min)

    def _line_index(self, line=None):
        if line is None:
            index = self.line
        else:
            index = line.index

        return chr(ord("A")+index-1)

    def colormap(self, name=None):
        """Setup a colormap"""

        c = ["377EB8",
             "E41A1C",
             "4DAF4A",
             "984EA3",
             "FF7F00",
             "A65628",
             "F781BF",
             "FFFF33"]
        if name == "paired":
            c = ['a6cee3', '1f78b4', 'b2df8a', '33a02c', 'fb9a99', 'e31a1c', 'fdbf6f', 'ff7f00']
        if name == "dark":
            c = ['1b9e77', 'd95f02', '7570b3', 'e7298a', '66a61e', 'e6ab02', 'a6761d', '666666']
        if name == "spectral8":
            c = ['d53e4f', 'f46d43', 'fdae61', 'fee08b', 'e6f598', 'abdda4', '66c2a5', '3288bd']
        if name == "spectral7":
            c = ['d53e4f', 'fc8d59', 'fee08b', 'ffffbf', 'e6f598', '99d594', '3288bd']
        if name == "spectral6":
            c = ['d53e4f', 'fc8d59', 'fee08b', 'e6f598', '99d594', '3288bd']
        if name == "spectral5":
            c = ['d7191c', 'fdae61', 'ffffbf', 'abdda4', '2b83ba']
        if name == "spectral4":
            c = ['d7191c', 'fdae61', 'abdda4', '2b83ba']

        self._layer["header"] += [r"\definecolor{color%d}{HTML}{%s}" % (i+1, c[i])
                                  for i in xrange(len(c))]

    def style(self, line, style):
        self._layer["header"].append(r"\tikzset{%s/.append style={%s}}" % (line, style))

    def __enter__(self):
        """Begin outputting TikZ code for the current plot"""
        self.line = 0
        self._lines = []

        self.x.update()
        self.y.update()

        self.scale[0] *= 200 / (self.x.max-self.x.min)
        self.scale[1] *= 200 / (self.y.max-self.y.min)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish outputting TikZ code for the current plot (including axes).
The graph is then rendered."""
        self._axes()

        def writelines(filename, *args):
            with open(filename, "w") as f:
                for a in args:
                    if isinstance(a, str):
                        f.write(a)
                    if isinstance(a, list):
                        f.write("%\n".join(a))
                    f.write("%\n")

        with TmpDir() as tmpdir:
            writelines(
                os.path.join(tmpdir, "standalone.tex"),
                r"\documentclass{standalone}",
                r"\usepackage{pykzplot}",
                r"\begin{document}",
                r"\pykzplot{pykzplot}",
                r"\end{document}",
            )

            writelines(
                os.path.join(tmpdir, "pykzplot.tex"),
                r"\makeatletter",
                self._layer["header"],
                "", "",
                r"\def\pykzplot@scalex{%s}" % self.scale[0],
                r"\def\pykzplot@scaley{%s}" % self.scale[1],
                "", "",
                r"\def\pykzplot@background{", self._layer["background"], "}",
                "",
                r"\def\pykzplot@lines{", self._layer["lines"], "}"
                "",
                r"\def\pykzplot@foreground{", self._layer["foreground"], "}",
                r"\makeatother",
            )

            subprocess.call(["cp",
                             os.path.join(tmpdir, "pykzplot.tex"),
                             self._output+".tex"])

            subprocess.call(["pdflatex", "standalone"],
                            cwd=tmpdir)
            subprocess.call(["cp",
                             os.path.join(tmpdir, "standalone.pdf"),
                             self._output+".pdf"])



    def xgrid(self):
        """Output the necessary TikZ code to draw a grid"""
        self._layer["background"].append("%\n% GRID X ")
        for (x, _) in self.x.ticks:
            self._layer["background"] += [
                r"\draw[style=help lines]",
                r"   (%.15f,%.15f)--" % (x, self.y.min),
                r"   (%.15f,%.15f);"  % (x, self.y.max)]

    def ygrid(self):
        """Output the necessary TikZ code to draw a grid"""
        self._layer["background"].append("%\n% GRID Y ")
        for (y, _) in self.y.ticks:
            self._layer["background"] += [
                r"\draw[style=help lines]",
                r"   (%.15f,%.15f)--" % (self.x.min, y),
                r"   (%.15f,%.15f);"  % (self.x.max, y)]

    def grid(self):
        self.xgrid()
        self.ygrid()

    def legend(self, x0, y0):
        """Output the necessary TikZ code to draw the plot legend.
(x0, y0): position of the top-left corner of the legend"""
        k = 0
        self._layer["foreground"].append("%\n% LEGEND ")
        for l in self._lines:
            line = ""
            if l.line:
                line = "--"
            self._layer["foreground"] += [
                r"\draw[line%s]" % self._line_index(l),
                r"  (%f,%f-%d/\pykz@Y)%s" % (x0, y0, k, line),
                r"  (%f+20/\pykz@X,%f-%d/\pykz@Y)" % (x0, y0, k),
                r"  node[right,black,fill=white,inner sep=2pt]{%s};" % l.title]
            if l.points:
                self._layer["foreground"] += [
                    r"\node[line%s]" % self._line_index(l),
                    r"at(%f+10/\pykz@X,%f-%d/\pykz@Y)" % (x0, y0, k),
                    r"{\marker%s};" % self._line_index(l)]
            k += 15

    def plot(self, fun=None, data=None, datatransform=None, title=None,
             samples=1000, line=True, points=False):
        self.line += 1
        if title:
            self._lines.append(Line(self.line, title, line, points))

        self._layer["lines"].append("")
        self._layer["lines"].append(r"\draw[line%s]" % self._line_index())

        def plot_point(first, x, y):
            tikz = ""

            if y is None:
                return

            if line and (not first[0]):
                self._layer["lines"][-1] += "--"
            first[0] = False

            if self.x.scale == "log":
                x = math.log(x)/math.log(10)
            if self.y.scale == "log":
                y = math.log(y)/math.log(10)
            tikz += "  (%.15f,%.15f)" % (x, y)

            if points:
                tikz += r"node{\marker%s}" % self._line_index()

            self._layer["lines"].append(tikz)

        first = [True]
        if fun:
            for x in self.x.points(samples):
                y = fun(x)
                plot_point(first, x, y)

        if data:
            with open(data, "r") as f:
                for line in f:
                    lineData = [float(v) for v in line.strip().split(" ")]
                    if datatransform:
                        lineData = datatransform(lineData)
                    if lineData is not None:
                        plot_point(first, lineData[0], lineData[1])
        self._layer["lines"][-1] += ";"

    def tikz(self, s):
        """Add a custom bit of TikZ code to the plot."""
        self._layer["foreground"].append(s)


def test1():
    plot = Plot("essai1")

    plot.x.min = 0
    plot.x.max = math.pi/2
    plot.x.tick = 0.5
    plot.y.min = -1
    plot.y.max = 1
    plot.y.tick = 0.5

    with plot:
        for k in xrange(1, 9):
            plot.plot(fun=lambda x, K=k: K*math.cos(K*x)/8)

def test2():
    plot = Plot("essai2")
    plot.scale = [2, 2]

    plot.x.scale = "log"
    plot.x.min = -2
    plot.x.max = 2
    plot.x.tick = 1

    plot.y.scale = "log"
    plot.y.min = -7
    plot.y.max = 7
    plot.y.tick = 1

    with plot:
        for k in xrange(8):
            plot.plot(fun=lambda x, K=k: x**(K-3.5),
                      samples=10,
                      line=(k < 4),
                      points=True,
                      title="$k = %d$"%k)
        plot.grid()
        plot.legend(-0.5, 6.5)

def test3():
    with open("essai.dat", "w") as f:
        N = 1000
        for i in xrange(N):
            x = (i+0.5)/N
            f.write("%f %f %f\n" % (x,
                                    math.sin(x*math.pi),
                                    math.sin(2*x*math.pi)))

    plot = Plot("essai3")

    plot.x.min = 0
    plot.x.max = 1
    plot.x.tick = 0.2
    plot.x.label = "$x$"

    plot.y.min = -1.1
    plot.y.max = 1.1
    plot.y.ticks = [(i*0.5, "%d"%i) for i in xrange(-2, 3)]

    with plot:
        plot.grid()
        plot.plot(data="essai.dat",
                  title=r"$\sin(\pi\,x)$")
        plot.plot(data="essai.dat",
                  datatransform=lambda x: (x[0], x[2]),
                  title=r"$\sin(2\,\pi\,x)$")
        plot.legend(0.1, -0.6)


if __name__ == "__main__":
    test1()
    test2()
    test3()
