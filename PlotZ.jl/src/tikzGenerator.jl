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
