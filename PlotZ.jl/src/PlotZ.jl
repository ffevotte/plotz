__precompile__()
module PlotZ

export Plot, DataFile, Markers
export plot!, style!, colormap!, dashed!

include("utils.jl")
include("dataSources.jl")
include("axis.jl")
include("style.jl")
include("markers.jl")
include("line.jl")
include("plot.jl")
include("render.jl")

end
