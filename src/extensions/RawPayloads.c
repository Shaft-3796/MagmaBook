#include "RawPayloads.h"
#include "Python.h"

static void collect_raw_item(RawItem* raw_item, PyObject* object, int parse_size){
    PyObject* bids = PyDict_GetItemString(object, "bids");
    PyObject* asks = PyDict_GetItemString(object, "asks");
    int bids_length = PyList_Size(bids);
    int asks_length = PyList_Size(asks);
    raw_item->length = bids_length+asks_length;
    raw_item->prices = (double*) calloc(asks_length+bids_length, sizeof(double)); //TODO FREE
    raw_item->sizes = (double*) calloc(asks_length+bids_length, sizeof(double)); //TODO FREE
    int j=0;
    // Bids
    for (int i=bids_length-1; i>=0; i--){
        PyObject* bid = PyList_GetItem(bids, i);
        raw_item->prices[j] = PyFloat_AsDouble(PyList_GetItem(bid, 0)); // Price
        raw_item->sizes[j] = (parse_size) ? PyFloat_AsDouble(PyList_GetItem(bid, 1))*raw_item->prices[j] : PyFloat_AsDouble(PyList_GetItem(bid, 1)); // Size
        j++;
    }
    // Asks
    for (int i=0; i<asks_length; i++){
        PyObject* ask = PyList_GetItem(asks, i);
        raw_item->prices[j] = PyFloat_AsDouble(PyList_GetItem(ask, 0)); // Price
        raw_item->sizes[j] = (parse_size) ? PyFloat_AsDouble(PyList_GetItem(ask, 1))*raw_item->prices[j] : PyFloat_AsDouble(PyList_GetItem(ask, 1)); // Size
        j++;
    }
}

void collect_raw_payload(RawPayload* raw_payload, PyObject* _args){
    // Params
    PyObject* args;
    PyArg_ParseTuple(_args, "O", &args);
    raw_payload->V_MAX = PyFloat_AsDouble(PyDict_GetItemString(args, "vmax"));
    raw_payload->V_MIN = PyFloat_AsDouble(PyDict_GetItemString(args, "vmin"));
    raw_payload->V_AGG = PyFloat_AsDouble(PyDict_GetItemString(args, "vagg"));
    raw_payload->GRID_MAX_HEIGHT = PyLong_AsLong(PyDict_GetItemString(args, "grid_max_height"));
    raw_payload->parse_size = PyLong_AsLong(PyDict_GetItemString(args, "parse_size"));

    // Data
    PyObject* raw_items = PyDict_GetItemString(args, "items");
    raw_payload->raw_items = (RawItem*) calloc(PyList_Size(raw_items), sizeof(RawItem)); //TODO FREE
    raw_payload->raw_items_length = PyList_Size(raw_items);
    for (int i = 0; i < PyList_Size(raw_items); i++){
        collect_raw_item(&raw_payload->raw_items[i], PyList_GetItem(raw_items, i), raw_payload->parse_size);
    }
}

// DEBUG
void display_raw_item(RawItem* raw_item){
    printf("[MagmaBook debug] Raw item with %d lines\n", raw_item->length);
    for(int i=0; i<raw_item->length; i++){
        printf("%f %f | ", raw_item->prices[i], raw_item->sizes[i]);
    }
    printf("\n");
}

// DEBUG
void display_raw_payload(RawPayload* raw_payload){
    printf("[OBDB debug] Raw payload: V_MAX: %f, V_MIN: %f, V_AGG: %f, Parse_size: %d with %d items\n",
           raw_payload->V_MAX, raw_payload->V_MIN, raw_payload->V_AGG, raw_payload->parse_size, raw_payload->raw_items_length);
    for (int i = 0; i < raw_payload->raw_items_length; i++){
        display_raw_item(&raw_payload->raw_items[i]);
    }
}


