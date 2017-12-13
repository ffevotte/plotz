
mutable struct Function
    fun
    samples :: Int
    range   :: Nullable{Tuple{Float64, Float64}}

    Function(fun; samples=100, range=Nullable{Tuple{Float32, Float32}}()) =
        new(fun, samples, range)
end

function Base.start(f::Function)
    (x0, x1) = get(f.range)
    dx = (x1 - x0) / (f.samples - 1)

    function _it(c::Channel)
        for i in 1:f.samples
            x = x0 + (i-1) * dx
            put!(c, (x, f.fun(x)))
        end
    end
    c = Channel(_it)
    return (c, start(c))
end

function Base.next(f::Function, cstate)
    (c, state) = cstate

    (val, newstate) = next(c, state)
    return (val, (c, newstate))
end

function Base.done(f::Function, cstate)
    (c, state) = cstate
    return done(c, state)
end




function DataFile(filename::String; sep=r"\s+", comment=r"^\s*#")
    function _it(c::Channel)
        open(filename) do f
            for line in eachline(f)
                if comment != nothing && ismatch(comment, line)
                    continue
                end

                tofloat(f) = try
                    parse(Float64, f)
                catch
                    f
                end

                fields = map(tofloat, split(line, sep))
                put!(c, fields)
            end
        end
    end
    return Channel(_it)
end
