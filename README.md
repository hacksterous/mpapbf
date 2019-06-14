## Minimalistic Python with Arbitrary Precision using LibBF
MPBF is a MicroPython wrapper around [libbf](https://bellard.org/libbf/).
Works for Unix and STM32 ports, but might also work for ESP32.

### File Description

```
libbf.c: BF core functions.
libbf.h: BF core header.
cutils.c: BF utilities.    
cutils.h: BF utilities header.
bf.c: C wrapper for libbf. This provides a set of functions that are called by the functions in mpbf.c   
bf.h: Header for C wrapper.                             
mpbf.c: MicroPython wrapper for BF. These are 3 functions that are exposed to Python.
mpapbf.py: MicroPython module. Optional.
micropython.mk: C module makfile.                       
test.c: Simple C test.
Makefile.mpbf: Example Makefile for running a simple test on Unix (test.c)                
```

### Compilation
1. Copy the contents of directory mpbf/ to $MP/ports/stm32/ or $MP/ports/unix/

2. Compile command for Unix:
```
   $ cd $MP/ports/unix/
   $ make V=1 USER_C_MODULES=. CFLAGS_EXTRA="-DMODULE_MPBF_ENABLED=1"
```  
3. Compile command for stm32:
```
   $ cd $MP/ports/stm32/
   $ make CROSS_COMPILE=arm-linux- V=1 USER_C_MODULES=. CFLAGS_EXTRA="-DMODULE_MPBF_ENABLED=1 -DBARE_M=1"
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
```
The returned string always ends with `s<a signed number>` -- this indicates the status returned by libbf and in most cases
can be discarded.

### MPAP usage
The number format is defined in [MPAP] (https://github.com/hacksterous/mpap). It's not necessary
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
```   
## Known Issues

1. Precision cannot be dynamically set in MPAP because of a bug in `mpapbf.py` and the `set_params()` function in mpbf.c

   
