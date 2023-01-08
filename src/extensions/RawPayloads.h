#ifndef ORDERBOOKDASHBACKEND_RAWPAYLOADS_H
#define ORDERBOOKDASHBACKEND_RAWPAYLOADS_H
#include <Python.h>

typedef struct RawItem{
    double* prices;
    double* sizes;
    int length;
} RawItem;

typedef struct RawPayload{
    // Params
    double V_MAX, V_MIN, V_AGG;
    int GRID_MAX_HEIGHT;
    int parse_size;
    // Data
    RawItem* raw_items;
    int raw_items_length;
} RawPayload;

void collect_raw_payload(RawPayload* raw_payload, PyObject* args);
void display_raw_payload(RawPayload* raw_payload);

#endif //ORDERBOOKDASHBACKEND_RAWPAYLOADS_H
