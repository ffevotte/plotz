# Histograms

<img src="document.svg?raw=true&sanitize=true"/>

## Simple histogram

We discuss here how to get the first histogram shown in the left part of the
figure above.

### Plotting data as bars

Instead of drawing curves with the `Plot.plot()` method, it is possible to draw
bars with `Plot.hist()`:

<!---plotz include("plot.py", "# hist") -->
```python
    p.hist(hist)
```
<!---plotz end -->


### Setting bins on the *x* axis

By default, histogram bars are associated to abscissae 0,1,...,N. It is possible
to set the bin boundaries in the `Plot.histogram.bins` attribute. For *N* bars,
this should be a list of size *N+1*:

<!---plotz include("plot.py", "# bins") -->
```python
    p.histogram.bins = bins
```
<!---plotz end -->


## Handling multiple data series

Here is a more complex example which demonstrates the possibility to plot
histograms from multiple data series. This example produces the histogram
presented in the right part of the figure above. In this case, the first bar
from each series will be grouped together, and so on.

The gap between data series can be set using the `Plot.histogram.gap` attribute:
<!---plotz include("plot.py", "# gap") -->
```python
    p.histogram.gap = 1
```
<!---plotz end -->

The data series are simply provided by calling `Plot.hist()` multiple times:
<!---plotz include("plot.py", "# series") -->
```python
    header = nth(DataFile("immigration.dat", comment=None), 3)

    for i in range(1,5):
        p.hist(DataFile("immigration.dat"), col=i, title=header[i])
```
<!---plotz end -->

Note here how titles were automatically obtained from the data file: first, the data
file is opened without any comment marker so as to get all lines, including the
header. Then, we use the `nth` utility function (which is taken from the
`itertools` recipes) to get the fourth line from it.

<!---plotz head("immigration.dat", 5) -->
```
# IMMIGRATION BY REGION AND SELECTED COUNTRY OF LAST RESIDENCE
# (these data come from the gnuplot demo scripts)
#
#Region    Austria  Hungary  Belgium  Czechoslovakia  Denmark  France  Germany  Greece  Ireland
1891-1900  234081   181288   18167    -               50231    30770   505152   15979   388416
...
```
<!---plotz end -->


In such histograms, abscissae generally reflect discrete categories, rather than
a continuum of real values. In such instances, it makes more sense to explicitly
set tick labels. Since we did not specify bins in this case, abscissae
associated to the groups bars are simply integer values. In this example, we
extract tick labels from the first column in the data file, and associate each
label to its index using `enumerate()`:
<!---plotz include("plot.py", "# ticks") -->
```python
    p.x.ticks = enumerate([row[0] for row in DataFile("immigration.dat")])
```
<!---plotz end -->

Tick labels are now very wide; we rotate them to avoid collisions:
<!---plotz include("plot.py", "# ticks rotate") -->
```python
    p.x.tick_rotate = -45
```
<!---plotz end -->
