# Axes and scales

<img src="plot.svg?raw=true&sanitize=true"/>

The `x` and `y` attributes of the `Plot` object are of type `Axis`. They are
used to handle everything related to axes: scale, ticks and labels.


## Linear and logarithmic scales

The axis scale can be changed using the `Axis.scale` attribute. By default, each
axis has a linear scale (`Axis.linear`), but can be set to use a logarithmic
scale (`Axis.logarithmic`):

<!---plotz include("plot.py", "# log scale") -->
```python
    p.y.scale = Axis.logarithmic
```
<!---plotz end -->


## Axis labels

Axes have of course a label:
<!---plotz include("plot.py", "# label") -->
```python
    p.y.label = r"\# iter"
```
<!---plotz end -->

which can be rotated by 90 degrees. This is useful when the label of the *y*
axis is wide:
<!---plotz include("plot.py", "# label rotate") -->
```python
    p.y.label_rotate = True
```
<!---plotz end -->

Depending on axes ticks, the default label position might be too close / too far
from the axis. It can be adjusted using the `Axis.label_shift` attribute:
<!---plotz include("plot.py", "# label shift") -->
```python
    p.y.label_shift *= 0.8
```
<!---plotz end -->


## Axis range and ticks

By default, axes ranges are computed automatically using the plotted data. But
they can be manually adjusted using the `min` or `max` attributes as
needed. Note that values must be provided in the axis scale. The `scale`
attribute can help with this:
<!---plotz include("plot.py", "# range") -->
```python
    p.x.max = p.x.scale(0.6)
```
<!---plotz end -->

PlotZ tries to determine automatically where to place the axis ticks and how to
label them. But this can be overriden using the `Axis.ticks` attribute.

If `ticks` is a number, it is taken to be the distance between ticks (again,
this should be scaled like the axis). Ticks start from the beginning of the axis
range and increase by the specified amount.
<!---plotz include("plot.py", "# ticks: step") -->
```python
    p.x.ticks = 1
```
<!---plotz end -->

`ticks` can also be a list of tick positions:
<!---plotz include("plot.py", "# ticks: list") -->
```python
    p.y.ticks = [1, 2, 3]
```
<!---plotz end -->

The list of tick positions can also be a list of `(position, label)` tuples, in
which case tick labels are explicitly specified. If, like above, only positions
are specified, tick labels are derived from the positions using the function
provided in the `Axis.tick_format` attribute. The default tick formatting
function pretty-prints the tick position as a floating-point value for linear
axes. For logarithmic axes, it uses a *10<sup>n</sup>* representation (like for
the *x* axis in the example above).

In this example, we revert to a standard, linear representation for the *y*
axis, even though it uses a logarithmic scale. This example uses the `ppfloat`
utility function (from the `plotz.utils` module). This function pretty-prints a
floating-point value by removing trailing zeros.
<!---plotz include("plot.py", "# ticks format") -->
```python
    p.y.tick_format = lambda x: ppfloat(10**x)
```
<!---plotz end -->
