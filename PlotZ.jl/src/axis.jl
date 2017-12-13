linear(x :: Number) = convert(Float64, x)
logarithmic(x :: Number) = exp(x)

mutable struct Axis
    orientation  :: Int
    scale

    label        :: Nullable{String}
    label_rotate :: Bool
    label_shift  :: Float64

    min          :: Float64
    max          :: Float64
    pos

    ticks
    tick_format
    tick_anchor



    Axis(orientation) = begin
        a = new()
        a.orientation = orientation
        a.scale = linear
        a.label = Nullable{String}()
        a.label_rotate = false
        a.label_shift = orientation==1 ? 2 : 3
        a.min = Inf
        a.max = -Inf
        a.pos = nothing

        a.ticks = nothing
        a.tick_format = x -> begin
            if a.scale == logarithmic
                string(raw"$", "10^{$x}", raw"$")
            else
                "$x"
            end
        end
        a.tick_anchor = nothing

        return a
    end
end


function update(a :: Axis)
    a.pos = convert(Float64, a.pos)

    if a.ticks == nothing
        a.ticks = []
    end

    if a.tick_anchor == nothing
        a.tick_anchor = a.orientation==1 ? "north" : "east"
    end
end
