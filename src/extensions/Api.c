#include <Python.h>
#include "MagmaBook.h"

// Module functions
static PyMethodDef functions[] = {
        {"raw_to_computed", raw_to_computed, METH_VARARGS, "Compute a python raw payload"},
};

// Module data
static struct PyModuleDef MagmaBookApi = {
        PyModuleDef_HEAD_INIT,
        "MagmaBookApi",
        NULL,
        -1,
        functions
};

// Module initialization
PyMODINIT_FUNC PyInit_MagmaBookApi(void) {
    PyObject * module = PyModule_Create( &MagmaBookApi );
    if ( module == NULL ) return NULL;
    return module;
}
