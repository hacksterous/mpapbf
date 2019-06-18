## Minimalistic Python Arbitrary Precision Math Using LibBF
MPBF is a MicroPython wrapper around [LibBF](https://bellard.org/libbf/).
Works for Unix and STM32 ports, but might also work for ESP32.

### File Description


| File  | Description 
| ------------- | ------------- 
| libbf.c  | C source for BF core functions 
| libbf.h | BF core header.  
|cutils.c | BF utilities.    
|cutils.h | BF utilities header.
|bf.c | C wrapper for libbf. This provides a set of functions that are called by the functions in mpbf.c   
|bf.h | Header for C wrapper.                             
|mpbf.c| MicroPython external C module for libbf. There are 3 functions that are exposed to Python.
|mpapbf.py | Wrapper MicroPython module. Optional.
|micropython.mk| C module makfile.                       
|test.c | Simple C test.
|Makefile.mpbf| Example Makefile for running a simple test on Unix (test.c) 

### Compilation
1. Copy the contents of directory mpbf/ to $MP/ports/stm32/ or $MP/ports/unix/

2. Compile command for Unix:
```
   $ cd $MP/ports/unix/
   $ make V=1 USER_C_MODULES=. CFLAGS_EXTRA="-DMODULE_MPBF_ENABLED=1"
```  
3. Compile command for stm32 (F407VE board):
```
   $ cd $MP/ports/stm32/
   $ make BOARD=BLACK_F407VE USER_C_MODULES=. CFLAGS_EXTRA="-DMODULE_MPBF_ENABLED=1 -DBARE_M=1"
```   
### MPBF Usage

All operations are done on decimal numbers represented as strings, e.g.:
`'2.718281828e1'` is 27.18281828.

```
   $ micropython
   MicroPython v1.11-44-g8b18cfede-dirty on 2019-06-14; linux version
   Use Ctrl-D to exit, Ctrl-E for paste mode
   >>> from mpbf import *
   >>> mpbf.init()
   >>> mpbf.set_params(500, 0)  # precision digits, rounding mode
   >>> mpbf.sop('1', '0', 5)    # 5 is exponentiation operation -- see bf.h
   '2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320
   0305992181741359662904357290033429526059563073813232862794349076323382988075319525101901157383418793070215408914993
   4884167509244761460668082264800168477411853742345442437107539077744992069551702761838606261331384583000752044933826
   5602976067371132007093287091274437470472306969772093101416928368190255151086574637721112523897844250569536967707854
   4996996794686445490598793163688923009879313s-16'
   >>> mpbf.set_params(5, 0)
   >>> mpbf.sop('1', '0', 5)
   '2.71828s-16'
   >>> mpbf.finish() #deallocate memory
```
The returned string always ends with `s<a signed number>` -- this indicates the status returned by libbf and in most cases
can be discarded.

### Functions implemented
|Function| Operator value Passed to sop ()|
|------------|-----------------------------|
| BF_OP_ADD  | 0
| BF_OP_MUL  | 1
| BF_OP_SUB  | 2
| BF_OP_DIV  | 3
| BF_OP_POW  | 4
| BF_OP_EXP  | 5
| BF_OP_LOG  | 6
| BF_OP_SIN  | 7
| BF_OP_COS  | 8
| BF_OP_TAN  | 9
| BF_OP_ATAN | 10
| BF_OP_ATAN2| 11
| BF_OP_ACOS | 12
| BF_OP_ASIN | 13
| BF_OP_SQRT | 14
| BF_OP_IDIV | 15
| BF_OP_REM  | 16
| BF_OP_RINT | 17
| BF_OP_ROUND| 18
| BF_OP_EQ   | 19
| BF_OP_LT   | 20
| BF_OP_LE   | 21
| BF_OP_PI   | 22


### MPAPBF usage
The number format is defined in [MPAP](https://github.com/hacksterous/mpap). It's not necessary
to use MPAP for availing arbitrary precision functions provided by MPBF/libbf, but it helps as a numerical
representation of floating point numbers instead of strings.

Keep mpapbf.py in a directory listed in a standard sys.path.
```   
   $ micropython
   MicroPython v1.11-44-g8b18cfede-dirty on 2019-06-14; linux version
   Use Ctrl-D to exit, Ctrl-E for paste mode
   >>> from mpapbf import *
   >>> mpap(1).exp()
   mpap(Mantissa = 27182818284590452353602874714, Exponent = 0, InternalAware = True)
   >>> sprec(500) #set precision to 500
   >>> mpap(1).exp()
   mpap(Mantissa = 2718281828459045235360287471352662497757247093699959574966967627724076630353547594571382178525166427427466    
   3919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190115738341879
   3070215408914993488416750924476146066808226480016847741185374234544243710753907774499206955170276183860626
   1331384583000752044933826560297606737113200709328709127443747047230696977209310141692836819025515108657463
   77211125238978442505695369677078544996996794686445490598793163688923009879313, Exponent = 0, InternalAware = True)
   >>> rprec() #reset precision back to default 27
   >>> mpap(1).exp()
   mpap(Mantissa = 27182818284590452353602874714, Exponent = 0, InternalAware = True)
```   
### Functions supported in MPAPBF

|MPBF Function | Python operator or function |
|------------|-----------------------------|
| BF_OP_ADD  | +
| BF_OP_MUL  | *
| BF_OP_SUB  | -
| BF_OP_DIV  | /
| BF_OP_POW  | **
| BF_OP_EXP  | `mpap(value).exp()`
| BF_OP_LOG  | `mpap(value).log()`
| BF_OP_SIN  | `mpap(value).sin()`
| BF_OP_COS  | `mpap(value).cos()`
| BF_OP_TAN  | `mpap(value).tan()`
| BF_OP_ATAN | `mpap(value).atan()`
| BF_OP_ATAN2| `mpap(value).atan2()`
| BF_OP_ACOS | `mpap(value).acos()`
| BF_OP_ASIN | `mpap(value).asin()`
| BF_OP_SQRT | `mpap(value).sqrt()`
| BF_OP_IDIV | //
| BF_OP_REM  | %
| BF_OP_RINT | *Not implemented*
| BF_OP_ROUND| *Not implemented*
| BF_OP_EQ   | ==
| BF_OP_LT   | <
| BF_OP_LE   | <=
| BF_OP_PI   | `mpap(value).pi()`. Returns *value\*pi*

## Known Issues

1. The factorization `factors()` function in `mpapbf.py` has a bug.

   
