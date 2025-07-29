## Fuzzing `miniz`: Exploring Edge Cases in ZIP Parsing

### Objective

The goal of this fuzzing project was to evaluate the robustness of [`miniz`](https://github.com/richgel999/miniz), a lightweight compression library, against malformed and adversarial ZIP inputs. I focused on testing the decompression (`inflate`) logic for its ability to safely and correctly handle both valid and pathological inputs, with an emphasis on memory safety and potential denial-of-service (DoS) vectors.

### Fuzz Target

A custom fuzzer was written against `mz_inflate()`, the decompression API, using libFuzzer:

```c
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    ...
    mz_stream stream;
    stream.next_in = data;
    stream.avail_in = size;
    stream.next_out = out_buf;
    stream.avail_out = OUT_BUF_SIZE;

    if (mz_inflateInit(&stream) != MZ_OK) {
        ...
    }

    mz_inflate(&stream, MZ_FINISH);
    mz_inflateEnd(&stream);
    ...
}
```

The focus was solely on decompression, under the assumption that inputs may be externally controlled or corrupted in untrusted environments.

### Dictionary

A custom fuzzing dictionary (`miniz.dict`) was constructed to boost input mutation effectiveness:

```text
"\x50\x4b\x03\x04"   // local file header
"\x50\x4b\x01\x02"   // central dir header
"\x50\x4b\x05\x06"   // EOCD marker
"\x00\x00"           // common padding/null
"\x08\x00"           // deflate method
"\xFF\xFF"           // length overflows
```

This dictionary was intended to improve discovery of parsing edge cases around key ZIP structures.

### Input Corpus

I curated a highly structured and diverse ZIP corpus categorized into:

#### ✅ Valid Inputs

* Empty archives
* Single and multi-file zips (compressed/uncompressed)
* Long filenames (200+ chars)
* Large file (>1MB)
* Nested zips
* Timestamps and nonstandard metadata

#### ⚠️ Edge Cases

* Corrupted headers (bit-flips at specific offsets)
* Truncated archives
* Zero-length files
* Invalid compression methods (e.g., 0x99)
* ZIPs with zero-width characters in filenames
* Right-to-left override characters (e.g. `normal‮fdp.exe.zip`)
* Unicode filenames (Arabic, Chinese, emoji)
* Hidden executable tricks (`.jpg.exe.zip`)
* DOS-reserved filenames (`com1.txt`, `nul.txt`)
* Files with no `.zip` extension
* Generated a chain of nested ZIPs, up to 20 layers deep

All corpus generation was automated in Python using the `zipfile` module, allowing repeatability and easy scaling.

### Observations

* **OOM behavior**: Inputs with five levels of nested compression (compressed data within compressed zips) began causing memory pressure on a 16GB machine. While this did not crash the library, it highlights potential for **resource exhaustion DoS** under naive usage.
* **Decompression errors** were consistently handled gracefully. Inputs that failed to inflate did not crash `miniz`, and the fuzzer did not discover memory corruption or control-flow violations under ASan/UBSan.

### Conclusion

No crashes, memory corruptions, or use-after-free vulnerabilities were found in this effort. However:

* The test inputs revealed that **nested compression can lead to high memory usage**, which could be abused for denial-of-service attacks if users do not impose explicit limits on nesting, size, or output expansion.
* This behavior is not unique to `miniz`; it reflects a common **ZIP bomb class of vulnerability**.

### Future Work

* Extend fuzzing to ZIP parsing rather than raw deflate streams
* Pivot to AFL++ with QEMU mode to explore deeper edge cases
