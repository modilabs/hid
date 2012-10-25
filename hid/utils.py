# encoding=utf-8
# maintainer: katembu

import math

VALID_CHARS = "0123456789ACDEFGHJKLMNPRTUVWXY"


def getBaseCharacters():
    '''Return base characters'''
    return VALID_CHARS


def generate(id_without_check):
    checkdigit = checkDigit(id_without_check)
    identifier = id_without_check+checkdigit


def computeCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)
          
        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()
         
        # this will be a running total
        sum = 0;
        
        # loop through digits from right to left
        for n, char in enumerate(reversed(identifier)):
             
            if not valid_chars.count(char):
                raise Exception('InvalidIDException')
             
            # Point 
            code_point = valid_chars.index(char)
              
            # weight will be the current digit's contribution to
            # the running total
            weight = None
            if (n % 2 == 0):
                weight = (2 * code_point)
            else:
                weight = code_point

            weight = (weight/mod)+(weight%mod)    
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod;
        checkCodePoint = mod - remainder;
        return valid_chars[checkCodePoint];


def validateCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)
          
        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()
         
        # this will be a running total
        sum = 0;
        
        # loop through digits from right to left
        for n, char in enumerate(reversed(identifier)):
             
            if not valid_chars.count(char):
                raise Exception('InvalidIDException')
             
            # Point 
            code_point = valid_chars.index(char)
              
            # weight will be the current digit's contribution to
            # the running total
            weight = None
            if (n % 2 == 0):
                weight = code_point
            else:
                weight = (2 * code_point)

            weight = (weight/mod)+(weight%mod)    
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod;
        return (remainder==0)
