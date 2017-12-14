macro chainable(expr)
    function arg_symbol(e::Expr)
        if e.head == :parameters
            return e
        end
        return e.args[1]
    end

    function arg_symbol(e::Symbol)
        return e
    end

    defun = deepcopy(expr)

    # Build the funcall
    call = deepcopy(defun.args[1])
    prototype = call.args

    # -> get the first argument
    if typeof(prototype[2]) == Expr && prototype[2].head == :parameters
        ifa = 3
    else
        ifa = 2
    end
    first_arg = prototype[ifa]

    # -> remove type specifications
    map!(arg_symbol, prototype, prototype)

    # Build the new defun
    # -> remove the first argument
    splice!(defun.args[1].args, ifa, [])
    # -> replace the body
    defun.args[2] = quote
        $first_arg -> $call
    end

    quote
        $(esc(defun))
        $(esc(expr))
    end
end



function rows(a)
    return a
end

struct rowIterator{T}
    a :: Array{T, 2}
end

function rows{T}(a :: Array{T, 2})
    return rowIterator(a)
end

function Base.start{T}(array :: rowIterator{T})
    return 1
end

function Base.next{T}(array :: rowIterator{T}, i :: Int)
    return (array.a[i,:], i+1)
end

function Base.done{T}(array :: rowIterator{T}, i :: Int)
    return i > size(array.a, 1)
end
