mutable struct LatexOutput
    lines    :: Vector{Any}
    index    :: Dict{String, LatexOutput}
    prefix   :: Vector{String}
    suffix   :: Vector{String}

    function LatexOutput(prefix :: Vector{String}, suffix :: Vector{String})
        return new([], Dict(), prefix, suffix)
    end
end

function LatexOutput(name :: String,
                     prefix=Nullable{String}(),
                     suffix=Nullable{String}())
    pref = ["", string("% ", name, " ")]
    if ! isnull(prefix)
        push!(pref, unsafe_get(prefix))
    end

    suf = Vector{String}(0)
    if ! isnull(suffix)
        push!(suf, unsafe_get(suffix))
    end

    return LatexOutput(pref, suf)
end

function splitPath(path :: String)
    components = split(path, "/")
    if components[1] == ""
        return components[2:end]
    else
        return components
    end
end

@chainable function insert!(l :: LatexOutput, path :: String,
                            prefix=Nullable{String}(), suffix=Nullable{String}())
    insert!(l, splitPath(path), prefix, suffix)
end

function insert!{T}(l :: LatexOutput, path :: Vector{T}, prefix, suffix)
    first = path[1]
    rest  = path[2:end]

    if length(path) == 1
        l.index[first] = LatexOutput(convert(String, first), prefix, suffix)
        push!(l.lines, l.index[first])
    else
        insert!(l.index[first], rest, prefix, suffix)
    end

    return l
end

function append!(l :: LatexOutput, path :: String, latex)
    append!(l, splitPath(path), latex)
end

function append!{T}(l :: LatexOutput, path :: Vector{T}, latex)
    if length(path) == 0
        push!(l.lines, latex)
    else
        first = path[1]
        rest = path[2:end]
        nested = l.index[first]
        append!(nested, rest, latex)
    end
end

function output(f, l::LatexOutput, indent::String="")
    output(f, l.prefix, indent)
    output(f, l.lines, string(indent, "  "))
    output(f, l.suffix, indent)
end

function output(f, l::String, indent::String)
    write(f, indent, l, "%\n")
end

function output{T}(f, l::Array{T}, indent::String)
    for line in l
        output(f, line, indent)
    end
end
