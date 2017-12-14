include("latexOutput.jl")

mutable struct TikzGenerator
    latex :: LatexOutput

    TikzGenerator() = begin
        t = new()

        t.latex = (LatexOutput("PlotZ", raw"\makeatletter", raw"\makeatother")
                   |> insert!("/header")
                   |> insert!("/header/colors")
                   |> insert!("/header/markers")
                   |> insert!("/header/patterns")
                   |> insert!("/header/thickness")
                   |> insert!("/background",
                              raw"\def\plotz@background{", "}")
                   |> insert!("/background/bbox")
                   |> insert!("/background/grid")
                   |> insert!("/background/legend")
                   |> insert!("/lines",
                              raw"\def\plotz@lines{", "}")
                   |> insert!("/foreground",
                              raw"\def\plotz@foreground{", "}")
                   |> insert!("/foreground/axes")
                   |> insert!("/foreground/legend")
                   |> insert!("/legend",
                              raw"\def\plotz@legend{", "}")
                   |> insert!("/legendmargin",
                              raw"\def\plotz@legendmargin{", "}")
                   |> insert!("/scale"))

        return t
    end
end


function index(i)
    'A' + i-1
end

function render(p::Plot, outputName::String)
    gen = TikzGenerator()
    render!(gen, p.style)

    for data_series in p.data
        render!(gen, data_series)
    end
    output(gen.latex)
end

macro define_style(style, path, definition)
    def = eval(definition)
    quote
        append!($(esc(:gen)).latex, $path, [
            @sprintf($def, index(i), val)
            for (i, val) in enumerate($(esc(style)))
        ])
    end
end

function render!(gen::TikzGenerator, style::Style)
    @define_style(style.color, "/header/colors",
                  raw"\definecolor{color%s}{HTML}{%s}")
    @define_style(style.marker, "/header/markers",
                  raw"\def\marker%s{%s}")
    @define_style(style.pattern, "/header/patterns",
                  raw"\tikzstyle{pattern%s}=[%s]")
    @define_style(style.thickness, "/header/thickness",
                  raw"\tikzstyle{thickness%s}=[%s]")
end

function render!(gen::TikzGenerator, line::Line)
    for subline in line.points
        append!(gen.latex, "/lines", raw"\draw")

        # First data point
        iter = start(subline)
        (x, y), iter = next(subline, iter)
        append!(gen.latex, "/lines",
                "  ($x,$y)")

        # Other data points
        while !done(subline, iter)
            (x, y), iter = next(subline, iter)
            append!(gen.latex, "/lines",
                    "--($x,$y)")
        end
        append!(gen.latex, "/lines", ";")
    end
end
