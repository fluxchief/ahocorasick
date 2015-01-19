/* Python wrapper code for Aho-Corasick code.  I know I should be
   using some wrapper-generating code, but I'm just practicing my C.
   *grin*

   Danny Yoo (dyoo@hkn.eecs.berkeley.edu)

 */


#include <Python.h>
#include "structmember.h"
#include "aho-corasick.h"


/* We add a few forward declarations here to make C happy. */
staticforward PyTypeObject ahocorasick_KeywordTreeType;
staticforward PyTypeObject ahocorasick_StateType;



/* Keyword Tree structure definition. */
typedef struct {
	PyObject_HEAD
	int count;
	int made;
	aho_corasick_t* tree;
} ahocorasick_KeywordTree;



/* Node structure definition */
typedef struct {
	PyObject_HEAD
	ahocorasick_KeywordTree *tree;
	aho_corasick_state_t *state;
} ahocorasick_State;



/* I also do a forward declaration of the state-wrapping function, since it is
   called in ahocorasick_KeywordTree_zerostate. */
static PyObject* 
ahocorasick_State_make(ahocorasick_KeywordTree *tree,
		       aho_corasick_state_t *state);



/**********************************************************************/
/* Implementation of the KeywordTree follows: */


/* Constructs a new KeywordTree. */
static PyObject* 
ahocorasick_KeywordTree_new(PyTypeObject *type,
			    PyObject *args,
			    PyObject *kwds) {
	ahocorasick_KeywordTree *self;
	self = (ahocorasick_KeywordTree *) type->tp_alloc(type, 0);
	if (self != NULL) {
		self->tree = PyMem_Malloc(sizeof(aho_corasick_t));
		if (self->tree == NULL) {
			Py_DECREF(self);
			return NULL;
		}
		if (aho_corasick_init(self->tree) == -1) {
			Py_DECREF(self);
			return NULL;
		}
		self->count = 0;
		self->made = 0;
	}
	return (PyObject*) self;
}


/* Initializes a KeywordTree. */
static int
ahocorasick_KeywordTree_init(ahocorasick_KeywordTree *self,
			     PyObject *args,
			     PyObject *kwargs) {
	return 0;
}



/* Deallocates the memory used in allocating this thing. */
static void
ahocorasick_KeywordTree_dealloc(ahocorasick_KeywordTree *self) {
	aho_corasick_destroy(self->tree);
	PyMem_Free(self->tree);
	self->ob_type->tp_free((PyObject*) self);
}


/* Adds a new keyword to the KeywordTree. */
static PyObject*
ahocorasick_KeywordTree_add(ahocorasick_KeywordTree *self,
			    PyObject *args,
			    PyObject *kwargs) {
	unsigned char *newKeyword;
	size_t n;
	static char *kwlist[] = {"keyword", NULL};
	if (! PyArg_ParseTupleAndKeywords
	    (args, kwargs, "s#", kwlist, &newKeyword, &n)) {
		return NULL;
	}


	/* Check for empty string: the underlying C implementation function
	   aho_corasick_addstring() crashes on empty string input, so let's
	   catch that before we enter. */
	if (n == 0) {
		PyErr_SetString(PyExc_AssertionError,
				"add() cannot take the empty string");
		return NULL;
	}

	if (self->made) {
		PyErr_SetString(PyExc_AssertionError, 
				"add() cannot be called once a tree has been finalized with make()");
		return NULL;
	}


	/* The only time we get -1 from addstring is on memory error, but
	   let's make sure to trace that. */
	if (aho_corasick_addstring(self->tree, newKeyword, n) == -1) {
		PyErr_SetString(PyExc_MemoryError,
				"internal error: aho_corasick_addstring reports memory allocation error");
		return NULL;
	}
	self->count++;

	Py_INCREF(Py_None);
	return Py_None;
}




/* Given a string, searches for the first keyword.  Either returns None, or a
   2-tuple (start, end).  Since search() and search_long() are so similar, I
   extract the common elements of both here, and specialize by using a helper
   function pointer. */
static PyObject*
ahocorasick_KeywordTree_basesearch(ahocorasick_KeywordTree *self,
				   PyObject *args, PyObject *kwargs,
				   ahocorasick_KeywordTree_search_helper_t helper) {
	unsigned char *queryString;
	size_t start, end;
	static char *kwlist[] = {"query", "startpos", NULL};
	int startpos = 0;
	size_t n;		/* length of queryString */
	if (! PyArg_ParseTupleAndKeywords
	    (args, kwargs, "s#|i", kwlist, &queryString, &n, &startpos)) {
		return NULL;
	}

	/* Check startpos bounds.  Assert that they're within the query
	   string. */
	if (startpos < 0) {
		PyErr_SetString(PyExc_AssertionError,
				"startpos can't be negative.");
		return NULL;
	}
	

	/* Before searching, the KeywordTree must have been make()ed. earlier,
	   or else the search doesn't work. */
	if (!self->made) {
		PyErr_SetString(PyExc_AssertionError,
				"make() must be called before search() to finalize tree construction.");
		return NULL;
	}
	
	if ((*helper)(self->tree, 
		      queryString, n,
		      (size_t) startpos,
		      &start, &end)) {
	  return Py_BuildValue("(ll)", start, end);
	}

	/* If we get to this point, the search has failed. */
	Py_INCREF(Py_None);
	return Py_None; 
}



