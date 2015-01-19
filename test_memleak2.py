from distutils.util import get_platform
import sys
sys.path.insert(0, "build/lib.%s-%s" % (get_platform(), sys.version[0:3]))


import ahocorasick

"""We just want to exercise the code and monitor its memory usage."""

def getZerostate():
    tree = ahocorasick.KeywordTree()
    tree.add("foobar")
    tree.make()
    return tree.zerostate()


while True:
    getZerostate()
