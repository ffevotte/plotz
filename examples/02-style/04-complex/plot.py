from plotz import Plot, DataFile
from plotz.utils import Markers

with Plot("fourier") as p:
    p.title = "Amplification factor of various acceleration schemes"

    p.x.min = 0
    p.x.max = 20
    p.x.ticks = 2
    p.x.label = r"$\omega$"

    p.y.min, p.y.max = 0, 1
    p.y.tick_format = lambda x: "%.1f"%x
    p.y.label = r"$\displaystyle\frac{\Vert\phi_1\Vert_2}{\Vert\phi_0\Vert_2}$"
    p.y.label_shift *= 0.8

    # thickness
    p.style.thickness = ["ultra thin", "thick", "ultra thick"]

    p.plot(DataFile("fourier.dat"), title="SI").style({
        "thickness": 2, # ultra thick
    })
    # thickness

    p.plot(DataFile("fourier.dat"), title="DSA", col=(0,2)).style({
        "thickness": 2,
    })

    # markers
    p.plot(DataFile("fourier.dat"), title="PDSA(2)", col=(0,3)).style({
        "thickness": 0,
        "markers": 7,
        "markers_filter": Markers.equallySpaced(2, 0),
    })

    p.plot(DataFile("fourier.dat"), title="PDSA(3)", col=(0,5)).style({
        "thickness": 0,
        "markers": 5,
        "markers_filter": Markers.equallySpaced(2, 1),
    })
    # markers

    p.plot(DataFile("fourier.dat"), title="PDSA(6)", col=(0,7)).style({
        "thickness": 1,
    })

    p.plot(DataFile("fourier.dat"), title="PDSA(9)", col=(0,9)).style({
        "thickness": 1,
    })

    # black dashed
    p.style.pattern[6] = "dashed"

    p.style.color[6] = "000000"    # black = "#000000"

    p.plot(DataFile("fourier.dat"), col=(0,6),
           title=r"$\rho_{\text{\sc pdsa}}^{\text{max}}(3)$").style({
        "thickness": 1,
    })
    # black dashed

    p.grid()
