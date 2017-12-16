using PlotZ

Plot("essai") do p
    p.title = raw"My first \texttt{PlotZ} plot"
    p.x.label = raw"$x$"
    p.y.label = raw"$y$"

    plot!(p, PlotZ.Function(sin, samples=50, range=(0, pi)),
          title=raw"$\sin(x)$")
end
