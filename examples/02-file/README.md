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
           title=r"Source Iterations")
```
<!---plotz end -->

In this case, `PlotZ` expects the data to be formatted as ascii text, in columns
separated by spaces or tabulations. Lines starting with a `#` are considered to
be comments. For example:

<!---plotz head("mydata.dat") -->
```
# 0 - omega          1 - SI                2 - DSA               3 - PDSA(6)
0.10471975511965977  0.9467649168031327    0.012888715231260443  0.028828379644380658
0.20943951023931953  0.9372862459120868    0.02692626878742191   0.06580048702437033
0.3141592653589793   0.922199231810265     0.043270450290093576  0.08964996639419284
0.41887902047863906  0.9024308261373377    0.061649229467980404  0.10761029060392499
0.5235987755982988   0.8790502690956817    0.0810076963032603    0.14533935820600352
0.6283185307179586   0.8531297217304907    0.10026664471108038   0.18926437950409242
0.7330382858376184   0.8256425986544388    0.11872831815571191   0.219879754099994
0.8377580409572781   0.7974074070964046    0.1358750738494186    0.24238557661130844
0.9424777960769379   0.7690703695087778    0.15147768349523894   0.27090628870053746
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
           title=r"DSA")
```
<!---plotz end-->


## CSV files

You can specify the type of separator and comments you want. For example, to
plot data from a CSV file:

<!---plotz include("plot.py", "#line3") -->
```python
    p.plot(DataFile("mydata.csv", sep=";", comment="#"), col=(0,3),
           title=r"PDSA(6)")
```
<!---plotz end-->

In this case, the data file might look like this:
<!---plotz head("mydata.csv") -->
```
# 0 - omega           1 - SI                 2 - DSA                3 - PDSA(6)
0.10471975511965977 ; 0.9467649168031327   ; 0.012888715231260443 ; 0.028828379644380658
0.20943951023931953 ; 0.9372862459120868   ; 0.02692626878742191  ; 0.06580048702437033
0.3141592653589793  ; 0.922199231810265    ; 0.043270450290093576 ; 0.08964996639419284
0.41887902047863906 ; 0.9024308261373377   ; 0.061649229467980404 ; 0.10761029060392499
0.5235987755982988  ; 0.8790502690956817   ; 0.0810076963032603   ; 0.14533935820600352
0.6283185307179586  ; 0.8531297217304907   ; 0.10026664471108038  ; 0.18926437950409242
0.7330382858376184  ; 0.8256425986544388   ; 0.11872831815571191  ; 0.219879754099994
0.8377580409572781  ; 0.7974074070964046   ; 0.1358750738494186   ; 0.24238557661130844
0.9424777960769379  ; 0.7690703695087778   ; 0.15147768349523894  ; 0.27090628870053746
...
```
<!---plotz end -->


