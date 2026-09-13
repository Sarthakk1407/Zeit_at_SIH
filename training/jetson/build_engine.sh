#!/usr/bin/env bash
# build_engine.sh -- ONNX -> TensorRT engine, ON THE JETSON (engines are not portable).
#
#   bash build_engine.sh gtcrn_stream.onnx            # FP16 (start here)
#   bash build_engine.sh gtcrn_stream.onnx fp32
#   bash build_engine.sh gtcrn_stream_int8_qdq.onnx int8
#
# Prints TensorRT's own latency statistics for one frame. The number to quote
# is the worst case (the p99 / max row), not the mean: the hop is 16 ms and a
# single late frame is an audible click.
set -euo pipefail

ONNX="${1:?usage: build_engine.sh model.onnx [fp16|fp32|int8]}"
MODE="${2:-fp16}"
TRTEXEC="${TRTEXEC:-/usr/src/tensorrt/bin/trtexec}"      # JetPack's location
ENGINE="${ONNX%.onnx}_${MODE}.engine"

case "$MODE" in
  fp32) FLAGS="" ;;
  fp16) FLAGS="--fp16" ;;
  int8) FLAGS="--int8 --fp16" ;;        # QDQ model: INT8 where marked, FP16 elsewhere
  *) echo "mode must be fp16, fp32 or int8"; exit 1 ;;
esac

echo "== building $ENGINE ($MODE)"
"$TRTEXEC" --onnx="$ONNX" --saveEngine="$ENGINE" $FLAGS \
           --skipInference

echo "== benchmarking one streaming frame"
"$TRTEXEC" --loadEngine="$ENGINE" --iterations=2000 --warmUp=500 --avgRuns=100 \
           --percentile=50,90,99 | tee "${ENGINE%.engine}_bench.txt" | grep -E "Latency|Throughput"

echo "== done: $ENGINE"
echo "   live test:  python3 realtime.py --onnx $ONNX --trt-$MODE"
