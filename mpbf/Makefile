# Tiny arbitrary precision floating point library
# 
# Copyright (c) 2017-2018 Fabrice Bellard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Enable Windows compilation
#CONFIG_WIN32=y
# build AVX2 version
# Enable profiling with gprof
#CONFIG_PROFILE=y
# Enable the MPFR library to do tests and benchmarks

ifdef CONFIG_WIN32
CROSS_PREFIX=x86_64-w64-mingw32-
EXE:=.exe
else
EXE:=
endif

CC=$(CROSS_PREFIX)gcc
CFLAGS=-Wall -g $(PROFILE) -MMD
CFLAGS+=-O2
CFLAGS+=-flto
#CFLAGS+=-Os
LDFLAGS=
#CFLAGS+=-m32
#LDFLAGS+=-m32
LIBS=-lm

PROGS=test$(EXE)

all: $(PROGS)

test$(EXE): test.o bf.o libbf.o cutils.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(PROGS) *.o *.d *~

-include $(wildcard *.d)
