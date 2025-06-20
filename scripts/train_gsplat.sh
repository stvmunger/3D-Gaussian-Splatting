#!/usr/bin/env bash
set -e
cd extern/gaussian-splatting

python train.py \
  -s ../../data/my_object \
  -m ../../outputs/my_object_3dgs_r2 \
  --iterations 30000 \
  -r 2 \
  --data_device cpu \
  --densify_until_iter 15000 \
  --densify_grad_threshold 0.0005 \
  --test_iterations 5000 15000 30000 \
  --save_iterations 15000 30000 \
  --checkpoint_iterations 5000 15000 30000 \
  --eval
