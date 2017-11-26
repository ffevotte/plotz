import re
import sys, os, os.path
import subprocess


class WorkingDirectory(object):
    def __init__(self, workdir):
        self._new = workdir
        self._old = None

    def __enter__(self):
        self._old = os.getcwd()
        os.chdir(self._new)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._old)


def include(filename, delimiter=None):
    try:
        prefix, suffix = ("", "\n")
        if filename.endswith(".py"):
            prefix, suffix = "```python\n", "```\n"
        if filename.endswith(".tex"):
            prefix, suffix = "```latex\n", "```\n"

        ret = prefix
        with open(filename, "r") as f:
            output = delimiter is None

            for line in f:
                if line.strip() == delimiter:
                    output = not output
                    continue

                if output:
                    ret += line

        ret += suffix
        return ret
    except:
        return "\n"

def head(filename, lines=10):
    with open(filename, "r") as f:
        i = 0
        ret = "```\n"
        for line in f:
            ret += line
            i += 1

            if i == lines:
                return ret + "...\n```\n"

def process_README(dirname):
    plotz = re.compile("<!---plotz(.*)-->")
    filename = "README.md"

    title = None
    image = "plot.svg"

    with open(filename, "r") as f:
        markdown = f.readlines()

    within_section = False
    with open(filename, "w") as f:
        for line in markdown:
            if title is None and line.startswith("# "):
                title = line[2:].strip()

            if not within_section:
                f.write(line)

            m = plotz.match(line.strip())
            if m:
                command = m.group(1).strip()
                if command == "end":
                    within_section = False
                    f.write(line)
                    continue

                within_section = True
                f.write(eval(command))

    return (dirname, title, image)


def pdflatex(filename):
    p = subprocess.Popen(["latexmk", "-pdf", "-interaction=errorstopmode", filename], stdin=subprocess.PIPE)
    p.stdin.close()
    p.wait()

toc = []
for entry in sorted(os.listdir(".")):
    if os.path.isdir(entry):
        print "\nentering %s" % entry
        with WorkingDirectory(entry):
            print "  - generating plot"
            subprocess.call(["python-coverage", "run", "plot.py"])
            subprocess.call(["python3", "plot.py"])

            print "  - processing README.md"
            toc.append(process_README(entry))

            if os.path.exists("document.tex"):
                print "  - compiling LaTeX document"
                pdflatex("document.tex")

            if os.path.exists("presentation.tex"):
                print "  - compiling LaTeX presentation"
                pdflatex("presentation.tex")

            for filename in os.listdir("."):
                if filename.endswith(".pdf"):
                    print "  - converting %s to svg" % filename
                    subprocess.call(["pdf2svg", filename, filename.replace(".pdf", ".svg")])

with open("README.md", "w") as f:
    f.write("# PlotZ examples gallery\n\n")

    for entry in toc:
        f.write("## [%s](%s)\n" % (entry[1], entry[0]))
        f.write('[<img src="%s?raw=true&sanitize=true"/>](%s)\n' % (os.path.join(entry[0], entry[2]), entry[0]))
        f.write("\n")
