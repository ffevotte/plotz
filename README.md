# PlotZ

If you are plotting graphs for scientific publication, chances are that

- your data has been produced by a python program (or by some other
  C/C++/Fortran code, but you want to post-process it in a higher-level language
  like python);
  
- you are eventually going to write a paper using LaTeX (what else?) in which
  you'll want your figures to be nice and tightly integrated with the rest of
  the document.

`PlotZ` aimz at producing publication-quality plots for inclusion in LaTeX
documents. It is designed to be as simple to use as possible, with a Python API
allowing to produce, post-process and plot your data in the same environment.

<img src="examples/figure.png?raw=true" width="600px" alt="Example plot" />


## Installation

Simply clone this repository somewhere, and source the accompanying environment
file to setup the relevant environment variables:

```sh
git clone https://github.com/ffevotte/plotz.git
source /path/to/plotz/env.sh
```


## Basic usage

### Python script

Put the following content in a python file (named `myplot.py`, for example):

```python
from plotz import *
from math import sin, pi

with Plot("myfigure") as p:
    p.title = r"My first \texttt{PlotZ} plot"
    p.x.label = "$x$"
    p.y.label = "$y$"
    p.y.label_rotate = True

    p.plot(Function(sin, samples=50, range=(0, pi)),
           title=r"$\sin(\pi \, x)$")

    p.legend("north east")
```

then execute the code:

```sh
source /path/to/plotz/env.sh
python myplot.py
```

You should get two files:

- `myfigure.pdf` is a rendered version of your figure (similar to the image
  shown above, except it is not rasterized),
- `myfigure.tex` is a LaTeX file that you can import in a LaTeX document


### LaTeX document

In order to include a `PlotZ` figure in a LaTeX document, the only steps needed
are:

- include the `plotz` package in your preamble
- use the `plotz` command to include your figure

For example:

```latex
\documentclass{article}
\usepackage{plotz}

\begin{document}

\begin{figure}[ht]
  \centering
  \plotz{myfigure}
  \caption{A \texttt{PlotZ} figure}
\end{figure}

\end{document}
```


## Contributing

If you make improvements to this code or have suggestions, please do not
hesitate to fork the repository or submit bug reports
on [github](https://github.com/ffevotte/plotz.git). The repository's URL is:

    https://github.com/ffevotte/plotz.git


## License

Copyright (C) 2017 François Févotte.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see [http://www.gnu.org/licenses/]().

### Acknowledgement

The color schemes included in `PlotZ` come from the
excellent [ColorBrewer](http://colorbrewer2.org/) tool.
