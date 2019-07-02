//anirb

#include <stdio.h>
#include <inttypes.h>
#include <math.h>
#include <string.h>

#include "libbf.h"

#define CHUD_A 13591409
#define CHUD_B 545140134
#define CHUD_C 640320
/* log2(C/12)*3 */
#define CHUD_BITS_PER_TERM 47.11041313821584202247

/* number of bits per base 10 digit */
#define BITS_PER_DIGIT 3.32192809488736234786

static bf_context_t bf_ctx;

static void *my_bf_realloc(void *opaque, void *ptr, size_t size) {
    return realloc(ptr, size);
}

static void chud_bs(bf_t *P, bf_t *Q, bf_t *G, int64_t a, int64_t b, int need_g,
                    limb_t prec) {
    int64_t c;

    if (a == (b - 1)) {
        bf_t T0, T1;
        
        bf_init(&bf_ctx, &T0);
        bf_init(&bf_ctx, &T1);
        bf_set_ui(G, 2 * b - 1);
        bf_mul_ui(G, G, 6 * b - 1, prec, BF_RNDN);
        bf_mul_ui(G, G, 6 * b - 5, prec, BF_RNDN);
        bf_set_ui(&T0, CHUD_B);
        bf_mul_ui(&T0, &T0, b, prec, BF_RNDN);
        bf_set_ui(&T1, CHUD_A);
        bf_add(&T0, &T0, &T1, prec, BF_RNDN);
        bf_mul(P, G, &T0, prec, BF_RNDN);
        P->sign = b & 1;

        bf_set_ui(Q, b);
        bf_mul_ui(Q, Q, b, prec, BF_RNDN);
        bf_mul_ui(Q, Q, b, prec, BF_RNDN);
#if LIMB_BITS == 64
        bf_mul_ui(Q, Q, (uint64_t)CHUD_C * CHUD_C * CHUD_C / 24, prec, BF_RNDN);
#else
        bf_mul_ui(Q, Q, CHUD_C, prec, BF_RNDN);
        bf_mul_ui(Q, Q, CHUD_C, prec, BF_RNDN);
        bf_mul_ui(Q, Q, CHUD_C / 24, prec, BF_RNDN);
#endif
        bf_delete(&T0);
        bf_delete(&T1);
    } else {
        bf_t P2, Q2, G2;
        
        bf_init(&bf_ctx, &P2);
        bf_init(&bf_ctx, &Q2);
        bf_init(&bf_ctx, &G2);

        c = (a + b) / 2;
        chud_bs(P, Q, G, a, c, 1, prec);
        chud_bs(&P2, &Q2, &G2, c, b, need_g, prec);
        
        /* Q = Q1 * Q2 */
        /* G = G1 * G2 */
        /* P = P1 * Q2 + P2 * G1 */
        bf_mul(&P2, &P2, G, prec, BF_RNDN);
        if (!need_g)
            bf_set_ui(G, 0);
        bf_mul(P, P, &Q2, prec, BF_RNDN);
        bf_add(P, P, &P2, prec, BF_RNDN);
        bf_delete(&P2);

        bf_mul(Q, Q, &Q2, prec, BF_RNDN);
        bf_delete(&Q2);
        if (need_g)
            bf_mul(G, G, &G2, prec, BF_RNDN);
        bf_delete(&G2);
#if 0
        printf("%" PRId64 "-%" PRId64 " limbs: P=%" PRId64 " Q=%" PRId64 " G=%" PRId64 "\n",
               a, b, P->len, Q->len, G->len);
#endif
    }
}


static void pi_chud(bf_t *Q, int64_t prec) {
    int64_t n, prec1;
    bf_t P, G;

    /* number of serie terms */
    n = (int64_t)ceil(prec / CHUD_BITS_PER_TERM) + 10;
    prec1 = prec + 32;

    bf_init(&bf_ctx, &P);
    bf_init(&bf_ctx, &G);

    chud_bs(&P, Q, &G, 0, n, 0, prec1);
    
    bf_mul_ui(&G, Q, CHUD_A, prec1, BF_RNDN);
    bf_add(&P, &G, &P, prec1, BF_RNDN);
    
    bf_div(Q, Q, &P, prec1, BF_RNDF);
 
    bf_set_ui(&P, CHUD_C / 64);
    bf_rsqrt(&G, &P, prec1);
    bf_mul_ui(&G, &G, (uint64_t)CHUD_C * CHUD_C / (8 * 12), prec1, BF_RNDF);

    bf_mul(Q, Q, &G, prec, BF_RNDN);
    
    bf_delete(&P);
    bf_delete(&G);
}

int main(int argc, char **argv) {
    bf_t PI;
    int32_t n_digits, prec, n_bits;
    char *digits;
    size_t digits_len;

	n_digits = 50;
    n_bits = (limb_t)ceil(n_digits * BITS_PER_DIGIT);
    prec = n_bits + 32;

    bf_context_init(&bf_ctx, my_bf_realloc, NULL);
    bf_init(&bf_ctx, &PI);

    pi_chud(&PI, prec);

    digits_len = bf_ftoa(&digits, &PI, 10, n_digits + 1,
                             BF_FTOA_FORMAT_FIXED | BF_RNDZ);

	printf ("dec value is %s\n", digits);
    digits_len = bf_ftoa(&digits, &PI, 16, n_bits / 4,
                             BF_FTOA_FORMAT_FIXED | BF_RNDZ);
	printf ("hex value is %s\n", digits);

    bf_t PI;
	return 0;
}