/* Given a string, searches for the first keyword.  Either returns None, or a
   2-tuple (start, end). */
static PyObject*
ahocorasick_KeywordTree_search(ahocorasick_KeywordTree *self,
			       PyObject *args, PyObject *kwargs) {
	return ahocorasick_KeywordTree_basesearch
		(self, args, kwargs,
		 ahocorasick_KeywordTree_search_helper);
}



/* Given a string, searches for the first keyword.  Either returns None, or a
   2-tuple (start, end).  Tries to match as long a keyword as it can.*/
static PyObject*
ahocorasick_KeywordTree_search_long(ahocorasick_KeywordTree *self,
				    PyObject *args, PyObject *kwargs) {
	return ahocorasick_KeywordTree_basesearch
		(self, args, kwargs,
		 ahocorasick_KeywordTree_search_long_helper);
}






/* Once the keywords have been passed into the tree, maketree does some final
   construction of the keyword tree.

   We must make sure that maketree has not be called multiple times.  If it
   is, ignore the call.
*/
static PyObject*
ahocorasick_KeywordTree_maketree(ahocorasick_KeywordTree *self) {
	/* fixme: only call this if self->count is positive! */
	if (!self->made) {
		if (self->count == 0) {
			PyErr_SetString(PyExc_AssertionError,
					"make() can not be called until at least one string has been add()ed.");
			return NULL;
		}
		aho_corasick_maketree(self->tree);
		self->made = 1;
	}
	Py_INCREF(Py_None);
	return Py_None;
}



/* Allows access to the states and their transitions. */
static PyObject*
ahocorasick_KeywordTree_zerostate(ahocorasick_KeywordTree *self) {
/* 	if (! self->made) { */
/* 		PyErr_SetString(PyExc_AssertionError, */
/* 				"zerostate() can not be called until the tree has been made()."); */
/* 		return NULL; */
/* 	} */
	return ahocorasick_State_make(self, self->tree->zerostate);
}



static PyMemberDef ahocorasick_KeywordTree_members[] = {
	{NULL}			/* sentinel */
};



static PyMethodDef ahocorasick_KeywordTree_methods[] = {
	/* The PyCFunction casts here are necessary to make the C compiler
	   happy.  These functions take ahocorasick_KeywordTree pointers as
	   their first argument. */
	{"add", (PyCFunction) ahocorasick_KeywordTree_add, METH_VARARGS | METH_KEYWORDS,
	 "Add a new keyword to the KeywordTree." },
	{"search", (PyCFunction) ahocorasick_KeywordTree_search, METH_VARARGS | METH_KEYWORDS,
	 "Search for a keyword.  Either returns a 2-tuple \
(start, end), or None." },
	{"search_long", (PyCFunction) ahocorasick_KeywordTree_search_long, METH_VARARGS | METH_KEYWORDS,
	 "Search for a keyword.  Either returns a 2-tuple \
(start, end), or None.  Tries for longest match." },
	{"make", (PyCFunction) ahocorasick_KeywordTree_maketree, METH_NOARGS,
	 "Finishes KeywordTree construction." },
	{"zerostate", (PyCFunction) ahocorasick_KeywordTree_zerostate, METH_NOARGS,
	 "extracts the root zerostate node of the KeywordTree."},
	{NULL}			/* sentinel */
};



/* Let's define the type table stuff. */
static PyTypeObject ahocorasick_KeywordTreeType = {
    PyObject_HEAD_INIT(NULL)
    0,                                                /*ob_size*/
    "ahocorasick.KeywordTree",                        /*tp_name*/
    sizeof(ahocorasick_KeywordTree),                  /*tp_basicsize*/
    0,                                                /*tp_itemsize*/
    (destructor)ahocorasick_KeywordTree_dealloc,      /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    "KeywordTree objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    ahocorasick_KeywordTree_methods,             /* tp_methods */
    ahocorasick_KeywordTree_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc) ahocorasick_KeywordTree_init,      /* tp_init */
    0,                         /* tp_alloc */
    ahocorasick_KeywordTree_new,                 /* tp_new */
};





/************************************************************************/
/* Implementation of the State follows: */


/* Deallocates a state. */
static void
ahocorasick_State_dealloc(ahocorasick_State *self) {
	Py_DECREF(self->tree);
	self->tree = NULL;
	self->state = NULL;
	self->ob_type->tp_free((PyObject*) self);
}



