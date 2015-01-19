#!/usr/bin/env python
"""Unit tests for aho-corasick keyword string searching.

Danny Yoo (dyoo@hkn.eecs.berkeley.edu)
"""

import unittest


## Adds the build library at the head to make testing easier.
from distutils.util import get_platform
import sys
sys.path.insert(0, "build/lib.%s-%s" % (get_platform(), sys.version[0:3]))
## print sys.path


import ahocorasick


class AhoCorasickTest(unittest.TestCase):
    def setUp(self):
        self.tree = ahocorasick.KeywordTree()


    def tearDown(self):
        self.tree = None


    def testKeywordAsPrefixOfAnother(self):
        """According to John, there's a problem with the matcher.
        this test case should expose the bug."""
        self.tree.add('foobar')
        self.tree.add('foo')
        self.tree.add('bar')
        self.tree.make()
        self.assertEqual((3, 6), self.tree.search('xxxfooyyy'))
        self.assertEqual((0, 3), self.tree.search('foo'))
        self.assertEqual((3, 6), self.tree.search('xxxbaryyy'))


    def testAnotherSearch(self):
        """Just to triangulate the search code.  We want to make sure
        that the implementation can do more than one search, at
        least."""
        self.tree.add("Python")
        self.tree.add("PLT Scheme")
        self.tree.make()
        self.assertEqual((19, 25),
                         self.tree.search("I am learning both Python and PLT Scheme"))
        self.assertEqual((0, 10),
                         self.tree.search("PLT Scheme is an interesting language."))


    def testSimpleConstruction(self):
        self.tree.add("foo")
        self.tree.add("bar")
        self.tree.make()
        self.assertEqual((10, 13),
                         self.tree.search("this is a foo message"))


    def testLongestSearch(self):
        self.tree.add("a")
        self.tree.add("alphabet");
        self.tree.make()
        self.assertEqual((0, 1), self.tree.search("alphabet soup"));
        self.assertEqual((0, 8), self.tree.search_long("alphabet soup"))
        self.assertEqual((13, 14), self.tree.search_long("yummy, I see an alphabet soup bowl"))
        


    def testSearchWithWholeMatch(self):
        """Make sure that longest search will match the whole string."""
        longString = "supercalifragilisticexpialidocious"
        self.tree.add(longString)
        self.tree.make()
        self.assertEqual((0, len(longString)),
                         self.tree.search(longString))


    def testSearchLongWithWholeMatch(self):
        """Make sure that longest search will match the whole string."""
        longString = "supercalifragilisticexpialidocious"
        self.tree.add(longString)
        self.tree.make()
        self.assertEqual((0, len(longString)),
                         self.tree.search_long(longString))

    def testSearchLongWithNoMatch(self):
        self.tree.add("foobar")
        self.tree.make()
        self.assertEqual(None, self.tree.search_long("fooba"))


    def testWithExpectedNonmatch(self):
        """Check to see that we don't always get a successful match."""
        self.tree.add("wise man")
        self.tree.make()
        self.assertEqual(
            None,
            self.tree.search("where fools and wise men fear to tread"))        


    def testEmptyConstruction(self):
        """Make sure that we can safely construct and dealloc a tree
        with no initial keywords.  Important because the C
        implementation assumes keywords exist on its dealloc, so we
        have to do some work on the back end to avoid silly segmentation
        errors."""
        tree = ahocorasick.KeywordTree()
        del tree


    def testEmptyMake(self):
        """Calling make() without adding any keywords should raise an
        AssertionError."""
        self.assertRaises(AssertionError, self.tree.make)


    def testDegenerateConstruction(self):
        """If we try searching before making, we should get an
        assertion error."""
        self.assertRaises(AssertionError,
                          lambda: self.tree.search("this is a test"))
    

    def testEmptyKeyword(self):
        """Trying to add an empty should raise an assertion error."""
        self.assertRaises(AssertionError,
                          lambda: self.tree.add(""))
        

    def testEmptyQuery(self):
        self.tree.add("hello world")
        self.tree.make()
        self.assertEqual(None, self.tree.search(""))


    def testNegativeStarposRaisesException(self):
        self.tree.add("hello world")
        self.tree.make()
        self.assertRaises(AssertionError, self.tree.search,
                          "blah", startpos=-42)
                          

    def testStartposWithSearch(self):
        """Check to see if startpos does the right thing."""
        self.tree.add("wood")
        self.tree.add("woodchuck")
        self.tree.make()
        queryString = "howmuchwoodwouldawoodchuckchuck"
        self.assertEqual((7, 11), self.tree.search(queryString))
        self.assertEqual((17, 21), self.tree.search(queryString, startpos=11))
        self.assertEqual((17, 21), self.tree.search(queryString, 11))


    def testStartposWithSearchLong(self):
        """Check to see if startpos does the right thing."""
        self.tree.add("wood")
        self.tree.add("woodchuck")
        self.tree.make()
        queryString = "howmuchwoodwouldawoodchuckchuck"
        self.assertEqual((7, 11), self.tree.search_long(queryString))
        self.assertEqual((17, 26),
                         self.tree.search_long(queryString, startpos=11))
        self.assertEqual((17, 26), self.tree.search_long(queryString, 11))


    def testEmbeddedNulls(self):
        """Check to see if we can accept embedded nulls"""
        self.tree.add("hell\0 world")
        self.tree.make()
        self.assertEqual(None, self.tree.search("ello\0 world"))
        self.assertEqual((0, 11), self.tree.search("hell\0 world"))



    def testEmbeddedNullsAgain(self):
        self.tree.add("\0\0\0")
        self.tree.make()
        self.assertEqual((0, 3), self.tree.search("\0\0\0\0\0\0\0\0"))
        self.assertEqual((3, 6), self.tree.search("\0\0\0\0\0\0\0\0", 3))
        self.assertEqual(None, self.tree.search("\0\0\0\0\0\0\0\0", 6))
        

    def testFindallAndFindallLong(self):
        self.tree.add("python")
        self.tree.add("scheme")
        self.tree.add("perl")
        self.tree.add("java")
        self.tree.add("pythonperl")
        self.tree.make()
        self.assertEqual([(0, 6), (6, 10), (10, 16), (16, 20)],
                         list(self.tree.findall("pythonperlschemejava")))
        self.assertEqual([(0, 10), (10, 16), (16, 20)],
                         list(self.tree.findall_long("pythonperlschemejava")))
        self.assertEquals([],
                          list(self.tree.findall("no pascal here")))
        self.assertEquals([],
                          list(self.tree.findall_long("no pascal here")))



    def testChasesInterface(self):
        self.tree.add("python")
        self.tree.add("is")
        self.tree.make()
        sourceBlocks = ["python programming is fun",
                        "how much is that python in the window"]
        sourceStream = iter(sourceBlocks)
        self.assertEqual([
                           (sourceBlocks[0], (0, 6)),
                           (sourceBlocks[0], (19, 21)),
                           (sourceBlocks[1], (9, 11)),
                           (sourceBlocks[1], (17, 23)),
                         ],
                         list(self.tree.chases(sourceStream)))


    def testZerostate(self):
	"""See if we can get the zero state off a tree."""
	self.tree.add("hello")
	self.tree.make()
	zerostate = self.tree.zerostate()
	self.assertEquals(0, zerostate.id())

    

    def testHeSheHisHersExample(self):
	"""This tests out the example automaton in Figure 1 of the original
	paper Efficient String Matching: An Aid to Bibliographic
	Search."""
	self.tree.add("he")
	self.tree.add("she")
	self.tree.add("his")
	self.tree.add("hers")
	self.tree.make()

	h, e, r, s, i = map(ord, "hersi")
	zerostate = self.tree.zerostate()
	states = [zerostate,                                 # 0
 		  zerostate.goto(h),                         # 1
 		  zerostate.goto(h).goto(e),                 # 2
 		  zerostate.goto(s),                         # 3
 		  zerostate.goto(s).goto(h),                 # 4
 		  zerostate.goto(s).goto(h).goto(e),         # 5
 		  zerostate.goto(h).goto(i),                 # 6
 		  zerostate.goto(h).goto(i).goto(s),         # 7
 		  zerostate.goto(h).goto(e).goto(r),         # 8
 		  zerostate.goto(h).goto(e).goto(r).goto(s)  # 9
		  ]

	# Jumping off the automaton should get us to None
	self.assertEquals(None, zerostate.goto(h).goto(ord('z')))

	# And the zerostate should have transitions everywhere.
	for i in range(256):
	    if i not in (h, s):
		self.assertEquals(0, zerostate.goto(i).id())

	fails = map(lambda s: s.fail(), states)
	## Make sure we get expected ids out of the states.
	self.assertEquals(range(10),
			  map(lambda s: s.id(), states))
        ## Make sure we get expected fails out of the states.
	self.assertEquals(
	    map(lambda n: states[n].id(), [0, 0, 0, 1, 2, 0, 3, 0, 3]),
	    map(lambda s: s.id(), fails[1:]))
	## and make sure that the zero state does not have a failure transition.
	self.assertEquals(None, zerostate.fail())


    def testLabels(self):
	self.tree.add("he")
	self.tree.add("she")
	self.tree.add("his")
	self.tree.add("hers")
	self.tree.make()
	self.assertEquals([ord('e'), ord('i')],
			  self.tree.zerostate().goto(ord('h')).labels())

	     
    def testLabelsAndTransitionsOfZerostate(self):
	self.tree.add("central dogma")
	self.tree.make()
	for i in range(0, 256):
	    if i == ord('c'):
		self.assertEquals(1, self.tree.zerostate().goto(i).id())
	    else:
		self.assertEquals(0, self.tree.zerostate().goto(i).id())
	self.assertEquals(None, self.tree.zerostate().fail())
	# The zero state should have labels to everything.
	self.assertEquals([i for i in range(0, 256)],
			  self.tree.zerostate().labels())


    def testPassingBadOrdinalRaisesAssert(self):
	self.tree.add('foo!')
	self.tree.make()
	self.assertRaises(AssertionError,
			  lambda: self.tree.zerostate().goto(-1))
	self.assertRaises(AssertionError,
			  lambda: self.tree.zerostate().goto(256))

	


    def testStateTraversalBeforeMake(self):
	"""Check to see that we can traverse the graph before calling make."""	
	self.tree.add("he")
	self.tree.add("she")
	self.tree.add("his")
	self.tree.add("hers")
	h, e, r, s, i = map(ord, "hersi")
	zerostate = self.tree.zerostate()
	states = [zerostate,                                 # 0
 		  zerostate.goto(h),                         # 1
 		  zerostate.goto(h).goto(e),                 # 2
 		  zerostate.goto(s),                         # 3
 		  zerostate.goto(s).goto(h),                 # 4
 		  zerostate.goto(s).goto(h).goto(e),         # 5
 		  zerostate.goto(h).goto(i),                 # 6
 		  zerostate.goto(h).goto(i).goto(s),         # 7
 		  zerostate.goto(h).goto(e).goto(r),         # 8
 		  zerostate.goto(h).goto(e).goto(r).goto(s)  # 9
		  ]

	# Jumping off the automaton should get us to None
	self.assertEquals(None, zerostate.goto(h).goto(ord('z')))
	## And, when make() hasn't been called yet, the zerostate
	## itself doesn't have arrows to itself.
	self.assertEquals(None, zerostate.goto(ord('z')))

	fails = map(lambda s: s.fail(), states)
	## Make sure we get expected ids out of the states.
	self.assertEquals(range(10),
			  map(lambda s: s.id(), states))
        ## Make sure we get expected fails out of the states.
	self.assertEquals([None] * len(fails), fails)


    def testAllowOverlaps(self):
        """Andrew Soreng requested a function for doing a findall, but
        allowing for overlaps."""

        patterns = ['ko', 'ov', 'ps', 'cq', 'qi', 'rf', 'uk', 'ml',
                    'om', 'lu', 'wz', 'ir', 'zp', 'we', 'ah', 'de',
                    'nf', 'uk' , 'aa', 'kr', 'vp', 'lg', 'cb', 'ty',
                    'wi', 'dl', 'gf', 'fu', 'qj', 'fo', 'vj', 'vt',
                    'pt', 'hg', 'gy', 'cc', 'ys', 'yn', 'uz', 'cw',
                    'ru', 'uj', 'ko', 'oy', 'eh', 'gz', 'dp', 'rp',
                    'gy', 'xe', 'wh', 'xe', 'zi', 'gl', 'xx', 'rr',
                    'np' , 'sx', 'bb', 'am', 'da', 'pp', 'od', 'gd',
                    'ol', 'ze', 'nc', 'xj', 'ug', 'hx', 'wv', 'xc',
                    'sz', 'an', 'ep', 'vn', 'of', 'fa', 'he', 'yj',
                    'ee', 'hu', 'io', 'hc', 'sf', 'ok', 'ke', 're',
                    'zf', 'jr', 'kd', 'zm', 'gr', 'mz', 'wd', 'vf' ,
                    'wn', 'tc', 'tx', 'do']
        for p in patterns:
            self.tree.add(p)
        self.tree.make()
        s = "jadamboeuhgijoiseroflbaffelkake"
        results = [s[match[0]: match[1]]
                   for match in self.tree.findall(s, allow_overlaps=1)]
        self.assertEqual(["da", "am", "hg", "of", "ke"],
                         results)

                         
    def testOverlaps2(self):
        """Another of Andre's test cases."""

        patterns = ['yw', 'ti', 'dp', 'ln', 'nr', 'do', 'js', 'kq',
                    'qa', 'xq', 'xl', 'nx', 'uh', 'lp', 'vr', 'jy',
                    'lb', 'ba' , 'zo', 'ya', 'yt', 'rw', 'xc', 'wm',
                    'iw', 'ib', 'cq', 'cz', 'rv', 'iz', 'em', 'qa',
                    'ud', 'ag', 'nj', 'nb', 'vg', ' dc', 'qu', 'ww',
                    'ts', 'xe', 'et', 'xa', 'xj', 'oy', 'kl', 'qz',
                    'bu', 'ba', 'rt', 'xr', 'dk', 'jw', 'fg', 'ui',
                    'lb' , 'xh', 'ci', 'vz', 'ez', 'vl', 'hi', 'bm',
                    'qy', 'vz', 'td', 'an', 'vi', 'cv', 'mf', 'mv',
                    'cn', 'io', 'ct', 'si', ' xk', 'jg', 'pt', 'yl',
                    'rv', 'ez', 'um', 'lx', 'sr', 'xc', 'cu', 'qe',
                    'uc', 'fd', 'jx', 'xn', 'sw', 'pz', 'hy', 'hn' ,
                    'er', 'bv', 'nb', 'tp']
        for p in patterns:
            self.tree.add(p)
        self.tree.make()
        s = "jadamboeuhgijoiseroflbaffelkake"
        results = [s[match[0]: match[1]]
                   for match in self.tree.findall(s, allow_overlaps=1)]
        self.assertEqual(['uh', 'er', 'lb', 'ba'],
                         results)
        


    def testOutput(self):
	self.tree.add("he")
	self.tree.add("she")
	self.tree.add("his")
	self.tree.add("hers")
	h, e, r, s, i = map(ord, "hersi")
	zerostate = self.tree.zerostate()
	states = [zerostate,                                 # 0
 		  zerostate.goto(h),                         # 1
 		  zerostate.goto(h).goto(e),                 # 2
 		  zerostate.goto(s),                         # 3
 		  zerostate.goto(s).goto(h),                 # 4
 		  zerostate.goto(s).goto(h).goto(e),         # 5
 		  zerostate.goto(h).goto(i),                 # 6
 		  zerostate.goto(h).goto(i).goto(s),         # 7
 		  zerostate.goto(h).goto(e).goto(r),         # 8
 		  zerostate.goto(h).goto(e).goto(r).goto(s)  # 9
		  ]
	self.assertEquals([None, #
			   None, #h
			   2,    #he
			   None, #s
			   None, #sh
			   3,    #she
			   None, #hi
			   3,    #his
			   None, #her
			   4,    #hers
			   ], 
			  map(lambda s: s.output(), states))


if __name__ == '__main__':
    unittest.main()
