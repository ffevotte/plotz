# Markers

This example demonstrates how to handle point markers.

<img src="plot.svg?raw=true&sanitize=true"/>

## Draw markers, lines or both

The default plotting style is to only draw lines, and no markers. This behaviour
can be changed by restyling plot lines after drawing them, setting their
`markers` attribute:

<!---plotz include("plot.py", "# markers") -->
```python
    p.plot(Function(fun[0], samples=20, range=(0, 1)), title=r"line 0").style({
        "markers": True,
    })
```
<!---plotz end -->

If the `markers` attribute is set to `True` (as in this example), the next
available marker is chosen. Otherwise, the value set to `markers` should be the
index of the desired marker in the `Plot.style.marker` list. The above plot
shows a preview of some of the predefined markers in PlotZ.

It is of course possible to de-activate the drawing of the line at the same
time, so that data is only represented as a series of points:

<!---plotz include("plot.py", "# no line") -->
```python
    p.plot(Function(fun[5], samples=20, range=(0, 1)), title=r"line 5").style({
        "markers": True,
        "line": False
    })
```
<!---plotz end -->


## Control the spacing of markers

If the data contains too many points, it may not be desirable to draw markers
for all of them. The `marker_filter` styling attribute allows controlling which
points get marked.

`plotz.utils.Markers` defines some standard markers filtering policies.
A first, basic way to restrict the number of markers is to only draw a certain
proportion of them. This is the purpose of the `oneInN` filter. With the
following setup, only half of the data points get marked:
<!---plotz include("plot.py", "# oneInN") -->
```python
    p.plot(Function(fun[1], samples=20, range=(0, 1)), title=r"line 1").style({
        "markers": True,
        "markers_filter": Markers.oneInN(2),
    })
```
<!---plotz end -->

An optional argument allows specifying which data point gets marked first. In
the example above, the second data point gets the first marker, so that markers
of "line 1" and "line 2" are in phase opposition.
<!---plotz include("plot.py", "# oneInN start") -->
```python
    p.plot(Function(fun[2], samples=20, range=(0, 1)), title=r"line 2").style({
        "markers": True,
        "markers_filter": Markers.oneInN(2, 1),
    })
```
<!---plotz end -->


`equallySpaced` provides another policy to filter markers: whith this setting,
the horizontal distance between marks is kept as constant as possible (in this
example, to 0.15).
<!---plotz include("plot.py", "# equallySpaced") -->
```python
    p.plot(Function(fun[3], samples=100, range=(0, 1)), title=r"line 3").style({
        "markers": True,
        "markers_filter": Markers.equallySpaced(0.15),
    })
```
<!---plotz end -->

Again, an optional argument allows setting the position of the first marker, so
as to determine if marker positions of two separate data series should be
aligned or not (as is the case for lines 3 and 4 above).