/* Private function: constructs a new State object that wraps around a
   primitive state.
*/
static PyObject*
ahocorasick_State_make(ahocorasick_KeywordTree *tree,
		       aho_corasick_state_t *state) {
	ahocorasick_State* self = (ahocorasick_State *)
		ahocorasick_StateType.tp_alloc(&ahocorasick_StateType, 0);
	if (self != NULL) {
		Py_INCREF(tree);
		self->tree = tree;
		self->state = state;
	}
	return (PyObject*) self;
}
		       
static PyObject*
ahocorasick_State_id(ahocorasick_State *self) {
	return Py_BuildValue("i", self->state->id);
}


static PyObject*
ahocorasick_State_goto(ahocorasick_State *self,
		       PyObject *args,
		       PyObject *kwargs) {

	static char *kwlist[] = {"label", NULL};
	int label;
	if (! PyArg_ParseTupleAndKeywords
	    (args, kwargs, "i", kwlist, &label)) {
		return NULL;
	}
	/* Label must be between 0 and 255, or else we raise
	   AssertionError. */
	if (label < 0 || label >= AHO_CORASICK_CHARACTERS) {
		PyErr_SetString(PyExc_AssertionError,
				"label must be an ordinal between 0 and 255.");
		return NULL;
	}

	if (aho_corasick_goto_get(self->state, label) == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	}

	return ahocorasick_State_make(self->tree,
				      aho_corasick_goto_get(self->state,
							    label));
}


/* Returns the state that the failure transition points to.  In the special
   case of the zerostate, we return None.  */
static PyObject*
ahocorasick_State_fail(ahocorasick_State *self) {
	if (self->state->fail == NULL) {
		/* If we get in here, we're probably at the zerostate. */
		Py_INCREF(Py_None);
		return Py_None;
	}
	return ahocorasick_State_make(self->tree, self->state->fail);
}


/* Returns a list of the non-NULL goto transitions from this state to the
   other states. */
static PyObject*
ahocorasick_State_labels(ahocorasick_State *self) {
	int i;
	PyObject *list;
	PyObject *label;

	if ( (list = PyList_New(0)) == NULL)
		return NULL;

	for(i = 0; i < AHO_CORASICK_CHARACTERS; i++) {
		if (aho_corasick_goto_get(self->state, i) != NULL) {
			if ( (label = Py_BuildValue("i", i)) == NULL) {
				Py_DECREF(list);
				return NULL;
			}
			if (PyList_Append(list, label) == -1) {
				Py_DECREF(label);
				Py_DECREF(list);
				return NULL;
			}
			Py_DECREF(label);
		}
	}
	return list;
}


static PyObject*
ahocorasick_State_output(ahocorasick_State *self) {
	if (self->state->output == 0) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	else {
		return Py_BuildValue("i", self->state->output);
	}
}


static PyMemberDef ahocorasick_State_members[] = {
	{NULL}			/* sentinel */
};


static PyMethodDef ahocorasick_State_methods[] = {
	{"id", (PyCFunction) ahocorasick_State_id, METH_NOARGS,
	 "Returns the id of this State."},

	{"goto", (PyCFunction) ahocorasick_State_goto, METH_VARARGS | METH_KEYWORDS,
	 "Traverses the state transition."},

	{"fail", (PyCFunction) ahocorasick_State_fail, METH_NOARGS,
	 "Traverses the failure transition."},

	{"labels", (PyCFunction) ahocorasick_State_labels, METH_NOARGS,
	 "Returns a list of all goto labels out of this state."},
	{"output", (PyCFunction) ahocorasick_State_output, METH_NOARGS,
	 "Returns None if this state does not output.  Otherwise, returns a positive number."},
	{NULL}			/* sentinel */
};


static PyTypeObject ahocorasick_StateType = {
    PyObject_HEAD_INIT(NULL)
    0,                                                /*ob_size*/
    "ahocorasick.State",                        /*tp_name*/
    sizeof(ahocorasick_State),                  /*tp_basicsize*/
    0,                                                /*tp_itemsize*/
    (destructor)ahocorasick_State_dealloc,      /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
    "State objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    ahocorasick_State_methods,             /* tp_methods */
    ahocorasick_State_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};




/**********************************************************************/
/* Module stuff below: */


/* Module method table. */

static PyMethodDef AhoCorasickMethods[] = {
  {NULL, NULL, 0, NULL}		/* sentinel */
};


#ifndef PyMODINIT_FUNC 		/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_ahocorasick(void) {
	PyObject* m;

	if (PyType_Ready(&ahocorasick_KeywordTreeType) < 0)
		return;

	ahocorasick_StateType.tp_new = PyType_GenericNew;
	if (PyType_Ready(&ahocorasick_StateType) < 0)
		return;


	m = Py_InitModule3("_ahocorasick", AhoCorasickMethods,
			   "Aho-Corasick keyword tree");

	if (m == NULL)
		return;

	Py_INCREF(&ahocorasick_KeywordTreeType);
	Py_INCREF(&ahocorasick_StateType);
	PyModule_AddObject(m, "KeywordTree", 
			   (PyObject*)&ahocorasick_KeywordTreeType);
}

