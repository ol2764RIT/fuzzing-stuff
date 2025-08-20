// fuzz_validation.c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <signal.h>
#include <setjmp.h>
#include "ucl.h"

#ifndef MAX_NODES
#  define MAX_NODES 5000
#endif

#ifndef MAX_DEPTH
#  define MAX_DEPTH 32
#endif

static sigjmp_buf g_jmp;

static void fuzz_sig_handler(int sig) {
    (void)sig;
    siglongjmp(g_jmp, 1);
}

#ifdef USE_BALANCED_DELIMS
static bool balanced_delims(const uint8_t *s, size_t n) {
    int braces = 0, brackets = 0;
    bool in_string = false, escape = false;

    for (size_t i = 0; i < n; i++) {
        unsigned char c = s[i];

        if (in_string) {
            if (escape) { escape = false; continue; }
            if (c == '\\') { escape = true;  continue; }
            if (c == '"')  { in_string = false; continue; }
            continue;
        }
        if (c == '"') { in_string = true; continue; }

        if (c == '{') braces++;
        else if (c == '}') { if (--braces < 0) return false; }
        else if (c == '[') brackets++;
        else if (c == ']') { if (--brackets < 0) return false; }
    }
    return !in_string && braces == 0 && brackets == 0;
}
#endif

static size_t count_nodes_limited(const ucl_object_t *o, size_t limit) {
    if (!o) return 0;
    size_t cnt = 0;

    ucl_object_iter_t it = NULL;
    const ucl_object_t *cur;

    while ((cur = ucl_iterate_object(o, &it, true)) != NULL) {
        if (++cnt > limit) return cnt;
        enum ucl_type t = ucl_object_type(cur);
        if (t == UCL_OBJECT || t == UCL_ARRAY) {
            cnt += count_nodes_limited(cur, (limit > cnt) ? (limit - cnt) : 0);
            if (cnt > limit) return cnt;
        }
    }
    return cnt;
}

static bool check_depth_limited(const ucl_object_t *o, int depth, int maxdepth) {
    if (!o) return true;
    if (depth > maxdepth) return false;
    ucl_object_iter_t it = NULL;
    const ucl_object_t *cur;
    while ((cur = ucl_iterate_object(o, &it, true)) != NULL) {
        enum ucl_type t = ucl_object_type(cur);
        if (t == UCL_OBJECT || t == UCL_ARRAY) {
            if (!check_depth_limited(cur, depth + 1, maxdepth)) return false;
        }
    }
    return true;
}

#ifdef HARNESS_PARANOID
static bool schema_sane(const ucl_object_t *schema) {
    if (!schema || ucl_object_type(schema) != UCL_OBJECT) return false;

    ucl_object_iter_t it = NULL;
    const ucl_object_t *v;
    while ((v = ucl_iterate_object(schema, &it, true)) != NULL) {
        const char *k = ucl_object_key(v);
        if (!k) continue;

        if (k[0] == '$' && k[1] == 'r' && k[2] == 'e' && k[3] == 'f' && k[4] == '\0') {
            if (ucl_object_type(v) != UCL_STRING) return false;
            continue;
        }
        if ((k[0]=='p' && k[1]=='r' && k[2]=='o' && k[3]=='p') ||
            (k[0]=='p' && k[1]=='a' && k[2]=='t' && k[3]=='t'))
        {
            if (ucl_object_type(v) != UCL_OBJECT) return false;
            continue;
        }
        if (k[0]=='r' && k[1]=='e' && k[2]=='q') {
            if (ucl_object_type(v) != UCL_ARRAY) return false;
            continue;
        }
        if (k[0]=='t' && k[1]=='y' && k[2]=='p' && k[3]=='e') {
            enum ucl_type t = ucl_object_type(v);
            if (!(t == UCL_STRING || t == UCL_ARRAY)) return false;
            continue;
        }
        if (k[0]=='i' && k[1]=='t' && k[2]=='e' && k[3]=='m') {
            enum ucl_type t = ucl_object_type(v);
            if (!(t == UCL_OBJECT || t == UCL_ARRAY)) return false;
            continue;
        }
    }
    return true;
}
#endif

int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size < 4) return 0;

#ifdef USE_BALANCED_DELIMS
    if (!balanced_delims(Data, Size)) return 0;
#endif

    const size_t mid = Size / 2;

    struct ucl_parser *ps = ucl_parser_new(0);
    struct ucl_parser *po = ucl_parser_new(0);
    if (!ps || !po) goto out;

    (void)ucl_parser_add_chunk(ps, Data, mid);
    (void)ucl_parser_add_chunk(po, Data + mid, Size - mid);

    if (ucl_parser_get_error(ps) || ucl_parser_get_error(po)) goto out;

    ucl_object_t *schema = ucl_parser_get_object(ps);
    ucl_object_t *obj    = ucl_parser_get_object(po);

    if (!schema || !obj) {
        if (schema) ucl_object_unref(schema);
        if (obj)    ucl_object_unref(obj);
        goto out;
    }

    if (ucl_object_type(schema) != UCL_OBJECT) {
        ucl_object_unref(schema);
        ucl_object_unref(obj);
        goto out;
    }

    if (count_nodes_limited(schema, MAX_NODES) > MAX_NODES ||
        count_nodes_limited(obj,    MAX_NODES) > MAX_NODES ||
        !check_depth_limited(schema, 0, MAX_DEPTH)         ||
        !check_depth_limited(obj,    0, MAX_DEPTH)) {
        ucl_object_unref(schema);
        ucl_object_unref(obj);
        goto out;
    }

#ifdef HARNESS_PARANOID
    if (!schema_sane(schema)) {
        ucl_object_unref(schema);
        ucl_object_unref(obj);
        goto out;
    }
#endif

    struct ucl_schema_error err;
    void (*old_segv)(int) = signal(SIGSEGV, fuzz_sig_handler);
    void (*old_bus) (int) = signal(SIGBUS,  fuzz_sig_handler);
    void (*old_ill) (int) = signal(SIGILL,  fuzz_sig_handler);

    if (!sigsetjmp(g_jmp, 1)) {
        (void)ucl_object_validate(schema, obj, &err);
    }
    signal(SIGSEGV, old_segv);
    signal(SIGBUS,  old_bus);
    signal(SIGILL,  old_ill);

    ucl_object_unref(schema);
    ucl_object_unref(obj);

out:
    if (ps) ucl_parser_free(ps);
    if (po) ucl_parser_free(po);
    return 0;
}
