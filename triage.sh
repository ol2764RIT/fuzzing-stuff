#!/bin/bash
# Usage: ./triage.sh <inputfile>

INPUT="$1"
REPRO=./main_tester

if [ ! -f "$INPUT" ]; then
  echo "File not found: $INPUT"
  exit 1
fi

# Run repro_min with ASan/UBSan enabled, capture stderr
OUTPUT=$($REPRO "$INPUT" 2>&1)

# If output contains ASan/UBSan error keywords → real crash
if echo "$OUTPUT" | grep -qE "ERROR: AddressSanitizer|runtime error:|==[0-9]+==ERROR"; then
  echo "[CRASH] $INPUT"
  mv -f "$INPUT" artifacts/

# If it just says "Parse error" → expected failure
elif echo "$OUTPUT" | grep -q "Parse error"; then
  echo "[PARSE ERROR] $INPUT"
  mv -f "$INPUT" fake_artifacts/
  # Clear out fake crashes right after moving
  rm -f fake_artifacts/*

# If it runs cleanly, send to corpus
else
  echo "[OK] $INPUT"
fi
