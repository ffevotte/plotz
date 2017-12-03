# Color schemes

<img src="document.svg?raw=true&sanitize=true"/>

## Predefined color schemes

A set of predefined color schemes are built in PlotZ. They can be selected using
the `Plot.style.colormap()` method. For example:

```python
    plot.style.colormap("paired")
```

The colors used in these themes come from the
excellent [ColorBrewer](http://colorbrewer2.org/) tool. We give below the
built-in themes description, along with their "Type" and "Scheme name" from
ColorBrewer.

- `default`: 8-color map with qualitatively varying colors
  ([Qualitative, Set1](http://colorbrewer2.org/#type=qualitative&scheme=Set1&n=8))
- `dark`: 8-color map with qualitatively varying colors, in darker tones
  ([Qualitative, Dark2](http://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=8))
- `paired`: 8-color map with paired colors
  ([Qualitative, Paired](http://colorbrewer2.org/#type=qualitative&scheme=Paired&n=8))
- `spectralN` (for N=4..8): N-color map with diverging colors
  ([Diverging, Spectral](http://colorbrewer2.org/#type=diverging&scheme=Spectral&n=8))

## Manually defined colors

The `Plot.style.color` array contains a list of all colors used in the plot in
HTML format. You can populate it with a set of manually defined colors. Below is
the definition of the default theme:

```python
    plot.style.color = ['A6CEE3', '1F78B4', 'B2DF8A', '33A02C', 'FB9A99', 'E31A1C', 'FDBF6F', 'FF7F00']
```
