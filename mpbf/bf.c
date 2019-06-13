//anirb

#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <math.h>
#include <string.h>

#include "libbf.h"
#include "bf.h"

#ifdef BARE_M
#include "mpconfig.h"
#include "misc.h"
#define realloc m_realloc
#define free m_free
#endif

/* number of bits per base 10 digit */
#define BITS_PER_DIGIT 3.32192809488736234786

static bf_context_t bf_ctx;

static void *my_bf_realloc(void *opaque, void *ptr, size_t size) {
    return realloc(ptr, size);
}

void bf_initialize (void) {
    bf_context_init(&bf_ctx, my_bf_realloc, NULL);
}

void bf_exit (void) {
    bf_context_end(&bf_ctx);
}

void reverse (char* s) {
	//K&R
	int c, i, j;

	for (i = 0, j = strlen(s) -1; i < j; i++, j--){
		c = s[i];
		s[i] = s[j];
		s[j] = c;
	}
}

char* itostr(int num, char* str) { 
	//K&R itoa
    int i, sign;
    
	if ((sign = num) < 0)
        num = -num; 
	i = 0;
    do { 
        str[i++] = num % 10 + '0'; 
    } while ((num /= 10) != 0);
    if (sign) 
        str[i++] = '-'; 
    str[i] = '\0';
    reverse(str); 
  
    return str; 
}

//takes in:
//	char* number a in the form '11.22222e1234'
//	char* number b in the form '11.22222e1234' (optional)
//	bf_op_type_t operator
//	uint32_t decimal digits precision
//	int rounding mode
//returns:
//	char* in the form '11.22222e1234'
char* bf_sop (
			const char* a,
			const char* b,
			bf_op_type_t op,
			uint32_t precisiondigits,
			int	rnd_mode
			) {

    bf_t A, B, R, S;
    int32_t prec;
	int32_t status;
    char *digits;

	//prec = (limb_t) int(precisiondigits * BITS_PER_DIGIT) + 32;
	prec = (limb_t) (precisiondigits * 4 + 32);
    bf_init(&bf_ctx, &A);
    bf_init(&bf_ctx, &B);
    bf_init(&bf_ctx, &R);

	bf_atof (&A, a, NULL, 10, prec, rnd_mode);
	bf_atof (&B, b, NULL, 10, prec, rnd_mode);

	status = 0;
	switch (op) {
		case BF_OP_MUL:
			status = bf_mul (&R, &A, &B, prec, rnd_mode);
			break;
		case BF_OP_ADD:
			status = bf_add (&R, &A, &B, prec, rnd_mode);
			break;
		case BF_OP_SUB:
			status = bf_sub (&R, &A, &B, prec, rnd_mode);
			break;
		case BF_OP_DIV:
			status = bf_div (&R, &A, &B, prec, rnd_mode);
			break;
		case BF_OP_REM:
			status = bf_remainder (&R, &A, &B, prec, rnd_mode);
			break;
		case BF_OP_IDIV:
			//takes an extra pointer &S for remainder that we don't use
			bf_init(&bf_ctx, &S);
			status = bf_divrem (&R, &S, &A, &B, prec, rnd_mode, rnd_mode);
			bf_delete(&S);
			break;
		case BF_OP_SIN:
			status = bf_sin (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_COS:
			status = bf_cos (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_TAN:
			status = bf_tan (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_ASIN:
			status = bf_asin (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_ACOS:
			status = bf_acos (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_ATAN:
			status = bf_atan (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_ATAN2:
			status = bf_atan2 (&R, &A, &B, prec, rnd_mode);
		case BF_OP_EXP:
			status = bf_exp (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_LOG:
			status = bf_log (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_SQRT:
			status = bf_sqrt (&R, &A, prec, rnd_mode);
			break;
		case BF_OP_RINT:
			//convert to int
			bf_move (&R, &A);
			status = bf_rint (&R, prec, rnd_mode);
			break;
		case BF_OP_ROUND:
			//round
			bf_move (&R, &A);
			status = bf_round (&R, prec, rnd_mode);
			break;
		case BF_OP_EQ:
			status = bf_cmp_eq (&A, &B);
			bf_set_float64 (&R, (double) status);
			break;
		case BF_OP_LT:
			status = bf_cmp_lt (&A, &B);
			bf_set_float64 (&R, (double) status);
			break;
		case BF_OP_LE:
			status = bf_cmp_le (&A, &B);
			bf_set_float64 (&R, (double) status);
			break;
		case BF_OP_PI:
			//get pi into R and then multiply by A
			bf_const_pi (&R, prec, rnd_mode);
			status = bf_mul (&R, &A, &R, prec, rnd_mode);
			break;
		default:
			status = -1;
			break;
	}

	bf_ftoa(&digits, &R, 10, precisiondigits + 1,
                             BF_FTOA_FORMAT_FIXED | rnd_mode);
	
    bf_delete(&A);
    bf_delete(&B);
    bf_delete(&R);

	char bf_status_string[10];
	return strcat(strcat(digits, "s"), itostr(status, bf_status_string));
}

