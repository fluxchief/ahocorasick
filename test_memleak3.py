from distutils.util import get_platform
import sys
sys.path.insert(0, "build/lib.%s-%s" % (get_platform(), sys.version[0:3]))


import ahocorasick

"""We just want to exercise the code and monitor its memory usage."""

def getLabels():
    tree = ahocorasick.KeywordTree()
    tree.add("he")
    tree.add("she")
    tree.add("his")
    tree.add("hers")
    tree.make()
    return tree.zerostate().labels()


while True:
    getLabels()
