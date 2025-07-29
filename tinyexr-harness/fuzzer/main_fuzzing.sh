#!/bin/bash
set -euo pipefail

FUZZERS=(fuzz-load-exr fuzz-parse-coupled fuzz-parse-exr)

mkdir -p crashes corpus mutated

JOBS=12
WORKERS=1
RSS_LIMIT=8192  # Increased memory limit

echo "Available fuzzers:"
for i in "${!FUZZERS[@]}"; do
  echo "$((i+1))) ${FUZZERS[i]}"
done

echo "fuzz-load-exr is fuzzed enough to diminishing returns, do not choose"
echo "fuzz-parse-coupled is fuzzed enough to diminishing returns, do not choose"
echo "fuzz-parse-exr" is fuzzed enough to diminshing returns"
read -rp "Select the fuzzer to run (1-${#FUZZERS[@]}): " choice

if ! [[ "$choice" =~ ^[1-9][0-9]*$ ]] || (( choice < 1 || choice > ${#FUZZERS[@]} )); then
  echo "Invalid choice."
  exit 1
fi

selected_fuzzer="${FUZZERS[choice-1]}"

echo "Running $selected_fuzzer..."

./"$selected_fuzzer" -jobs="$JOBS" -workers="$WORKERS" ./corpus \
  -artifact_prefix=crashes/"$selected_fuzzer"- \
  -max_len=8192 \
  -rss_limit_mb=$RSS_LIMIT \
  -use_value_profile=1 \
  -use_cmp=1 \
  -use_memmem=1 \
  -cross_over=1 \
  -detect_leaks=0

echo "Merging corpus for $selected_fuzzer..."

./"$selected_fuzzer" -merge=1 -use_value_profile=1 -artifact_prefix=crashes/"$selected_fuzzer"- ./corpus ./mutated

echo "Done."
