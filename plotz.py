import sys
import tempfile
import os
import shutil
import subprocess

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

class LatexOutput:
    def __init__(self):
        self._lines = []
        self._index = {}

    def _getKey(self, path):
        if isinstance(path, str):
            path = path.split("/")

        lines = self._lines
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

    def insert(self, key, before=None, after=None):
        path = key.split("/")
        name = path[-1]
        path = path[:-1]
        (lines, index) = self._getKey(path)

        if before is not None:
            lines.append(before)

        index[name] = (len(lines), {})
        lines.append(["%%\n%% %s\n"%key])

        if after is not None:
            lines.append(after)

    def replace(self, key, a):
        (lines, index) = self._getKey(key)
        del lines[1:]
        lines += a
        index.clear()

    def write(self, f):
        def _write(f,l):
            if isinstance(l, str):
                f.write(l+"%\n")
            else:
                for ll in l:
                    _write(f, ll)
        #
        for l in self._lines:
            _write(f,l)


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
        self._orientation = orientation
        self._setup = True
        self.setScale(lambda x: x)

        self.label = None
        self.label_rotate = False
        if orientation == 1:
            self.label_shift = 2
        else:
            self.label_shift = 3

        self.min = float("inf")
        self.max = float("-inf")

        self.tick = None
        self.ticks = None
        self.tick_format = self._tick_format


    def setScale(self, fun):
        if not self._setup:
            sys.stderr.write("Plotz error: can not change axis scale after setup")
            return

        self._scale = fun

    def scale(self, x):
        return self._scale(x)

    def freeze(self):
        self._setup = False

    def _coord(self, x, y):
        """Exchange x, y coordinates depending on the axis orientation.
x here is always taken to be along the axis, and
y in the orthogonal direction."""
        if isinstance(x, float):
            x = "%.15f" % x
        if isinstance(y, float):
            y = "%.15f" % y

        if self._orientation == 1:
            return "%s,%s" % (x, y)
        return "%s,%s" % (y, x)

    def _tick_format(self, x):
        """Default implementation for the ticks format.
Pretty print regular values and use 10^x in the case of logarithmic scale."""
        if self.scale == "log":
            label = "$10^{%d}$" % x
        else:
            label = ppfloat(x)
        return label

    def update(self):
        if self.tick is None:
            delta = (self.max-self.min)
            factor = 1
            while delta < 10:
                delta *= 10
                factor *= 10
            self.tick = round(delta/5.) / factor
            self.min = round(self.min*factor) / factor
            self.max = round(self.max*factor) / factor

        if self.ticks is None:
            self.ticks = []

            x = self.min
            factor = 1
            while x != round(x) and abs(x) < 0.9:
                x *= 10
                factor *= 10
            x = round(x)/factor

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

    def output(self, position, latex):
        if self._orientation == 1:
            tick_options = "below"
            label_options = tick_options
        else:
            tick_options = "left"
            label_options = tick_options
            if self.label_rotate:
                label_options += ",rotate=90,anchor=south,inner sep=1em"

        # Axis
        latex.append("/background/axes", [
            r"\draw(%s)" % self._coord(self.min, position),
            r"   --(%s);" % self._coord(self.max, position)])

        # Label
        if self.label is not None:
            latex.append("/background/ticks",
                         r"\draw (%s)++(%s)"
                         % (self._coord(0.5*(self.min+self.max),position),
                            self._coord(0, "-%fem"%self.label_shift)) +
                         r"node[%s]{%s};" % (label_options, self.label))

        # Ticks
        for (x, label) in self.ticks:
            latex.append("/background/ticks", [
                r"\draw(%s)++(%s)--++(%s)" % (self._coord(x,position),
                                              self._coord(0,"0.5em"),
                                              self._coord(0,"-1em")),
                r"   node[%s]{%s};" % (tick_options, label)])

