#########################################################
# mpap
# Minimalistic Python port of Arbitrary Precision Arithmetic using BF
# Based on MPAP
# https://bellard.org/libbf/
# Targeted for MicroPython on microcontrollers
# (c) 2019 Anirban Banerjee <anirbax@gmail.com>
#########################################################
MPAPERRORFLAG = ''
MAX_PRECISION_HARD_LIMIT = 1000
ROUNDING_MODE = 0
PRECISION = 27 
BIGGESTNUM = 1
import mpbf

mpbf.init ()
mpbf.set_params (PRECISION, ROUNDING_MODE)

def finish ():
    mpbf.finish()

def rprec():
    global ROUNDING_MODE
    global PRECISION
    global BIGGESTNUM
    BIGGESTNUM = 1
    PRECISION = 27
    mpbf.set_params (PRECISION, ROUNDING_MODE)

def sprec(prec):
    global ROUNDING_MODE
    global PRECISION
    PRECISION = prec
    mpbf.set_params (PRECISION, ROUNDING_MODE)

class mpap ():
    PIx2 = '6.283185307179586476925286766559005768394338798750211641949889184615632812572417997256069650684234135988'

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

    #True is positive, False is negative
    Sign = 1

    ImagMantissa = 0 
    ImagExponent = 0
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

    def __init__(self, Mantissa, Exponent = 0, InternalAware = False, \
        ImagMantissa = 0, ImagExponent = 0):

        global MAX_PRECISION_HARD_LIMIT
        global PRECISION
        global BIGGESTNUM
        global MPAPERRORFLAG
        global ROUNDING_MODE

        if(isinstance(Mantissa, mpap)):
            self.Mantissa = Mantissa.Mantissa
            self.Exponent = Mantissa.Exponent
            return

        try:
            #catch inf in Mantissa and illegal format in Exponent
            if type(Mantissa) == float:
                if str(float(Mantissa)) == 'inf' or str(float(Mantissa)) == '-inf' or \
                    str(float(Exponent)) == 'inf' or str(float(Exponent)) == '-inf':
                    raise OverflowError
            Exponent = int(Exponent)
        except (ValueError, OverflowError):
            self.Mantissa = 0
            self.Exponent = 0
            MPAPERRORFLAG = "Illegal mantissa or exponent. \nHint: use strings to hold large numbers!"
            return

        if (type(Mantissa) == float or type(Mantissa) == str):
            # String rep of mantissa, useful for reuse (strings are immutable), also UnSigned variant
            strMan = str(Mantissa)
            strManUS = strMan.replace('-', '')
            # Extract all significant digits
            if('e' in strMan): # Oops, too small; have to expand notation
                # Something like 1e-07... significant digits are before e, then 
                # extract the second part and add it to exponent accumulator
                strManParts = strMan.split('e')
                try:
                    self.Mantissa = int(strManParts[0].replace('.', ''))
                    Exponent += int(strManParts[1])
                except (ValueError, OverflowError):
                    self.Mantissa = 0
                    self.Exponent = 0
                    MPAPERRORFLAG = "Illegal mantissa or exponent."
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

        #For numbers with large exponents, grow the precision
        PRECISION = max(PRECISION, (len(str(self.Mantissa).replace('-', '')) + self.Exponent))
        BIGGESTNUM = max(BIGGESTNUM, self.Exponent+1)
        #but don't let the precision grow beyond the max. precision value of 
        BIGGESTNUM = min(BIGGESTNUM, MAX_PRECISION_HARD_LIMIT)
        #print ("BIGGESTNUM is ", BIGGESTNUM)
        PRECISION = max(PRECISION, BIGGESTNUM)
        #print ("auto-setting mpbf precision to: ", PRECISION)
        mpbf.set_params (PRECISION, ROUNDING_MODE)

        #zero value has sign 0
        self.Sign = (1 if self.Mantissa > 0 else (0 if self.Mantissa == 0 and self.Exponent == 0 else -1))
        return
    #enddef init

    def bfwrapper1 (self, op):
        return mpap(mpbf.sop (self.scistr(), '', op).split('s')[0])

    def bfwrapper2 (self, other, op):
        #print ("bfwrapper2: self", repr(self))
        #print ("bfwrapper2: other", repr(other))
        return mpap(mpbf.sop (self.scistr(), other.scistr(), op).split('s')[0])

    def __truediv__ (self, other):
        global MPAPERRORFLAG
        if(not isinstance(other, mpap)):
            return self / mpap(other)

        if other == 0:
            MPAPERRORFLAG = "Division by zero."
            return mpap(0)

        #integer dividend
        if self == int(self):
            m = int(self)/other.Mantissa
            return mpap(Mantissa = m, Exponent = -other.Exponent)
        
        #subtract divisor's exponent from dividend's exponent after adjusting
        #for the InternalAware representaiton
        re = self.Exponent - (len(str(self.Mantissa).replace('-', '')) - 1)
        re -= other.Exponent - (len(str(other.Mantissa).replace('-', '')) - 1)

        #print ("re is ", re)
        #print ("self.Mantissa is ", self.Mantissa)
        #print ("other.Mantissa is ", other.Mantissa)

        rm = mpap(self.Mantissa).bfwrapper2(mpap(other.Mantissa), 3)
        #print ("rm is ", repr(rm))
        rm = mpap(Mantissa = str(rm), Exponent = re, InternalAware = False)
        #print ("rm is ", repr(rm))
        return rm

    def isInt(self):
        # 123456 --> (123456, 5)
        return len(str(self.Mantissa).replace('-', '')) <= self.Exponent + 1

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
            return mpap(s) * self.Sign
        else:
            return int(s) * self.Sign

    def __int__ (self):
        return self.int(preserveType = False)

    def float (self):
        s = str(self.Mantissa)
        return float(('-' if self.Sign == -1 else '') + s[0:1] + '.' + s[1:] + 'e' + str(self.Exponent))

    def __repr__(self):
        return "mpap(Mantissa = " + str(self.Mantissa) + ", Exponent = " + str(self.Exponent) + ", InternalAware = True)"

    def __str__(self):
        if self.isInt():
            return str(int(self))
        elif len(str(self.Mantissa)) - 1 > self.Exponent and self.Exponent >= 0:
            #do not return as 1.23e45
            strAbsSelfMantissa = str(abs(self.Mantissa))
            decPoint = self.Exponent + 1
            return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa[:decPoint] + '.' + strAbsSelfMantissa[decPoint:]
        else:
            strAbsSelfMantissa = str(abs(self.Mantissa))
            frac = strAbsSelfMantissa[1:]
            # mpap(1, -3) is 1.0e-3 and not 1.e-3
            if frac == '':
                frac = '0'
            strAbsSelfMantissa = strAbsSelfMantissa[0] + '.' + frac
            return ('-' if self.Mantissa < 0 else '') + strAbsSelfMantissa + "e" + str(self.Exponent)

    # return number in the form of
    # Mantissa = ###.#######, Exponent = ###*3
    # returns new mantissa as a string with adecimal point
    # and the exponent as an integer
    def sci(self):
        strMantissa = str(self.Mantissa)
        strMantissa = strMantissa.replace('-', '')
        lenStrMantissa = len(strMantissa)
        diff = self.Exponent - lenStrMantissa + 4 # 3 additional places
        strMantissa = strMantissa + '0'*diff
        expo = self.Exponent
        multfac = self.Exponent % 3 + 1
        expo = (self.Exponent // 3) * 3
        man = ('-' if (self.Sign == -1) else '') + strMantissa[:multfac] + '.' + strMantissa[multfac:]
        # handle the case when mantissa string is like '123.' -- add a zero at end
        if man[-1:] == '.':
            man += '0'
        return man, expo

    # similar to sci(), but returns a single string as ###.#######e###
    def scistr(self):
        m, e = self.sci()
        return m + 'e' + str(e)

    def floor(self):
        i = self.int(preserveType = True)
        return i if self.Sign >= 0 else i-1

    def ceil(self):
        return self.floor() + 1

    def __neg__(self):
        return mpap(Mantissa = (-1) * self.Mantissa, Exponent = self.Exponent, InternalAware = True)

    def __floordiv__ (self, other):
        if(not isinstance(other, mpap)):
            return self // mpap(other)
        #for negative numbers, round downwards, not towards 0
        res = (self / other).floor()
        return res

    def __mod__ (self, other):
        if(not isinstance(other, mpap)):
            return self % mpap(other)
        return self.bfwrapper2(other, 16)

    def __abs__(self):
        if(self.Sign == 1):
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
        return self + (-other)

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
        global MPAPERRORFLAG
        if(not isinstance(other, mpap)):
            return self ** mpap(other)
        if (self.Sign == -1 and other.Exponent < 0):
            MPAPERRORFLAG = "Complex result is not implemented."
            return mpap (0)
        return self.bfwrapper2(other, 4)

    def sgn(self):
        return self.Sign

    def log (self):
        global MPAPERRORFLAG
        ## See https://stackoverflow.com/questions/27179674/examples-of-log-algorithm-using-arbitrary-precision-maths
        if (self <= 0):
            MPAPERRORFLAG = "I give up!"
            return mpap (0)
        if (self == 1):
            return mpap(0)
        #t = utime.ticks_ms()
        r = self.bfwrapper1(6)
        #print ("Time taken for log:", utime.ticks_diff(utime.ticks_ms(), t))
        return r

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
        return self.bfwrapper1(9)

    def sin (self):
        return self.bfwrapper1(7)

    def cos (self):
        return self.bfwrapper1(8)

    def acos (self):
        return self.bfwrapper1(12)

    def asin (self):
        return self.bfwrapper1(13)

    def atan (self):
        return self.bfwrapper1(10)

    def atan2 (self):
        return self.bfwrapper1(11)

    def endian(self, boundary=8):
        boundary = int(boundary)
        if boundary == 0:
            boundary = 8;
        copy = self
        result = mpap(0)
        while copy != 0:
            result <<= boundary
            result |= (copy & ((1<<boundary)-1))
            copy >>= boundary

        return result

    def factors (self):
        n = int(self)

        if n == 0:
            self.result = 0
    
        self.result = set()
        self.result |= {int(1), n}
    
        def all_multiples(result, n, factor):
            z = n
            f = int(factor)
            while z % f == 0:
                result |= {f, z // f}
                f += factor
            return result
        
        self.result = all_multiples(self.result, n, 2)
        self.result = all_multiples(self.result, n, 3)
        
        for i in range(1, int(self.sqrt()) + 1, 6):
            i1 = i + 1
            i2 = i + 5
            if not n % i1:
                self.result |= {int(i1), n // i1}
            if not n % i2:
                self.result |= {int(i2), n // i2}

        print (self.result)
        return mpap(1)

