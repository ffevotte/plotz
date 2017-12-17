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

    size_x :: Float32
    size_y :: Float32
    scale  :: Float32

    style :: Style

    data  :: Vector{Line}

    Plot() = begin
        p = new()
        p.title = Nullable{String}()

        p.x = Axis(1)
        p.y = Axis(2)

        p.size_x = 266.66
        p.size_y = 200
        p.scale = 1

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

    update!(p.x)
    update!(p.y)
    if p.x.pos == nothing
        p.x.pos = p.y.min
    end
    if p.y.pos == nothing
        p.y.pos = p.x.min
    end

    render(p, output)
end

@chainable function plot!(p::Plot, data; title=nothing)
    p.x._setup = false
    p.y._setup = false

    l = Line()
    l.title = title

    push!(l.points, Vector{Tuple{Float32, Float32}}(0))
    j = 1

    for r in rows(data)
        x = p.x.scale(r[1])
        y = p.x.scale(r[2])

        push!(l.points[j], (r[1], r[2]))

        p.x.min = min(x, p.x.min)
        p.x.max = max(x, p.x.max)

        p.y.min = min(y, p.y.min)
        p.y.max = max(y, p.y.max)
    end

    push!(p.data, l)
    return l
end
