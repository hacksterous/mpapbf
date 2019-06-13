//anirb

#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <math.h>
#include <string.h>

#include "bf.h"

/* number of bits per base 10 digit */
#define BITS_PER_DIGIT 3.32192809488736234786

int main(int argc, char **argv) {

	char *val = realloc(NULL, 20000);
	bf_initialize ();
	val = bf_sop("-1.23e20", "3.1415926535897932384626433832795028841971693", BF_OP_MUL, 50, 0);
	printf ("val is %s\n", val);

	char * a = "1.0e200";
	val = bf_sop(a, "", BF_OP_LOG, 50, 0);
	printf ("log %s is %s\n", a, val);
	char * b = "3.1415926535897932384626433832795028841971693993751058";
	val = bf_sop(b, "", BF_OP_LOG, 50, 0);
	printf ("log %s is %s\n", b, val);
	free(val);
	return 0;
}
