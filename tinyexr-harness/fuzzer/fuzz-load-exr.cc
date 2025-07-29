#define TINYEXR_IMPLEMENTATION
#include "tinyexr.h"

#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  const char* err = nullptr;

  // EXR Data initlization
  float* out_rgba = nullptr;
  int width = 0, height = 0;

  // Load image from memory
  LoadEXRFromMemory(&out_rgba, &width, &height, data, size, &err);

  // Free if successful
  free(out_rgba);
  FreeEXRErrorMessage(err);

  return 0;
}
