#!/bin/bash

BASE_DATA_PATH=/home/gpu-admin/workspace/dataset/SpeechParaling-Bench/audio_dataset_ch
API_KEY=sk-2bc5f2b241bd4743b0b7878b824a39d5
OUTPUT_BASE_PATH="output_ch"

find "$BASE_DATA_PATH" -type f -name "*.wav" | xargs dirname | sort -u | while read -r DIR; do
    
    REL_PATH="${DIR#$BASE_DATA_PATH/}"
    
    echo "=========================================================="
    echo " Processing in batch, now processing: $REL_PATH"
    echo "=========================================================="
    
    python run_sample_parallel_v2.py \
        --input_dir "$DIR" \
        --output_dir "$OUTPUT_BASE_PATH/$REL_PATH" \
        --api_key "${API_KEY}" \
        --language zh
done