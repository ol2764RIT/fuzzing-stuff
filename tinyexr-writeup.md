## Fuzzing `tinyexr`: Stress-Testing EXR Decoding Logic

### Objective

This project evaluated the robustness of `tinyexr`, a minimal OpenEXR decoder, by targeting its EXR parsing and decoding logic with malformed and edge-case image inputs. The focus was on memory safety, undefined behavior, and denial-of-service vectors, using structured and randomized inputs across multiple fuzz targets.

### Fuzz Targets

Three fuzzers were developed using `tinyexr`’s API, each targeting a distinct stage of the decoding pipeline:

* `fuzz-load-exr`: Full decode to floating-point buffer via `LoadEXRFromMemory`
* `fuzz-parse-coupled`: Parses header and loads pixel data using explicitly requested float channels
* `fuzz-parse-exr`: Only parses version and header

Each target was compiled with AddressSanitizer and UndefinedBehaviorSanitizer. Multiple versions of each fuzzer were used to allow parallel scaling, and memory/resource limits were configured for high-throughput batch runs.

### Corpus Strategy

#### Seed Corpus

Valid EXR images were collected from the OpenEXR sample suite and other sources. The corpus included:

* RGB and grayscale EXRs
* Tiled and scanline storage formats
* Deep EXRs with non-standard layers
* 16-bit and 32-bit floating-point data
* Non-RGB layouts such as CMYK, XYZ, and alpha-only channels

#### Mutations

A Python-based harness was built to:

* Flatten directory trees to eliminate nested corpus structures
* Apply Radamsa mutations to each file
* Generate five mutated variants per input
* Output to a dedicated mutated corpus directory

This introduced randomized byte-level corruption while preserving valid headers in some variants to explore deeper parsing paths.

### Execution

Fuzzing was configured to run in a scalable manner across multiple jobs and machines:

* Parallelized using `-jobs` and `-workers`
* Configurable RSS memory limit (typically 8GB)
* Input length capped at 8192 bytes
* Enabled libFuzzer instrumentation: value profiling, comparisons, crossover, memmem
* Crashes isolated with unique prefixes per fuzzer
* Corpus merged using `-merge=1` after mutation

This design allowed simultaneous fuzzing of multiple fuzzer versions, each potentially exploring different regions of the input space.

### Results

No crashes, memory corruptions, or undefined behavior were detected. Specific outcomes include:

* Malformed EXR headers were rejected cleanly by the parser
* Images using unusual color channel layouts (e.g., CMYK, XYZ) were handled without failure, though high-resolution cases showed increased memory usage
* Memory usage scaled linearly with pixel resolution and channel count, but did not exceed configured limits

### Conclusion

`tinyexr` is already included in OSS-Fuzz, and its core APIs appear hardened against malformed inputs. This independent fuzzing effort reinforced that finding memory safety issues in this codebase is nontrivial. While no vulnerabilities were discovered, this process highlighted:

* The need for user-side validation, especially around memory budgeting
* The benefits of using a diverse and rich corpus when fuzzing complex binary formats like EXR
* The value of targeting multiple stages of a decoding pipeline separately

### Takeaways

Even with upstream continuous fuzzing via OSS-Fuzz, targeted fuzzing with real-world corpus diversity and structural mutation can complement coverage and provide assurance. Combining multiple fuzzers, explicit pixel format manipulation, and controlled mutation strategies can uncover functional edge cases or resource consumption issues that OSS-Fuzz configurations may not prioritize.
