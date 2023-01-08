#ifndef ORDERBOOKDASHBACKEND_COMPUTEDPAYLOADS_H
#define ORDERBOOKDASHBACKEND_COMPUTEDPAYLOADS_H
#include "RawPayloads.h"

typedef struct ComputedItem{
    double* depth; // [size, size, size...]
    int depth_length;
} ComputedItem;

typedef struct ComputedPayload{
    // Data
    ComputedItem* computed_items;
    int computed_items_length;
    double* scale;
    int scale_length;
    double treshold;
} ComputedPayload;

void compute_raw_payload(ComputedPayload* computed_payload, RawPayload* raw_payload);
void display_computed_payload(ComputedPayload* computed_payload);

#endif //ORDERBOOKDASHBACKEND_COMPUTEDPAYLOADS_H
