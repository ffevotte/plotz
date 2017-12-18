__precompile__()
module PlotZ

export Plot, DataFile
export plot!, style!, colormap!, dashed!

include("utils.jl")
include("dataSources.jl")
include("axis.jl")
include("style.jl")
include("plot.jl")
include("render.jl")

end
