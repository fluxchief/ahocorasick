from distutils.util import get_platform
import sys
sys.path.insert(0, "build/lib.%s-%s" % (get_platform(), sys.version[0:3]))


import ahocorasick

"""We just want to exercise the code and monitor its memory usage."""

n = 0
while True:
    sys.stdout.write("iteration %s\n" % n)
    sys.stdout.flush()
    tree = ahocorasick.KeywordTree()
    f = open("/usr/share/dict/words")
    for i, word in enumerate(f):
        tree.add(word.strip())
    f.close()
    tree.make()
    tree.search("foo bar baz")
    n += 1
