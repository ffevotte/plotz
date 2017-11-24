# Plotting python functions

<img src="plot.svg?raw=true&sanitize=true"/>

This example demonstrates how to plot the data computed by python functions.

## Basic usage

The basic way to plot functions is to use the `Function` data generator.
You give it a function, and optionally a number of samples (defaulting to 100)
and a range (see below).

<!---plotz include("plot.py", "#line1") -->
```python
    p.plot(Function(sin, samples=50, range=(0, pi)),
           title=r"$\sin(x)$")
```
<!---plotz end -->

You can of course give it functions that you define yourself, or `lambda`s for
short definitions:

<!---plotz include("plot.py", "#line2") -->
```python
    p.plot(Function(lambda x: sin(2*x), range=(0, pi)),
           title=r"$\sin(2\,x)$")
```
<!---plotz end-->


## Getting the range automatically

If you want the range to be inherited from previously plotted data, you can just
omit the `range` argument:

<!---plotz include("plot.py", "#line3") -->
```python
    p.plot(Function(lambda x: sin(3*x)),
           title=r"$\sin(3\,x)$")
```
<!---plotz end-->