class Legend(object):
    def __init__(self):
        self._index = 0
        self._latex = []

    def add(self, line, marker, index, title):
        y = 1.1 * self._index
        self._index -= 1

        if line:
            line = "--"
        else:
            line = ""

        self._latex.append(r"\draw[line%s](0,%fem)%s(2em,%fem)" % (index, y, line, y)
                           + r"node[right, inner sep=2pt]{\strut %s};" % title)
        if marker:
            self._latex.append(r"\node[line%s]at(1em,%fem){\marker%s};" % (index, y, index))

    def latex(self):
        return self._latex

class Plot:
    def __init__(self, output):
        self._output = output

        self.line = 0
        self.x = Axis(1)
        self.y = Axis(2)
        self._legend = Legend()

        self.size_x = 266.66
        self.size_y = 200.00
        self.scale  = 1.0

        self.latex = LatexOutput()
        self.latex.append("/", r"\makeatletter")
        self.latex.insert("/header")
        self.latex.insert("/background", r"\def\plotz@background{", "}")
        self.latex.insert("/background/axes")
        self.latex.insert("/background/legend")
        self.latex.insert("/background/ticks")
        self.latex.insert("/lines"     , r"\def\plotz@lines{", "}")
        self.latex.insert("/foreground", r"\def\plotz@foreground{", "}")
        self.latex.insert("/legend"    , r"\def\plotz@legend{", "}")
        self.latex.insert("/scale")
        self.latex.append("/", r"\makeatother")

        self.latex.insert("/header/colors")
        self.colormap()

        self.latex.insert("/header/lines")
        self.latex.append("/header/lines", [
            r"\tikzstyle{lineA}=[very thick, color1]",
            r"\tikzstyle{lineB}=[very thick, color2]",
            r"\tikzstyle{lineC}=[very thick, color3]",
            r"\tikzstyle{lineD}=[very thick, color4]",
            r"\tikzstyle{lineE}=[very thick, color5]",
            r"\tikzstyle{lineF}=[very thick, color6]",
            r"\tikzstyle{lineG}=[very thick, color7]",
            r"\tikzstyle{lineH}=[very thick, color8]",
        ])

        self.latex.insert("/header/markers")
        self.latex.append("/header/markers", [
            r"\def\markerA{$+$}",
            r"\def\markerB{$\circ$}",
            r"\def\markerC{$\Box$}",
            r"\def\markerD{$\triangle$}",
            r"\def\markerE{$\times$}",
            r"\def\markerF{$\bullet$}",
            r"\def\markerG{$\blacksquare$}",
            r"\def\markerH{$\blacktriangle$}",
        ])

    def colormap(self, name=None):
        """Setup a colormap"""

        # Default colormap
        c = ["377eb8", "e41a1c", "4daf4a", "984ea3", "ff7f00", "a65628", "f781bf", "ffff33"]

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

        self.latex.replace("/header/colors",
                           [r"\definecolor{color%d}{HTML}{%s}" % (i+1, c[i])
                            for i in xrange(len(c))])

    def lineStyle(self, index, style):
        self.latex.append("/header/lines",
                          r"\tikzset{line%s/.append style={%s}}" % (self._index(index), style))

    def markerShape(self, index, marker):
        self.latex.append("/header/markers",
                          r"\def\marker%s{%s}"%(self._index(index), marker))

    def plot(self, data, title=None, line=True, points=False):
        self.line += 1
        if title is not None:
            self._legend.add(line, points, self._index(), title)

        self.latex.append("/lines", r"\draw[line%s]" % self._index())

        def coord(line, x, y):
            x = self.x.scale(x)
            self.x.min = min(x, self.x.min)
            self.x.max = max(x, self.x.max)

            y = self.y.scale(y)
            self.y.min = min(y, self.y.min)
            self.y.max = max(y, self.y.max)

            self.latex.append("/lines", "%s(%.15f,%.15f)%s"%(line,x,y,points))

        if line:
            line = "--"
        else:
            line = "  "

        if points:
            points = r"node{\marker%s}" % self._index()
        else:
            points = ""

        first = True
        for (x,y) in data:
            if first:
                first = False
                coord("  ", x, y)
            else:
                coord(line, x, y)

        self.latex.append("/lines", ";")


    def legend(self, position, anchor=None):
        if isinstance(position, str):
            if anchor is None:
                anchor = position
            position = "current bounding box." + position
        else:
            if anchor is None:
                anchor = "center"
            position = "%f,%f" % position

        self.latex.append("/background/legend",
                          r"\node(legend)at(%s){};"
                          % (position))
        self.latex.append("/foreground",
                          r"\node[anchor=%s,inner sep=1em]at(legend){\usebox{\plotz@boxlegend}};"
                          % (anchor))

    def tikz(self, tikz):
        self.latex.append("/foreground", tikz)


    def _index(self, line=None):
        index = self.line
        if line is not None:
            index = line

        return chr(ord("A")+index-1)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return

        self.latex.append("/scale", r"\def\plotz@scalex{%f}" % (self.size_x*self.scale / (self.x.max-self.x.min)))
        self.latex.append("/scale", r"\def\plotz@scaley{%f}" % (self.size_y*self.scale / (self.y.max-self.y.min)))

        self.latex.append("/legend", self._legend.latex())

        self.x.update()
        self.y.update()
        self.x.output(self.y.min, self.latex)
        self.y.output(self.x.min, self.latex)

        with TmpDir() as tmp:
            with open(os.path.join(tmp, "standalone.tex"), "w") as f:
                f.write("%\n".join([
                    r"\nonstopmode",
                    r"\documentclass{standalone}",
                    r"\usepackage{plotz}",
                    r"\begin{document}",
                    r"\plotz{plotz}",
                    r"\end{document}"
                ]))

            with open(os.path.join(tmp, "plotz.tex"), "w") as f:
                self.latex.write(f)

            subprocess.call(["cp",
                             os.path.join(tmp, "plotz.tex"),
                             self._output+".tex"])

            subprocess.call(["pdflatex", "standalone.tex"],
                            cwd=tmp)

            subprocess.call(["cp",
                             os.path.join(tmp, "standalone.pdf"),
                             self._output+".pdf"])


