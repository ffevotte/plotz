mutable struct Line
    title     :: Nullable{String}
    line      :: Bool
    color     :: Int
    markers   :: Nullable{Int}
    markers_filter
    pattern   :: Int
    thickness :: Int
    points    :: Vector{Vector{Tuple{Float32, Float32}}}

    Line() = begin
        l = new()
        l.title = Nullable{String}()
        l.line = true
        l.points = []
        l.markers_filter = Markers.always()
        return l
    end
end

@chainable function style!(line :: Line; kwargs...)
    for (name, val) in kwargs
        try
            setfield!(line, name, val)
        catch
            setfield!(line, name,
                      convert(typeof(getfield(line, name)), val))
        end
    end
    return line
end
