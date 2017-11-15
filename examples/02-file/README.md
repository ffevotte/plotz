# Plotting data files

<img src="plot.svg?raw=true&sanitize=true"/>

This example demonstrates how to plot the data coming from ASCII files, such as
CSV or "gnuplot-style" files.

## Gnuplot-style data files

You can plot data from a file using the `DataFile` data generator.
In its most simple form, you only need to provide the data file name:

<!---plotz include("plot.py", "#line1") -->
```python
    p.plot(DataFile("mydata.dat"),
           title=r"$\sin(\pi\,x)$")
```
<!---plotz end -->

In this case, `PlotZ` expects the data to be formatted as ascii text, in columns
separated by spaces or tabulations. Lines starting with a `#` are considered to
be comments. For example:

<!---plotz head("mydata.dat") -->
```
# x       	 sin(pi x) 	 sin(2 pi x)
0.0000000 	 0.0000000 	 0.0000000
0.0100000 	 0.0314108 	 0.0627905
0.0200000 	 0.0627905 	 0.1253332
0.0300000 	 0.0941083 	 0.1873813
0.0400000 	 0.1253332 	 0.2486899
0.0500000 	 0.1564345 	 0.3090170
0.0600000 	 0.1873813 	 0.3681246
0.0700000 	 0.2181432 	 0.4257793
0.0800000 	 0.2486899 	 0.4817537
...
```
<!---plotz end -->

## CSV files

You can specify the type of separator and comments you want. For example, to
plot data from a CSV file:

<!---plotz include("plot.py", "#line3") -->
```python
    p.plot(DataFile("mydata.csv", sep=";", comment="#"),
           title=r"$\sin(3\,\pi\,x)$")
```
<!---plotz end-->

In this case, the data file might look like this:
<!---plotz head("mydata.csv") -->
```
# x         ; sin(3 pi x) ; sin(4 pi x)
0.0000000   ; 0.0000000   ; 0.0000000
0.0100000   ; 0.0941083   ; 0.1253332
0.0200000   ; 0.1873813   ; 0.2486899
0.0300000   ; 0.2789911   ; 0.3681246
0.0400000   ; 0.3681246   ; 0.4817537
0.0500000   ; 0.4539905   ; 0.5877853
0.0600000   ; 0.5358268   ; 0.6845471
0.0700000   ; 0.6129071   ; 0.7705132
0.0800000   ; 0.6845471   ; 0.8443279
...
```
<!---plotz end -->


## Plotting different columns

By default, the first two columns are plotted. To use other columns, provide a
`col` argument to the `plot` function. For example, to plot the 3rd column as a
function of the 1st:

<!---plotz include("plot.py", "#line2") -->
```python
    p.plot(DataFile("mydata.dat"), col=(0,2),
           title=r"$\sin(2\,\pi\,x)$")
```
<!---plotz end-->
