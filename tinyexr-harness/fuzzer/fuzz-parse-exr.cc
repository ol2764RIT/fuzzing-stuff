#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define TINYEXR_IMPLEMENTATION
#include "tinyexr.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  const char *err = nullptr;

  EXRVersion exr_version;
  if (ParseEXRVersionFromMemory(&exr_version, data, size) != 0) {
    return 0;  // Not a valid EXR
  }

  EXRHeader header;
  InitEXRHeader(&header);

  if (ParseEXRHeaderFromMemory(&header, &exr_version, data, size, &err) == 0) {
    FreeEXRHeader(&header);
  }

  FreeEXRErrorMessage(err);
  return 0;
}
