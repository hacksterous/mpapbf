#########################################################
# mpap
# Minimalistic Python port of Arbitrary Precision Arithmetic using BF
# Based on MPAP
# https://bellard.org/libbf/
# Targeted for MicroPython on microcontrollers
# (c) 2019 Anirban Banerjee <anirbax@gmail.com>
#########################################################
MPBF_DEGREES_MODE = False
MAX_PRECISION_HARD_LIMIT = 190
ROUNDING_MODE = 0
PRECISION = 27 
import mpbf
import gc

mpbf.init ()
mpbf.set_params (PRECISION, ROUNDING_MODE)

def finish ():
    mpbf.finish()

def rprec():
    global ROUNDING_MODE
    global PRECISION
    PRECISION = 27
    mpbf.set_params (PRECISION, ROUNDING_MODE)

def sprec(prec):
    global ROUNDING_MODE
    global PRECISION
    global MAX_PRECISION_HARD_LIMIT
    PRECISION = min(prec, MAX_PRECISION_HARD_LIMIT)
    mpbf.set_params (PRECISION, ROUNDING_MODE)

class mpap ():
    # Internal Representation of significant digits + sign.
    Mantissa = None

    # Internal Representation of (Integer) Exponent of 10,
    # e.g. 6.283012 = [Mantissa = 6283012, Exponent = 6]
    #      0.097215 = [Mantissa = 97215  , Exponent = -2]
    # This exponent IS the scientific notation exponent.
    # Contrary to intuition, Mantissa * 10eExponent is NOT this number it
    # To reconstruct this number, take the first number and insert "." divider in 0-1 pos
    # e.g. 9.7215e-2, this is the actual number.
    # This is implied in later calculations, beware!
    Exponent = 0

    # __init__
    # Initialization Function
    # If a non-integer float type is passed to Mantissa, then this number will be converted
    # to our internal representation.
    #
    # (!!) IF YOU PASS A INTEGER TO mantissa there are two possible behaviors.
    # Your int may be interpreted
    # as a literal integer (InternalAware = False) or interpreted as internal representation of significant
    # digits, so 142857 = 1.42857x10^0 = 1.42857.
    # By default, we assume you are NOT aware of the Internal structures. This keeps consistency with float support
    # for mantissa.

    # Set InternalAware = True to interpret as internal representation.

    def __init__(self, Mantissa, Exponent = 0, InternalAware = False):

        if(isinstance(Mantissa, mpap)):
            self.Mantissa = Mantissa.Mantissa
            self.Exponent = Mantissa.Exponent
            return

        #if True:
        try:
            #catch inf in Mantissa and illegal format in Exponent
            if type(Mantissa) == float:
                if str(float(Mantissa)) == 'inf' or str(float(Mantissa)) == '-inf' or \
                    str(float(Mantissa)) == 'nan' or str(float(Exponent)) == 'nan' or \
                    str(float(Exponent)) == 'inf' or str(float(Exponent)) == '-inf':
                    raise OverflowError
            Exponent = int(Exponent)
            #pass
        except (ValueError, OverflowError):
            self.Mantissa = None
            self.Exponent = 0
            return

        if (type(Mantissa) == float or type(Mantissa) == str):
            # String rep of mantissa, useful for reuse (strings are immutable), also UnSigned variant
            strMan = str(Mantissa)
            strManUS = strMan.replace('-', '')
            if strManUS.lower() == 'nan' or strManUS.lower() == 'inf':
                self.Mantissa = None
                self.Exponent = 0
                return 
            elif strManUS.lower() == 'none' or strManUS == '':
                #no mathematical result
                self.Mantissa = None
                self.Exponent = None
                return 
            # Extract all significant digits
            if('e' in strMan): # Oops, too small; have to expand notation
                # Something like 1e-07... significant digits are before e, then 
                # extract the second part and add it to exponent accumulator
                strManParts = strMan.split('e')
                try:
                    self.Mantissa = int(strManParts[0].replace('.', ''))
                    Exponent += int(strManParts[1])
                except (ValueError, OverflowError):
                    self.Mantissa = None
                    self.Exponent = 0
                    return
            else:
                self.Mantissa = int(strMan.replace('.', ''))

            # Count exponent for scientific notation
            isFraction = (strManUS.find('.') > -1 and int(strManUS[:strManUS.find('.')]) == 0)
            #if (abs(float(Mantissa)) < 1) or isFraction == True:
            if isFraction == True:
                # numbers that cause single/double-precision float() to overflow
                # will fail this if-clause
                if self.Mantissa == 0:
                    #number is 0, .0, 0.0, 0. etc
                    self.Mantissa = 0
                    self.Exponent = 0
                    Exponent = 0
                else:
                    #number is a fraction
                    for i in range(len(strManUS)):
                        if(strManUS[i] == '.'):
                            continue
                        if(strManUS[i] != '0'):
                            break
                        Exponent = Exponent - 1
            else:
                Exponent = Exponent - 1 # 1.42857 is 1.425847e0
                for i in range(len(strManUS)):
                    if(strManUS[i] == 'e' or  strManUS[i] == '.'):
                        break
                    Exponent = Exponent + 1

            self.Exponent = Exponent

        else:
            #handle integer parameters only
            if(Mantissa == 0):
                self.Mantissa = 0
                self.Exponent = 0
            else:
                self.Mantissa = Mantissa
                #print ("InternalAware is ", InternalAware)
                if(InternalAware):
                    self.Exponent = Exponent
                else:
                    self.Exponent = Exponent + len(str(Mantissa).replace('-', '')) - 1
            
        #endif

        #M=10, E=1 and M=1, E=1 both indicate the same number,
        #however, the different values of mantissa will be a problem
        #in numeric comparisons, so reduce to the form M=1, E=1
        MantissaStr = str(self.Mantissa)
        i = 0
        while MantissaStr[-1:] == '0' and \
                self.Mantissa != 0:
            MantissaStr = MantissaStr[:-1]
            i += 1
        self.Mantissa = int (MantissaStr)

        #print ("__init__: self.Mantissa is ", self.Mantissa)
        return
    #enddef init

    def bfwrapper1 (self, op):
        #print ("bfwrapper1: calling SOP with op=", op)
        gc.collect()
        #print ("bfwrapper1: self is ", self.scistr())
        s = mpbf.sop(self.scistr(), '', op)
        #print ("bfwrapper1: returned result ", s)
        s = s.split('s')[0]
        return mpap(s)

    def bfwrapper2 (self, other, op):
        #print ("bfwrapper2: calling SOP with op=", op)
        #print ("bfwrapper2: other is ", other)
        #print ("bfwrapper2: other.scistr is ", oss)

        gc.collect()
        s = mpbf.sop(self.scistr(), other.scistr(), op)
        s = s.split('s')[0]
        return mpap(s)

    def __truediv__ (self, other):
        if(not isinstance(other, mpap)):
            return self / mpap(other)

        if other == 0:
            return mpap('NaN')

        #subtract divisor's exponent from dividend's exponent after adjusting
        #for the InternalAware representaiton
        re = self.Exponent - (len(str(self.Mantissa).replace('-', '')) - 1)
        re -= other.Exponent - (len(str(other.Mantissa).replace('-', '')) - 1)

        #do division of the mantissa integers with the set precision
        rm = mpap(self.Mantissa).bfwrapper2(mpap(other.Mantissa), 3)
        #then adjust the exponent calculated earlier
        rm = mpap(Mantissa = str(rm), Exponent = re, InternalAware = True)
        return rm

    def isInt(self):
        # 123456 --> (123456, 5)
        return len(str(self.Mantissa).replace('-', '')) <= self.Exponent + 1

    def isNaNInf (self):
        return self.Mantissa == None and self.Exponent == 0

    def isNone (self):
        return self.Mantissa == None or self.Exponent == None

    def int(self, preserveType = True):
        # 123456 (123456, 5)
        s = str(self.Mantissa).replace('-', '')
        if self.Exponent < 0:
            s = '0'
        else:
            lenS =len(s)
            #fill up with requisite number of 0s on the right
            s = s + '0'*(self.Exponent + 1 - lenS)
            #take as many required by the Exponent (add 1 more
            #since canonical form is always #.##....e###
            s = s[0:(self.Exponent + 1)]

        if preserveType == True:
            #convert to an integer, but return the mpap() version
            return mpap(s) * self.sgn()
        else:
            return int(s) * self.sgn()

    def __int__ (self):
        return self.int(preserveType = False)

    def float (self):
        s = str(self.Mantissa)
        return float(('-' if self.sgn() == -1 else '') + s[0:1] + '.' + s[1:] + 'e' + str(self.Exponent))

    def __repr__(self):
        return "mpap(Mantissa = " + str(self.Mantissa) + ", Exponent = " + str(self.Exponent) + ", InternalAware = True)"

    def __str__(self, decimalplaces=6):
        if self.isInt():
            return str(int(self))
        elif len(str(self.Mantissa)) - 1 > self.Exponent and self.Exponent >= 0:
            #do not return as 1.23e45
            strAbsSelfMantissa = str(abs(self.Mantissa))
            decPoint = self.Exponent + 1
            return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa[:decPoint] + '.' + strAbsSelfMantissa[decPoint:]
        else:
            # fractional number
            strAbsSelfMantissa = str(abs(self.Mantissa))
            if abs(self.Exponent) >= decimalplaces:
                frac = strAbsSelfMantissa[1:]
                # mpap(1, -3) is 1.0e-3 and not 1.e-3
                if frac == '':
                    frac = '0'
                strAbsSelfMantissa = strAbsSelfMantissa[0] + '.' + frac
                return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa + "e" + str(self.Exponent)
            else:
                strAbsSelfMantissa = ('-0.' if self.Mantissa < 0 else '0.') + '0'*(abs(self.Exponent) - 1) + strAbsSelfMantissa
                #print ("strAbsSelfMantissa is ", strAbsSelfMantissa)
                return strAbsSelfMantissa

    # return number in the form of
    # Mantissa = ###.#######, Exponent = ###*3
    # returns new mantissa as a string with adecimal point
    # and the exponent as an integer
    def sci(self):
        #print ("sci: self is ", repr(self))
        man = str(self.Mantissa)
        expo = self.Exponent
        strMantissa = str(man).replace('-', '')
        lenStrMantissa = len(strMantissa)
        if self.Exponent <= 0:
            # we increase the exponent value to the nearest negative
            # upper multiple and compensate by adding more 0s to the
            #mantissa string
            if self.Exponent % 3 != 0:
                multfac = (3-abs(self.Exponent)%3)
                #print ("1. multfac is ", multfac)
                expo = self.Exponent - multfac
                if  lenStrMantissa < multfac + 1:
                    strMantissa +=  '0'*(multfac+1-lenStrMantissa)
            else:
                multfac = 0
            man = ('-' if (self.sgn() == -1) else '') + strMantissa[:multfac+1] + '.' + strMantissa[multfac+1:]

        else:
            diff = self.Exponent - lenStrMantissa + 1 
            if diff < 0:
                diff += 3 # 3 additional places
            strMantissa = strMantissa + '0'*diff
            expo = self.Exponent
            multfac = self.Exponent % 3 + 1
            #print ("2. multfac is ", multfac)
            expo = (expo// 3) * 3
            man = ('-' if (self.sgn() == -1) else '') + strMantissa[:multfac] + '.' + strMantissa[multfac:]
        # handle the case when mantissa string is like '123.' -- add a zero at end
        if man[-1:] == '.':
            man += '0'
        elif man.find('.') == -1:
            man += '.0'
        #print ("sci: man is ", man)
        #print ("sci: expo is ", expo)
        return man, expo

    # similar to sci(), but returns a single string as ###.#######e###
    def scistr(self):
        m, e = self.sci()
        return m + 'e' + str(e)

    def floor(self):
        i = self.int(preserveType = True)
        return i if self.sgn() >= 0 else i-1

    def ceil(self):
        return self.floor() + 1

    def frac(self):
        return self - self.floor()

    def __neg__(self):
        return mpap(Mantissa = (-1) * self.Mantissa, Exponent = self.Exponent, InternalAware = True)

    def round (self, digits):
        #rounds UP so many digits AFTER decimal
        #print ("round: self is ", self)
        if digits < 0:
            return self
        r = self + mpap(Mantissa = 5, Exponent = -(digits + 1))
        #print ("round: r is ", r)
        return r

    def roundstr (self, digits):
        #print ("roundstr: self is ", self)
        v = str(self.round(digits)).split('.')
        if len (v) > 1 and digits > 0:
            return v[0] + '.' + v[1][:digits]
        else:
            return v[0]

    def __floordiv__ (self, other):
        if(not isinstance(other, mpap)):
            return self // mpap(other)
        #for negative numbers, round downwards, not towards 0
        res = (self / other).floor()
        return res

    def __mod__ (self, other):
        if(not isinstance(other, mpap)):
            return self % mpap(other)
        s = self.bfwrapper2(other, 16)
        #modulo result has same sign as divisor
        if other.sgn() == 1:
            if s < 0:
                s += other 
        elif other.sgn() == -1:
            if s > 0:
                s += other 

        return s

    def __abs__(self):
        if(self.sgn() == 1):
            return self
        else:
            return -self

    def __eq__(self, other):
        if(not isinstance(other, mpap)):
            return self == mpap(other)
        return self.Mantissa == other.Mantissa and self.Exponent == other.Exponent

    def __hash__(self):
        return hash((self.Mantissa, self.Exponent))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if(not isinstance(other, mpap)):
            return self < mpap(other)
        return True if self.bfwrapper2(other, 20) == 1 else False

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self < other and not self == other

    def __ge__(self, other):
        return not self < other

    def __add__(self, other):
        if(not isinstance(other, mpap)):
            return self + mpap(other)
        return self.bfwrapper2(other, 0)

    def __sub__(self, other):
        if(not isinstance(other, mpap)):
            return self - mpap(other)
        #return self + (-other)
        return self.bfwrapper2(other, 2)

    def __mul__(self, other):
        if(not isinstance(other, mpap)):
            return self * mpap(other)
        return self.bfwrapper2(other, 1)

    def __lshift__ (self, other):
        if(not isinstance(other, mpap)):
            return self << mpap(other)
        return self * mpap(2) ** other

    def __rshift__ (self, other):
        if(not isinstance(other, mpap)):
            return self >> mpap(other)
        return self // mpap(2) ** other

    def __xor__ (self, other):
        if(not isinstance(other, mpap)):
            return self ^ mpap(other)
        return mpap(int(self) ^ int(other))

    def __or__ (self, other):
        if(not isinstance(other, mpap)):
            return self | mpap(other)
        return mpap(int(self) | int(other))

    def __and__ (self, other):
        if(not isinstance(other, mpap)):
            return self & mpap(other)
        return mpap(int(self) & int(other))

    def __invert__ (self):
        return mpap(~int(self))

    def __not__ (self):
        return mpap(1 if self == 0 else 0)

    def __pow__(self, other):
        if(not isinstance(other, mpap)):
            return self ** mpap(other)
        if (self.sgn() == -1 and other.Exponent < 0):
            return mpap ('NaN')
        return self.bfwrapper2(other, 4)

    def sgn(self):
        return (1 if self.Mantissa > 0 else (0 if self.Mantissa == 0 else -1))

    def ln (self):
        return log(self)

    def log10 (self):
        return self.log()/(mpap(10).log())

    def log (self):
        ## See https://stackoverflow.com/questions/27179674/examples-of-log-algorithm-using-arbitrary-precision-maths
        if (self <= 0):
            return mpap ('NaN')
        if (self == 1):
            return mpap(0)
        #t = utime.ticks_ms()
        #r = self.bfwrapper1(6)
        #print ("Time taken for log:", utime.ticks_diff(utime.ticks_ms(), t))
        return self.bfwrapper1(6)

    def pi(self):
        return self.bfwrapper1(22)

    def sqrt (self):
        return self.bfwrapper1(14)

    def exp (self):
        return self.bfwrapper1(5)

    def digits(self):
        return mpap(len(str(int(self))))

    def bits(self):
        return mpap(self.log()/mpap(2).log()).ceil()

    def tan (self):
        if MPBF_DEGREES_MODE == True:
            d2r = mpap('3.1415926535897932384626433832795') / 180
            return (self * d2r).bfwrapper1(9)
        else:
            return self.bfwrapper1(9)

    def sin (self):
        if MPBF_DEGREES_MODE == True:
            d2r = mpap('3.1415926535897932384626433832795') / 180
            return (self * d2r).bfwrapper1(7)
        else:
            return self.bfwrapper1(7)

    def cos (self):
        if MPBF_DEGREES_MODE == True:
            d2r = mpap('3.1415926535897932384626433832795') / 180
            return (self * d2r).bfwrapper1(8)
        else:
            return self.bfwrapper1(8)

    def acos (self):
        if MPBF_DEGREES_MODE == True:
            r2d = mpap(180) / mpap('3.1415926535897932384626433832795')
            return self.bfwrapper1(12) * r2d
        else:
            return self.bfwrapper1(12)

    def asin (self):
        if MPBF_DEGREES_MODE == True:
            r2d = mpap(180) / mpap('3.1415926535897932384626433832795')
            return self.bfwrapper1(13) * r2d
        else:
            return self.bfwrapper1(13)

    def atan (self):
        if MPBF_DEGREES_MODE == True:
            r2d = mpap(180) / mpap('3.1415926535897932384626433832795')
            return self.bfwrapper1(10) * r2d
        else:
            return self.bfwrapper1(10)

    def atan2 (self, other):
        #print ("atan2: self is ", self)
        if MPBF_DEGREES_MODE == True:
            r2d = mpap(180) / mpap('3.1415926535897932384626433832795')
            return self.bfwrapper1(11) * r2d
        else:
            return self.bfwrapper2(mpap(other), 11)

    def asinh (self):
        return (self + (self*self + 1).sqrt()).log()

    def acosh (self):
        if (self < 1):
            return mpap ('NaN')
        elif self == 1:
            return mpap(0)
        else:
            return (self + (self*self - 1).sqrt()).log()
        
    def atanh (self):
        if (self < 1):
            return mpap ('NaN')
        elif self == 1:
            return mpap(0)
        else:
            return ((self + 1) / (self - 1)).log() / 2

    def sinh (self):
        return (self.exp() - (-self).exp()) / 2

    def cosh (self):
        return (self.exp() + (-self).exp()) / 2

    def tanh (self):
        return ((self * 2).exp() - 1)/((self * 2).exp() + 1)
