"""Copy chosen smali files out of the cached disassembly, for reading.

ci/queries.txt, one per line:
    Lcom/foo/Bar;        the class's smali file
    grep:some text       every smali file that contains this text (fixed string)
    #...                 a comment
Output goes to build/extract/, keeping the dex it came from in the path.
"""
import os, shutil, subprocess, sys, glob

cache = os.environ.get("MARGYT_CACHE") or os.path.expanduser("~/.cache/margyt-dex")
out = "build/extract"
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
trees = sorted(glob.glob(os.path.join(cache, "pieces", "*", "smali")))
print("%d disassembled dex trees" % len(trees))
limit = 400
copied = 0
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    hits = []
    if line.startswith("grep:"):
        needle = line[5:]
        for tree in trees:
            r = subprocess.run(["grep", "-rlF", "--include=*.smali", "--", needle, tree],
                               capture_output=True, text=True)
            hits += r.stdout.split()
        print("grep %r: %d files" % (needle, len(hits)))
    else:
        rel = line[1:-1] + ".smali" if line.startswith("L") and line.endswith(";") else line
        for tree in trees:
            path = os.path.join(tree, rel)
            if os.path.isfile(path):
                hits.append(path)
        print("%s: %d" % (line, len(hits)))
    for path in hits[:limit]:
        tree_id = path.split(os.sep + "smali" + os.sep, 1)[0].rsplit(os.sep, 1)[1][:8]
        dest = os.path.join(out, tree_id, path.split(os.sep + "smali" + os.sep, 1)[1])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(path, dest)
        copied += 1
print("copied", copied)
