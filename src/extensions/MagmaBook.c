#include <Python.h>
#include "RawPayloads.h"
#include "ComputedPayloads.h"

PyObject* raw_to_computed(PyObject* self, PyObject* args) {
    // PLACEHOLDERS
    RawPayload raw_payload = {};
    ComputedPayload computed_payload= {};
    PyObject* return_payload = PyDict_New();

    collect_raw_payload(&raw_payload, args);
    //display_raw_payload(&raw_payload);

    compute_raw_payload(&computed_payload, &raw_payload);
    //display_computed_payload(&computed_payload);

    // return computed_payload to python
    /*
    PyObject* scale = PyList_New(computed_payload.scale_length);
    for(int i=0; i<computed_payload.scale_length; i++){
        PyList_SetItem(scale, i, PyFloat_FromDouble(computed_payload.scale[i]));
    }
    PyDict_SetItemString(return_payload, "scale", scale);
     */
    // Items
    PyObject* items = PyList_New(computed_payload.computed_items_length);
    for(int i=0; i<computed_payload.computed_items_length; i++){
        ComputedItem item = computed_payload.computed_items[i];
        // Depth
        PyObject* depth = PyList_New(item.depth_length);
        for(int j=0; j<item.depth_length; j++){
            PyList_SetItem(depth, j, PyFloat_FromDouble(item.depth[j]));
        }
        PyList_SetItem(items, i, depth);
    }
    PyDict_SetItemString(return_payload, "items", items);

    /* MEMORY FREEING */
    // Raw payloads

    for(int i=0; i<raw_payload.raw_items_length; i++){
        RawItem item = raw_payload.raw_items[i];
        free(item.prices);
        free(item.sizes);
    }
    free(raw_payload.raw_items);
    // Computed payloads
    free(computed_payload.scale);
    for(int i=0; i<computed_payload.computed_items_length; i++){
        ComputedItem item = computed_payload.computed_items[i];
        free(item.depth);
    }
    free(computed_payload.computed_items);

    return Py_BuildValue("O", return_payload);
}