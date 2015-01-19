"""setup.py for aho-corasick."""
from distutils.core import setup, Extension

classifiers = """Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Topic :: Text Editors :: Text Processing""".split("\n")

setup(name="ahocorasick",
      version="0.9",
      license="GPL",
      description="Aho-Corasick automaton implementation",
      long_description="""The Aho-Corasick automaton is a data structure that can quickly do a multiple-keyword search across text. It's described in the classic paper 'Efficient string matching: an aid to bibliographic search': http://portal.acm.org/citation.cfm?id=360855&dl=ACM&coll=GUIDE. The majority of the code here is adapted from source code from the Fairly Fast Packet Filter (FFPF) project: http://ffpf.sourceforge.net/general/overview.php.""",
      platforms = ["any"],
      author="Danny Yoo",
      author_email="dyoo@hkn.eecs.berkeley.edu",
      url="http://hkn.eecs.berkeley.edu/~dyoo/python/ahocorasick/",
      download_url="http://hkn.eecs.berkeley.edu/~dyoo/python/ahocorasick/ahocorasick-0.9.tar.gz",
      packages = ['ahocorasick'],
      ext_modules = [Extension("ahocorasick._ahocorasick",
                               ["aho-corasick.c",
                                "slist.c",
                                "py_wrapper.c"],
                               define_macros=[
                                                 ('USE_PYTHON_MALLOC', 1)
                                              ]
                               )],
      classifiers=classifiers)
