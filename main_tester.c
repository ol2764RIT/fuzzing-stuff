#include <ucl.h>
#include <stdio.h>

int main(void) {
    const char *bad = "{ {";  // malformed schema
    struct ucl_parser *p = ucl_parser_new(0);
    if (!p) {
        fprintf(stderr, "Failed to allocate parser\n");
        return 1;
    }

    ucl_parser_add_string(p, bad, 0);
    ucl_object_t *schema = ucl_parser_get_object(p);

    if (schema == NULL) {
        fprintf(stderr, "Parser returned NULL schema (bad input)\n");
        ucl_parser_free(p);
        return 1;
    }

    ucl_object_validate(schema, NULL, NULL);

    ucl_object_unref(schema);
    ucl_parser_free(p);
    return 0;
}
