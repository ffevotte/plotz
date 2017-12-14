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

    style :: Style

    data  :: Vector{Line}

    Plot() = begin
        p = new()
        p.title = Nullable{String}()
        p.x = Axis(1)
        p.y = Axis(2)
        p.data = []
        p.style = Style()
        return p
    end
end

colormap!(plot, name="default") = colormap!(plot.style, name)
dashed!(plot, activate=true) = dashed!(plot.style, activate)

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
