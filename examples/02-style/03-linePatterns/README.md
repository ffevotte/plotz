# Line pattern and thickness

This example demonstrates how to change the line pattern or thickness. This is
especially useful for monochrome plots.

<img src="monochrome.svg?raw=true&sanitize=true"/>

## Drawing dashed lines

By default, all lines are solid. In order to load and use the set of pre-defined
line patterns, simply use the `Plot.style.dashed()` method:

<!---plotz include("plot.py", "# dashed") -->
```python
    p.style.dashed()
    p.style.colormap("monochrome")
```
<!---plotz end -->

This combines neatly with the "monochrome" colormap, which sets all line colors
to black. The following figure illustrates the set of pre-defined line patterns:

<img src="plot.svg?raw=true&sanitize=true"/>

## Setting line thickness

By default, all lines are "very thick". There is no helper function to load a
set of pre-defined line thicknesses. Instead, the line thickness can be changed
by setting the `Plot.style.thickness` list. In the more complex example at the
top of the page, different line thicknesses have been defined to help better
distinguish the lines:
<!---plotz include("plot.py", "# line thickness") -->
```python
    p.style.thickness[0] = "ultra thick"
    p.style.thickness[1] = "ultra thick"
    p.style.thickness[2] = "very thick"
```
<!---plotz end -->

Also note that, in that example, the last line uses a dotted pattern (pattern 3)
instead of the dashdotted pattern it should have defaulted to. This is because a
line pattern was explicitly set for it:
<!---plotz include("plot.py", "# explicit dashed pattern") -->
```python
    p.plot(DataFile("mydata.dat"), col=(0,3), title=r"PDSA(6)").style({
        "pattern": 3,
    })
```
<!---plotz end -->
