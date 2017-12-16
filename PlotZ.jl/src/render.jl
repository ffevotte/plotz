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


macro rawsprintf(fmt, val...)
    fmt = eval(fmt)
    quote
        @sprintf $fmt $(map(esc, val)...)
    end
end

function render(p::Plot, outputName::String)
    gen = TikzGenerator()
    render!(gen, p.style)

    for data_series in p.data
        render!(gen, data_series)
    end

    render_title!(gen, p)
    render_size!(gen, p)
    compile(gen, outputName)
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

function render_title!(gen::TikzGenerator, plot::Plot)
    if plot.title != nothing
        append!(gen.latex, "/background/legend",
                raw"\coordinate(title)at(current bounding box.north);")

        append!(gen.latex, "/foreground",
                @rawsprintf(raw"\draw(title)++(0,1em)node[anchor=south]{%s};",
                            get(plot.title)))
    end
end

function render_size!(gen::TikzGenerator, plot::Plot)
    append!(gen.latex, "/background/bbox",
            @rawsprintf(raw"\fill[white](%f,%f)rectangle(%f,%f);",
                        plot.x.min, plot.y.min,
                        plot.x.max, plot.y.max))

    append!(gen.latex, "/scale", @rawsprintf(raw"\def\plotz@scalex{%.6f}",
                                             plot.size_x*plot.scale / (plot.x.max-plot.x.min)))
    append!(gen.latex, "/scale", @rawsprintf(raw"\def\plotz@scaley{%.6f}",
                                             plot.size_y*plot.scale / (plot.y.max-plot.y.min)))
end


function compile(gen::TikzGenerator, outputName::String)
    mktempdir() do tmpdir
        cd(tmpdir) do
            open("standalone.tex", "w") do f
                write(f, join([
                    raw"\errorstopmode",
                    raw"\documentclass{standalone}",
                    raw"\usepackage{plotz}",
                    raw"\begin{document}",
                    raw"\plotz{plotz}",
                    raw"\end{document}",
                ], "%\n"))
            end

            open("plotz.tex", "w") do f
                output(f, gen.latex)
            end
        end

        Base.Filesystem.cp(joinpath(tmpdir, "plotz.tex"),
                           string(outputName, ".tex"),
                           remove_destination=true)

        cd(tmpdir) do
            (stdout, stdin, pdflatex) = readandwrite(`pdflatex -file-line-error standalone.tex`)
            close(stdin)

            context = 0
            error = r"^.+:\d+: |^! LaTeX Error:"
            for line in eachline(stdout)
                if match(error, line) != nothing
                    context = max(context, 5)
                end

                if context > 0
                    println(line)
                    context -= 1
                end
            end
        end

        try
            Base.Filesystem.cp(joinpath(tmpdir, "standalone.pdf"),
                               string(outputName, ".pdf"),
                               remove_destination=true)
        catch
            error("No output PDF file produced")
        end
    end
end
