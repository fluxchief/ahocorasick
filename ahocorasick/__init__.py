## fixme: add documentation

import _ahocorasick


__all__ = ['KeywordTree']



class KeywordTree(_ahocorasick.KeywordTree):

## Most of the methods here are just delegated over to the underlying
## C KeywordTree.  But we add a few more convenience functions here.

    def chases(self, sourceStream):
        for block in sourceStream:
            for match in self.findall(block):
                yield (block, match)


    def findall(self, sourceBlock, allow_overlaps=0):
        """Returns all the search matches in the source block.

        If allow_overlaps is true, then we allow subsequent matches to
        overlap."""
        startpos = 0
        while True:
            match = self.search(sourceBlock, startpos)
            if not match:
                break
            yield match
            if allow_overlaps:
                startpos = match[0] + 1
            else:
                startpos = match[1]
        
        
    def chases_long(self, sourceStream):
        for block in sourceStream:
            for match in self.findall_long(block):
                yield (block, match)


    def findall_long(self, sourceBlock, allow_overlaps=0):
        """Returns all the search matches in the source block.

        If allow_overlaps is true, then we allow subsequent matches to
        overlap.  """
        startpos = 0
        while True:
            match = self.search_long(sourceBlock, startpos)
            if not match:
                break
            yield match
            if allow_overlaps:
                startpos = match[0] + 1
            else:
                startpos = match[1]

