mutable struct Style
    color     :: Vector{String}
    thickness :: Vector{String}
    pattern   :: Vector{String}
    marker    :: Vector{String}

    Style() = begin
        s = new()
        colormap!(s)
        s.thickness = ["very thick" for i in 1:8]
        dashed!(s, false)
        s.marker = [
            raw"$+$",
            raw"$\circ$",
            raw"$\Box$",
            raw"$\triangle$",
            raw"$\times$",
            raw"$\bullet$",
            raw"$\blacksquare$",
            raw"$\blacktriangle$",
        ]
        return s
    end
end

function colormap!(s::Style, name::String="default")
    if name == "default"
        c = ["377EB8", "E41A1C", "4DAF4A", "984EA3", "FF7F00", "A65628", "F781BF", "FFFF33"]
    elseif name == "paired"
        c = ["A6CEE3", "1F78B4", "B2DF8A", "33A02C", "FB9A99", "E31A1C", "FDBF6F", "FF7F00"]
    elseif name == "dark"
        c = ["1B9E77", "D95F02", "7570B3", "E7298A", "66A61E", "E6AB02", "A6761D", "666666"]
    elseif name == "spectral8"
        c = ["D53E4F", "F46D43", "FDAE61", "FEE08B", "E6F598", "ABDDA4", "66C2A5", "3288BD"]
    elseif name == "spectral7"
        c = ["D53E4F", "FC8D59", "FEE08B", "FFFFBF", "E6F598", "99D594", "3288BD"]
    elseif name == "spectral6"
        c = ["D53E4F", "FC8D59", "FEE08B", "E6F598", "99D594", "3288BD"]
    elseif name == "spectral5"
        c = ["D7191C", "FDAE61", "FFFFBF", "ABDDA4", "2B83BA"]
    elseif name == "spectral4"
        c = ["D7191C", "FDAE61", "ABDDA4", "2B83BA"]
    elseif name == "monochrome"
        c = ["000000" for i in 1:8]
    else
        error("Unknown colormap: `$name'")
    end

    s.color = c
end

function dashed!(style::Style, activate=true)
    if activate
        style.pattern = [raw"solid",
                         raw"dash pattern=on 6pt off 6pt",
                         raw"dash pattern=on 6pt off 3pt on 2\pgflinewidth off 3pt",
                         raw"dotted",
                         raw"dashed",
                         raw"dash pattern=on 3pt off 2pt on \pgflinewidth off 2pt",
                         raw"loosely dotted",
                         (raw"dash pattern=on 4pt off 2pt on \pgflinewidth off " *
                          raw"2pt on \pgflinewidth off 2pt on \pgflinewidth off 2pt")]
    else
        style.pattern = ["solid" for i in 1:8]
    end
end
