"""Produces graphviz .dot output of a KeywordTree.  Much of this is
mimicing the example FSM from the Graphviz gallery here:

    http://www.graphviz.org/Gallery/directed/fsm.html

The only function that's intended for the public is dotty().
Everything else is meant to be private.

This code is really really messy.  I'm sorry!  *grin*
"""


def dotty(kwtree, name="finite_state_machine"):
    """Returns a string that represents the dot file."""
    zerostate = kwtree.zerostate()
    out_names = []
    for child in children(zerostate):
	out_names.extend(map(state_name, output_states(zerostate)))
    edge_triplets = []
    for (label, child) in child_edges(zerostate):
	edge_triplets.append((zerostate, label, child))
	edge_triplets.extend(all_edges(child))
    edge_names = map(lambda (s1, label, s2): 
		     '%s -> %s [ label = "%s"]' % (state_name(s1), 
						   state_name(s2),
						   chr(label)),
		     edge_triplets)
    return """
digraph %(name)s {
    rankdir=LR;
    size="8,11"
    orientation=land;
    node [shape = doublecircle]; %(output_states)s
    node [shape = circle];
    %(edges)s
}
""" % { 'name' : name,
	'output_states' : ' '.join(out_names),
	'edges' : '\n'.join(edge_names),
	}


def state_name(state):
    return "STATE_%s" % state.id()


def child_edges(state):
    """Small utility function to get the edges."""
    for label in state.labels():
	if state.goto(label).id() != 0:
	    yield (label, state.goto(label))


def children(state):
    """Small utility function to get the neighbors.  Note: we filter out
    anything with an id of 0."""
    for label in state.labels():
	if state.goto(label).id() != 0:
	    yield state.goto(label)


def all_edges(state):
    """Returns a list of all (state, label, state) triplets reachable from
    this state."""
    if state == None:
	return []
    edges = []
    for edge, child in child_edges(state):
	edges.append((state, edge, child))
    for child in children(state):
	edges.extend(all_edges(child))
    return edges


def output_states(state):
    """Return a list of all the output states reachable from this state."""
    if state == None:
	return []
    outputs = []
    if state.output() != None:
	outputs.append(state)
    for child in children(state):
	outputs.extend(output_states(child))
    return outputs
