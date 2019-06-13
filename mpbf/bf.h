typedef enum {
	BF_OP_ADD,    //0
	BF_OP_MUL,    //1
	BF_OP_SUB,    //2
	BF_OP_DIV,    //3
	BF_OP_POW,    //4
	BF_OP_EXP,    //5
	BF_OP_LOG,    //6
	BF_OP_SIN,    //7
	BF_OP_COS,    //8
	BF_OP_TAN,    //9
	BF_OP_ATAN,   //10
	BF_OP_ATAN2,  //11
	BF_OP_ACOS,   //12
	BF_OP_ASIN,   //13
	BF_OP_SQRT,   //14
	BF_OP_IDIV,   //15
	BF_OP_REM,    //16
	BF_OP_RINT,   //17
	BF_OP_ROUND,  //18
	BF_OP_EQ,	  //19
	BF_OP_LT,	  //20
	BF_OP_LE,	  //21
	BF_OP_PI,	  //22
	} bf_op_type_t; 
                    
extern void bf_initialize (void);
extern void bf_exit (void);

extern char* bf_sop (
			const char* a,
			const char* b,
			bf_op_type_t op,
			uint32_t precisiondigits,
			int	rnd_mode
			);

