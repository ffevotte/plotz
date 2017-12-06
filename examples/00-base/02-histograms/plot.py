import numpy
from math import pi, sqrt, exp
from plotz import Plot, Function, DataFile
numpy.random.seed(42)

mu, sigma = 100, 15
n = 10000
x = mu + sigma * numpy.random.randn(n)
hist, bins = numpy.histogram(x, bins=30)

factor = (bins[1]-bins[0]) * n

with Plot("plot") as p:
    p.title = "example of PlotZ histogram"

    p.x.min = 40
    p.x.max = 160
    p.x.ticks = 20
    p.x.label = r"$x$"

    p.y.min = 0
    p.y.ticks = 200
    p.y.label = r"\# occurrences"
    p.y.label_rotate = True
    p.y.label_shift *= 0.8

    # bins
    p.histogram.bins = bins
    # bins

    # hist
    p.hist(hist)
    # hist

    def normal(x):
        return factor/sqrt(2*pi*sigma**2) * exp(-(x-mu)**2/(2*sigma**2))

    p.style.pattern[0] = "dashed"
    p.plot(Function(normal))


from plotz.utils import nth
with Plot("immigration") as p:
    p.title = "US immigration from Northern Europe"

    # gap
    p.histogram.gap = 1
    # gap

    # series
    header = nth(DataFile("immigration.dat", comment=None), 3)

    for i in range(1,5):
        p.hist(DataFile("immigration.dat"), col=i, title=header[i])
    # series

    # ticks
    p.x.ticks = enumerate([row[0] for row in DataFile("immigration.dat")])
    # ticks

    # ticks rotate
    p.x.tick_rotate = -45
    # ticks rotate

    p.y.min = 0
    p.y.ticks = 100000
