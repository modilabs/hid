# encoding=utf-8
# maintainer: katembu


import os
from urlparse import urlparse
import httplib
import math
import random

from datetime import datetime

VALID_CHARS = "0123456789ACDEFGHJKLMNPRTUVWXY"
LEN = 4


def getBaseCharacters():
    '''Return base characters'''
    return VALID_CHARS


def getIdentifierLength():
    '''Return Identifier Length'''
    return LEN


def generate(id_without_check):
    '''Append Check digit '''
    checkdigit = computeCheckDigit(id_without_check)
    return id_without_check + checkdigit


def computeCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)
        print identifier

        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        #this will be a running total
        sum = 0

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

            weight = (weight / mod) + (weight % mod)
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod
        checkCodePoint = mod - remainder
        print remainder
        print checkCodePoint
        try:
            checkdigit = valid_chars[checkCodePoint]
        except:
            checkdigit = valid_chars[0]

        return checkdigit


def validateCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)

        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        # this will be a running total
        sum = 0
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

            weight = (weight / mod) + (weight % mod)
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod
        return (remainder == 0)


def generateIdentifier():
    char = getBaseCharacters()
    slen = getIdentifierLength()
    identifier = ''.join([random.choice(char) for i in range(0, slen - 1)])
    return generate(identifier)

  
def transmit_form(form):
    ''' Submit data to commcare server '''
    xml_form = form.data
    headers = {"Content-type": "text/xml", "Accept": "text/plain"}
    url = form.COMMCARE_URL
    SUBMIT_CASEXML = form.SUBMIT_TO_COMMCARE

    if SUBMIT_CASEXML:
        print url
        up = urlparse(url)
        conn = httplib.HTTPSConnection(up.netloc) if url.startswith("https") \
                                        else httplib.HTTPConnection(up.netloc)
        conn.request('POST', up.path, xml_form, headers)
        resp = conn.getresponse()
        responsetext = resp.read()
        if resp.status == 201:
            print "Bad HTTP Response: %s " % responsetext
        else:
            print "Thanks for submitting %s Bad response text" % responsetext
