mutable struct LineProperties
    color     :: Int
    marker    :: Int
    pattern   :: Int
    thickness :: Int

    LineProperties() = new(0, 0, 0, 0)
end

macro next(sym)
    quote
        $(esc(sym)) += 1
    end
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

    line :: LineProperties

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
        p.line = LineProperties()
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
    l.color = @next p.line.color
    l.pattern = @next p.line.pattern
    l.thickness = @next p.line.thickness

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
