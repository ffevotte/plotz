# Getting started

<img src="plot.svg?raw=true&sanitize=true"/>

## Python code

Here is some boilerplate code to produce a very simple plot:

<!---plotz include("plot.py") -->
```python
from math import sin, pi
from plotz import *

with Plot("plot") as p:
    p.title = r"My first \texttt{PlotZ} plot"
    p.x.label = "$x$"
    p.y.label = "$y$"

    p.plot(Function(sin, samples=50, range=(0, pi)),
           title=r"$\sin(x)$")

    p.legend("north east")
```
<!---plotz end -->


## LaTeX document

The figure can be included in any LaTeX document using the `plotz` command:

<!---plotz include("document.tex", "%plotz") -->
```latex
\begin{figure}[h]
  \centering
  \plotz{plot}
  \caption{A \texttt{PlotZ} plot}
  \label{fig:plotz}
\end{figure}
```
<!---plotz end -->

Optional `width` and `height` arguments can be given to the `plotz` command. If
specified, the `PlotZ` picture is scaled to the desired size. In the following
case, the picture is scaled down to fit two plots in the page width. Notice how
the font size, line thickness, \textit{etc.} remain constant; only the axes
scales are adjusted.

<!---plotz include("document.tex", "%plotz*") -->
```latex
\begin{figure}[h]
  \centering
  \plotz[width=0.47\textwidth]{plot}%
  \hfill%
  \plotz[width=0.47\textwidth]{plot}%
  \caption{Two \texttt{PlotZ} pictures scaled down to fit side by side.}
  \label{fig:plotz*}
\end{figure}
```
<!---plotz end -->

<img src="document.svg?raw=true&sanitize=true"/>


If you include the same figure in a beamer presentation, it will nicely adapt to
its new environment: notice how the font changed, and remains readable:

<img src="presentation.svg?raw=true&sanitize=true" style="border: 1px solid blue"/>
