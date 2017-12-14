include("utils.jl")
include("latexOutput.jl")
include("tikzGenerator.jl")

include("dataSources.jl")
include("axis.jl")

mutable struct Line
    title     :: Nullable{String}
    line      :: Bool
    color     :: Int
    markers   :: Nullable{Int}
    pattern   :: Int
    thickness :: Int
    points    :: Vector{Vector{Tuple{Float32, Float32}}}

    Line() = begin
        l = new()
        l.title = Nullable{String}()
        l.line = true
        l.points = []
        return l
    end
end

@chainable function style!(line :: Line; kwargs...)
    for (name, val) in kwargs
        setfield!(line, name,
                  convert(typeof(getfield(line, name)), val))
    end
    return line
end


mutable struct Plot
    title :: Nullable{String}

    x     :: Axis
    y     :: Axis

    data  :: Vector{Line}

    Plot() = begin
        p = new()
        p.title = Nullable{String}()
        p.x = Axis(1)
        p.y = Axis(2)
        p.data = []
        return p
    end
end

function Plot(fun, output::String)
    p = Plot()
    fun(p)
    render(p, output)
end


@chainable function plot!(p::Plot, data)
    l = Line()
    push!(l.points, Vector{Tuple{Float32, Float32}}(0))
    j = 1

    for r in rows(data)
        push!(l.points[j], (r[1], r[2]))
    end

    push!(p.data, l)
    return l
end

function render(p::Plot, outputName::String)
    gen = TikzGenerator()
    for data_series in p.data
        render(gen, data_series)
    end
    output(gen.latex)
end

function render(gen::TikzGenerator, line::Line)
    for subline in line.points
        append!(gen.latex, "/lines", raw"\draw")

        # First data point
        iter = start(subline)
        (x, y), iter = next(subline, iter)
        append!(gen.latex, "/lines",
                "  ($x,$y)")

        # Other data points
        while !done(subline, iter)
            (x, y), iter = next(subline, iter)
            append!(gen.latex, "/lines",
                    "--($x,$y)")
        end
        append!(gen.latex, "/lines", ";")
    end
end

N = 10
data = Array{Float64,2}(N, 2)
for i in 1:N
    x = (i-0.5)/N
    data[i,1] = x
    data[i,2] = sin(pi*x)
end

Plot("essai") do p
    p.title = "My first PlotZ plot"
    p |> plot!(data) |> style!(color=1)
    true
end
