module Markers

function always()
    (x, y) -> true
end

function oneInN(n::Int, start=1::Int)
    _i = start
    _n = n
    (x, y) -> begin
        if _i == 1
            _i = _n
            return true
        else
            _i -= 1
            return false
        end
    end
end

function equallySpaced(dX::Real, start=0::Real)
    _start = start

    (x, y) -> begin
        if x >= _start
            _start += dX
            return true
        else
            return false
        end
    end
end

end
