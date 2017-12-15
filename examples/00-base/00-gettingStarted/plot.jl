# push!(LOAD_PATH, pwd())
using PlotZ

N = 10
data = Array{Float64,2}(N, 2)
for i in 1:N
    x = (i-0.5)/N
    data[i,1] = x
    data[i,2] = sin(pi*x)
end

Plot("essai") do p
    p.title = "My first PlotZ plot"
    plot!(p, PlotZ.Function(sin, range=(0,pi))) |> style!(color=1)
    plot!(p, DataFile("../../01-dataSources/02-file/mydata.csv", sep=";")) |> style!(color=1)
    colormap!(p, "monochrome")
    dashed!(p)
end
