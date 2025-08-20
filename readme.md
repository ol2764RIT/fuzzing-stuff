# Fuzzing libucl – 10 Day Campaign

This repository documents a 10-day fuzzing campaign targeting [libucl](https://github.com/vstakhov/libucl), a universal configuration language library. The goal was to explore the parser and schema validation logic using libFuzzer with sanitizers and custom harnesses.

---

## Repository Layout

```

fuzzing-campaign-1/
├── fuzz.sh              # Build + fuzz orchestration script
├── fuzz\_validation.c    # Custom libFuzzer harness for schema + object validation
├── main\_tester.c        # Minimal repro driver (ASan/UBSan enabled)
├── triage.sh            # Crash triage script
├── ucl.dict             # libFuzzer dictionary (tokens & keywords)
├── validation\_corpus/   # Seed inputs
├── writeup.md           # This writeup

````

---

## Setup & Build

The fuzzing harnesses use clang, libFuzzer, and AddressSanitizer (ASan).

To rebuild everything:

```bash
./fuzz.sh build
````

This:

* Rebuilds libucl with sanitizers
* Compiles fuzz targets (`fuzz_ucl_parser`, `repro_min`)
* Compiles a standalone tester (`main_tester`)

---

## Running the Fuzzer

Default run:

```bash
./fuzz.sh fuzz
```

This runs `fuzz_ucl_parser` with:

* `-fork=8` (parallel workers)
* `-ignore_crashes=1`
* `-use_value_profile=1`
* `seed_corpus/` (initial seeds)
* `ucl.dict` (custom tokens)

Additional options can be passed directly, for example:

```bash
./fuzz.sh fuzz -max_total_time=3600
```

---

## Triage & Repro

After fuzzing, inputs are replayed against `main_tester` and categorized:

```bash
./triage.sh <input>
```

* `[CRASH]` → Real bug (ASan/UBSan triggered, saved under `artifacts/`)
* `[PARSE ERROR]` → Expected parse failure (discarded)
* `[OK]` → Valid input

---

## Fuzzing Harnesses

### `fuzz_validation.c`

* Splits input in half → one half as a schema, one half as an object
* Applies depth and node count limits to prevent runaway recursion
* Validates objects against schema with `ucl_object_validate`
* Protects against `SIGSEGV`, `SIGBUS`, `SIGILL` using `sigsetjmp`

Optional modes:

* `USE_BALANCED_DELIMS`: Require `{}` / `[]` matching
* `HARNESS_PARANOID`: Enforce stricter schema sanity checks

### `main_tester.c`

* Standalone repro program
* Useful for ASan-based crash verification

---

## Findings

Over the 10-day campaign:

* Generated thousands of unique inputs
* Observed crashes in schema validation when closing delimiters were not balanced
* Triage showed these were parse errors, not exploitable memory bugs
* Achieved deeper coverage by combining dictionary seeding with split-schema fuzzing

---

## Lessons Learned

1. Schema/object separation fuzzing increased code coverage compared to raw fuzzing
2. Balanced delimiter filtering improved input quality and execution depth
3. Automated triage was essential, reducing false positives significantly
4. libucl’s parser is resilient, with most issues reducing to parse errors rather than memory safety bugs

---

## Next Steps

* Extend harness with custom mutators for schema keywords
* Run with different sanitizers (MSan, TSan)

```
