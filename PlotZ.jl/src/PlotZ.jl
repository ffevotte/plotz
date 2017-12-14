include("utils.jl")
include("dataSources.jl")
include("axis.jl")
include("style.jl")
include("plot.jl")
include("render.jl")


N = 10
data = Array{Float64,2}(N, 2)
for i in 1:N
    x = (i-0.5)/N
    data[i,1] = x
    data[i,2] = sin(pi*x)
end

Plot("essai") do p
    p.title = "My first PlotZ plot"
    p |> plot!(Function(sin, range=(0,pi))) |> style!(color=1)
    p |> plot!(DataFile("../../examples/01-dataSources/02-file/mydata.csv", sep=";")) |> style!(color=1)
    colormap!(p, "monochrome")
    dashed!(p)
end
