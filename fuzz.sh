#!/bin/bash
set -euo pipefail

# Paths
INCLUDE_DIR="../../include"
SRC_DIR="../../src"
UTHASH_DIR="../../uthash"
LIB="../../src/.libs/libucl.a"
LIBUCL_ROOT="../.."   # project root (adjust if needed)

# Compiler + flags
CC=clang
SAN_FLAGS="-O1 -g -fsanitize=address"
CFLAGS="$SAN_FLAGS -I${INCLUDE_DIR} -I${SRC_DIR} -I${UTHASH_DIR}"

# Usage helper
usage() {
    echo "Usage: $0 {build|fuzz} [args...]"
    echo
    echo "  build           Rebuild libucl with sanitizers and compile fuzz targets"
    echo "  fuzz [options]  Run fuzz_ucl_parser with options (default: -fork=8 -ignore_crashes=1 -use_value_profile=1)"
    exit 1
}

# Ensure we’re in the right place
if [[ ! -f fuzz_ucl_parser.c ]]; then
    echo "Run this script from the fuzzing-campaign-1 directory"
    exit 1
fi

cmd="${1:-}"
shift || true

case "$cmd" in
    build)
        echo "[*] Rebuilding libucl with sanitizers..."
        (
            cd "$LIBUCL_ROOT"
            make clean || true
            export CC=clang
            export CFLAGS="$SAN_FLAGS"
            export CXXFLAGS="$SAN_FLAGS"
            ./configure
            make -j$(nproc)
        )


        echo "[*] Building fuzz_ucl_parser..."
        $CC -O1 -g \
            -fsanitize=fuzzer,address \
            -I${INCLUDE_DIR} -I${SRC_DIR} -I${UTHASH_DIR} \
            fuzz_ucl_parser.c $LIB -o fuzz_ucl_parser

        echo "[*] Building repro_min..."
        $CC $CFLAGS fuzz_min.c $LIB -o repro_min

        echo "[*] Building main_tester..."
        $CC $CFLAGS main_tester.c $LIB -o main_tester

        echo "[+] Build complete with ASan/UBSan instrumentation."
        ;;
    fuzz)
        echo "[*] Starting fuzzing..."
        FUZZ_ARGS=("$@")
        if [ ${#FUZZ_ARGS[@]} -eq 0 ]; then
            FUZZ_ARGS=(-fork=8 -ignore_crashes=1 -use_value_profile=1 seed_corpus/ -dict=ucl.dict)
        fi

        ./fuzz_ucl_parser "${FUZZ_ARGS[@]}"
        ;;
    *)
        usage
        ;;
esac
