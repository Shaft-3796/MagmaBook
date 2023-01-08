#include "ComputedPayloads.h"
#include "RawPayloads.h"
#include <stdlib.h>
#include <stdio.h>


void compute_raw_payload(ComputedPayload* computed_payload, RawPayload* raw_payload){
    // Base conversion
    computed_payload->computed_items_length = raw_payload->raw_items_length;
    // Treshold
    int grid_height = 1+(raw_payload->GRID_MAX_HEIGHT-1)*(raw_payload->V_AGG/100.0);
    double treshold = (raw_payload->V_MAX - raw_payload->V_MIN) / grid_height;
    computed_payload->treshold = treshold; // for DEBUG
    computed_payload->scale_length = (raw_payload->V_MAX-raw_payload->V_MIN)/treshold+1;
    // Scale computing
    computed_payload->scale = (double*) calloc(computed_payload->scale_length, sizeof(double)); //TODO FREE
    for(int i=0; i<computed_payload->scale_length; i++){
        computed_payload->scale[i] = raw_payload->V_MIN + i*treshold;
    }
    computed_payload->scale[computed_payload->scale_length-1] = raw_payload->V_MAX;

    // Items computing
    computed_payload->computed_items = (ComputedItem*) calloc(computed_payload->computed_items_length, sizeof(ComputedItem)); //TODO FREE
    for(int item_index=0; item_index<raw_payload->raw_items_length; item_index++) {
        RawItem* item = &(raw_payload->raw_items[item_index]);
        ComputedItem computed_item = {};
        int scale_index = 0;
        computed_item.depth_length = computed_payload->scale_length-1;
        computed_item.depth = (double *) calloc(computed_item.depth_length, sizeof(double)); //TODO FREE
        for (int i = 0; i < item->length; i++) {
            double price = item->prices[i];
            double size = item->sizes[i];
            // Handle limits
            if(price < raw_payload->V_MIN){
                continue;
            }
            if(price > raw_payload->V_MAX){
                break;
            }
            if(computed_payload->scale[scale_index] <= price && price < computed_payload->scale[scale_index+1]){
                computed_item.depth[scale_index] += size;
            } else {
                if(scale_index+1 == computed_payload->scale_length-1){
                    computed_item.depth[scale_index] += size;
                }
                else{
                    scale_index++;
                    i--;
                }
            }

        }
        computed_payload->computed_items[item_index] = computed_item;
    }
}


// DEBUG
void display_computed_payload(ComputedPayload* computed_payload){
    printf("--------------------------------------\n");
    printf("computed_items_length: %d\n", computed_payload->computed_items_length);
    printf("scale_length: %d\n", computed_payload->scale_length);
    printf("treshold: %f\n", computed_payload->treshold);
    printf("scale: ");
    for(int i=0; i<computed_payload->scale_length; i++){
        printf("%f ", computed_payload->scale[i]);
    }
    printf("\n");
    for(int i=0; i<computed_payload->computed_items_length; i++){
        printf("-> computed_item %d: ", i);
        for(int j=0; j<computed_payload->computed_items[i].depth_length; j++){
            printf("%f ", computed_payload->computed_items[i].depth[j]);
        }
        printf("\n");
    }
}
