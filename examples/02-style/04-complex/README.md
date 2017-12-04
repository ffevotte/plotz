# More complex example

This example builds a more complex figure in order to demonstrate how all
styling options can be combined.

<img src="fourier.svg?raw=true&sanitize=true"/>

Here are a few things to note:

- The styling of line thickness is overridden, explicitly setting new
  thicknesses and attributing them to the drawn lines.
  <!---plotz include("plot.py", "# thickness", "    ") -->
```python
        p.style.thickness = ["ultra thin", "thick", "ultra thick"]
    
        p.plot(DataFile("fourier.dat"), title="SI").style({
            "thickness": 2, # ultra thick
        })
```
  <!---plotz end -->

- Lines 2 to 4 ("DSA", "PDSA(2)" and "PDSA(3)") completely coincide. Markers are
  used to distinguish between one another. Note how markers are equally spaced,
  but set in phase opposition so that they appear alternatively.
  <!---plotz include("plot.py", "# markers", "    ") -->
```python
        p.plot(DataFile("fourier.dat"), title="PDSA(2)", col=(0,3)).style({
            "thickness": 0,
            "markers": 7,
            "markers_filter": Markers.equallySpaced(2, 0),
        })
    
        p.plot(DataFile("fourier.dat"), title="PDSA(3)", col=(0,5)).style({
            "thickness": 0,
            "markers": 5,
            "markers_filter": Markers.equallySpaced(2, 1),
        })
```
  <!---plotz end -->
 
- Marker types are explicitly set so that lines "PDSA(2)" and "PDSA(3)"
  respectively use marker indices 7 (black triangle) and 5 (bullet).
  
