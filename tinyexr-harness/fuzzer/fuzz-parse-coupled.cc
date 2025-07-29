#define TINYEXR_IMPLEMENTATION
#include "tinyexr.h"

#include <stdint.h>
#include <stdlib.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  const char* err = nullptr;

  if (size < 4) return 0;

  EXRVersion exr_version;
  if (ParseEXRVersionFromMemory(&exr_version, data, size) != 0) {
    return 0;
  }

  EXRHeader header;
  InitEXRHeader(&header);

  if (ParseEXRHeaderFromMemory(&header, &exr_version, data, size, &err) != 0) {
    FreeEXRErrorMessage(err);
    return 0;
  }

  // Request all pixel types as float
  for (int i = 0; i < header.num_channels; ++i) {
    header.requested_pixel_types[i] = TINYEXR_PIXELTYPE_FLOAT;
  }

  EXRImage image;
  InitEXRImage(&image);

  if (LoadEXRImageFromMemory(&image, &header, data, size, &err) == TINYEXR_SUCCESS) {
    FreeEXRImage(&image);
  }

  FreeEXRHeader(&header);
  FreeEXRErrorMessage(err);
  return 0;
}
