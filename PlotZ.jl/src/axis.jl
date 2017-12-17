linear(x :: Number) = convert(Float64, x)
logarithmic(x :: Number) = exp(x)

mutable struct Axis
    _setup       :: Bool
    _orientation :: Int

    scale

    label        :: Nullable{String}
    label_rotate :: Bool
    label_shift  :: Float64

    min          :: Float64
    max          :: Float64
    pos

    ticks
    tick_format
    tick_rotate :: Float64
    tick_anchor



    Axis(orientation) = begin
        a = new()
        a._setup = true
        a._orientation = orientation
        a.scale = linear

        a.label = Nullable{String}()
        a.label_rotate = false
        a.label_shift = (orientation==1) ? 2 : 3

        a.min = Inf
        a.max = -Inf
        a.pos = nothing

        a.ticks = nothing
        a.tick_format = x -> begin
            if a.scale == logarithmic
                raw"$" * "10^{$x}" * raw"$"
            else
                @sprintf "%.2f" x
            end
        end
        a.tick_anchor = nothing
        a.tick_rotate = 0

        return a
    end
end


function update!(a::Axis)
    update_ticks!(a)

    if a.tick_anchor == nothing
        a.tick_anchor = a._orientation==1 ? "north" : "east"
    end
end

function update_ticks!(a::Axis)
    if typeof(a.ticks) <: Void
        delta = (a.max-a.min)
        factor = 1
        while delta < 10
            delta *= 10
            factor *= 10
        end
        a.ticks = round(delta/5.) / factor
        a.min = floor(a.min*factor) / factor
        a.max = ceil(a.max*factor) / factor
    end

    if typeof(a.ticks) <: Number
            x = a.min
            factor = 1
            while x != round(x) && abs(x) < 0.9
                x *= 10
                factor *= 10
            end
            x = round(x)/factor
            a.min = min(a.min, x)

            ticks = []
            while x <= a.max
                push!(ticks, x)
                x += a.ticks
            end

            a.ticks = ticks
    end

    map!(a.ticks, a.ticks) do t
        if typeof(t) <: Number
            x = t
            label = a.tick_format(x)
            return (x, label)
        else
            t
        end
    end
end
