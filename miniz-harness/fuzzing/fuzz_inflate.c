#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "miniz.h"

// Fuzzer entry point
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // Skip if input is too small to be valid
    if (size < 1)
        return 0;

    // Allocate a reasonable output buffer (you can fuzz this too, but keep it static for now)
    const size_t OUT_BUF_SIZE = 4096;
    uint8_t *out_buf = (uint8_t *)malloc(OUT_BUF_SIZE);
    if (!out_buf)
        return 0;

    // Initialize inflate stream
    mz_stream stream;
    memset(&stream, 0, sizeof(stream));
    stream.next_in = data;
    stream.avail_in = size;
    stream.next_out = out_buf;
    stream.avail_out = OUT_BUF_SIZE;

    // Initialize inflate
    if (mz_inflateInit(&stream) != MZ_OK) {
        free(out_buf);
        return 0;
    }

    // Try to inflate
    mz_inflate(&stream, MZ_FINISH); // Don't worry about return value — we're testing robustness
    mz_inflateEnd(&stream);

    free(out_buf);
    return 0;
}
