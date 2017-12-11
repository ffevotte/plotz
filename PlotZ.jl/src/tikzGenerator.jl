mutable struct TikzGenerator
    latex :: LatexOutput

    TikzGenerator() = begin
        t = new()

        t.latex = LatexOutput("PlotZ", raw"\makeatletter", raw"\makeatother")
        insert!(t.latex, "/header")
        insert!(t.latex, "/header/colors")
        insert!(t.latex, "/header/markers")
        insert!(t.latex, "/header/patterns")
        insert!(t.latex, "/header/thickness")
        insert!(t.latex, "/background",
                raw"\def\plotz@background{", "}")
        insert!(t.latex, "/background/bbox")
        insert!(t.latex, "/background/grid")
        insert!(t.latex, "/background/legend")
        insert!(t.latex, "/lines",
                raw"\def\plotz@lines{", "}")
        insert!(t.latex, "/foreground",
                raw"\def\plotz@foreground{", "}")
        insert!(t.latex, "/foreground/axes")
        insert!(t.latex, "/foreground/legend")
        insert!(t.latex, "/legend",
                raw"\def\plotz@legend{", "}")
        insert!(t.latex, "/legendmargin",
                raw"\def\plotz@legendmargin{", "}")
        insert!(t.latex, "/scale")

        return t
    end
end
