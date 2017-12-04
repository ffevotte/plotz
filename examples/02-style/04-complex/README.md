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

- Lines "DSA", "PDSA(2)" and "PDSA(3)" completely coincide. Markers are used to
  distinguish between one another. Note how markers are equally spaced, but set
  in phase opposition so that they appear alternatively.

- Marker types are explicitly set so that lines "PDSA(2)" and "PDSA(3)"
  respectively use marker indices 7 (black triangle) and 5 (bullet).
  
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
 
- The last line (which has index 6) is styled entirely manually: it is
  explicitly set to be dashed and black by overriding the default styling for
  that line index
  <!---plotz include("plot.py", "# black dashed", "    ") -->
```python
        p.style.pattern[6] = "dashed"
    
        p.style.color[6] = "000000"    # black = "#000000"
    
        p.plot(DataFile("fourier.dat"), col=(0,6),
               title=r"$\rho_{\text{\sc pdsa}}^{\text{max}}(3)$").style({
            "thickness": 1,
        })
```
  <!---plotz end -->
