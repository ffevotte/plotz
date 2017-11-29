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

def process_README(toc=None):
    plotz = re.compile("<!---plotz(.*)-->")
    img = re.compile('<img src="(.*\.svg)\?raw=true&sanitize=true"/>')

    filename = "README.md"

    title = None
    image = None

    with open(filename, "r") as f:
        markdown = f.readlines()

    within_section = False
    with open(filename, "w") as f:
        for line in markdown:
            if title is None and line.startswith("# "):
                title = line[2:].strip()

            if image is None:
                m = img.search(line)
                if m:
                    image = m.group(1).strip()

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

    return (title, image)


def pdflatex(filename):
    p = subprocess.Popen(["latexmk", "-pdf", "-interaction=errorstopmode", filename], stdin=subprocess.PIPE)
    p.stdin.close()
    p.wait()

def make():
    print "  - generating plot"
    subprocess.call(["python-coverage", "run", "plot.py"])
    subprocess.call(["python3", "plot.py"])

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

    print "  - processing README.md"
    return process_README()

def table_of_contents(toc, level="##", path=""):
    ret = []
    for entry in toc:
        rel_path = os.path.join(path, entry[0])
        ret.append("%s [%s](%s)" % (level, entry[1], rel_path))

        if isinstance(entry[2], list):
            ret.append(table_of_contents(entry[2], level+"#", rel_path))
        else:
            ret.append('[<img src="%s?raw=true&sanitize=true"/>](%s)\n' % (os.path.join(rel_path, entry[2]), rel_path))

    return "\n".join(ret)


def walk(rel_path = ""):
    print "\nentering %s" % rel_path
    if os.path.exists("plot.py"):
        return (rel_path,) + make()

    toc = []
    for entry in sorted(os.listdir(os.getcwd())):
        if not os.path.isdir(entry):
            continue

        with WorkingDirectory(entry):
            toc.append(walk(entry))

    (title, _) = process_README(toc=toc)
    return (rel_path, title, toc)


subprocess.call(["find", ".", "-name", ".coverage", "-delete"])
walk()

find = subprocess.Popen(["find", ".", "-name", ".coverage"],
                        stdout=subprocess.PIPE)
coverage_files = [name.strip() for name in find.stdout.readlines()]
subprocess.call(["python-coverage", "combine"] + coverage_files)
subprocess.call(["python-coverage", "html", "-d", "../htmlcov"])