def Function(fun, samples=100, range=(0,1)):
    x0 = range[0]
    x1 = range[1]
    dx = float(x1-x0)/(samples-1)
    for i in xrange(samples):
        x = x0 + i*dx
        yield(x, fun(x))

def columns(i, j):
    def fun(fields):
        return (fields[i], fields[j])
    return fun

def DataFile(filename, fun=columns(0,1)):
    with open(filename, "r") as f:
        for line in f:
            fields = [float(v) for v in line.strip().split(" ")]
            yield fun(fields)


def test1():
    import math
    import numpy

    N = 100
    data = numpy.zeros((N,3))
    for i in xrange(N):
        x = (i+0.5)*1/float(N)
        data[i,:] = [x, math.sin(math.pi*x), math.sin(math.pi*x*2)]

    with Plot("test") as plot:
        plot.x.label = "$x$"
        plot.y.label = "$y$"
        plot.y.label_rotate = True
        plot.y.tick = 0.25
        plot.y.tick_format = lambda x: "%.2f"%x

        plot.size_y *= 0.8
        #plot.scale *= 1.63208

        plot.plot(Function(lambda x: math.sin(0.5*math.pi*x), samples=50, range=(0,1)),
                  line=False, points=True,
                  title=r"function $\sin(\frac{\pi x}{2})$")

        plot.plot(DataFile("essai.dat"),
                  title="data file")

        plot.plot(data[:, [0,2]],
                  title="numpy array")

        plot.tikz(r"""
           \draw[->](0.56,0)
             node[anchor=south west, fill=white]{\texttt{tikz} annotations on the figure}
             -- ++(-1em,-1em);""")

        plot.legend("south west")

if __name__ == "__main__":
    test1()
