#!/usr/bin/env python3
import ctypes
import hashlib
import binascii
import base58
import sys
import ast
import json
import os
from base58 import encode as base58_encode
 
################################################################################
################################################################################
ssl_library = ctypes.cdll.LoadLibrary('libssl.so')
 
def gen_ecdsa_pair():
    NID_secp160k1 = 708
    NID_secp256k1 = 714
    k = ssl_library.EC_KEY_new_by_curve_name(NID_secp256k1)
 
    if ssl_library.EC_KEY_generate_key(k) != 1:
        raise Exception("internal error?")
 
    bignum_private_key = ssl_library.EC_KEY_get0_private_key(k)
    size = (ssl_library.BN_num_bits(bignum_private_key)+7)//8
    storage = ctypes.create_string_buffer(size)
    ssl_library.BN_bn2bin(bignum_private_key, storage)
    private_key = storage.raw
    size = ssl_library.i2o_ECPublicKey(k, 0)
    storage = ctypes.create_string_buffer(size)
    ssl_library.i2o_ECPublicKey(k, ctypes.byref(ctypes.pointer(storage)))
    public_key = storage.raw
 
    ssl_library.EC_KEY_free(k)
    return public_key, private_key
 
 
def ecdsa_get_coordinates(public_key):
    x = bytes(public_key[1:33])
    y = bytes(public_key[33:65])
    return x, y
 
 
def generate_address(public_key):
    assert isinstance(public_key, bytes)
    x, y = ecdsa_get_coordinates(public_key)
    s = b'\x04' + x + y 
    hasher = hashlib.sha256()
    hasher.update(s)
    r = hasher.digest()
    hasher = hashlib.new('ripemd160')
    hasher.update(r)
    r = hasher.digest()
    return base58_check(r, version=60)
 
 
def base58_check(src, version=0):
    src = bytes([version]) + src
    hasher = hashlib.sha256()
    hasher.update(src)
    r = hasher.digest()
    hasher = hashlib.sha256()
    hasher.update(r)
    r = hasher.digest()
    checksum = r[:4]
    s = src + checksum
    return base58_encode(int.from_bytes(s, 'big'))
 
 
def generatepair():
    public_key, private_key = gen_ecdsa_pair()
    hex_private_key = ''.join(["{:02x}".format(i) for i in private_key])
    assert len(hex_private_key) == 64
    priv = base58_check(private_key, version=188)
    pub = ''.join(['{:02x}'.format(i) for i in public_key])
    addr = generate_address(public_key)
    segid = getsegid(addr)
    return([segid, pub, priv, addr])
 
 
def genaddresses():
    segids = {}
    while len(segids.keys()) < 64:
        try:
            genvaldump_result = generatepair()
        except Exception as e:
            continue
        segid = genvaldump_result[0]
        if segid in segids:
            pass
        else:
            segids[segid] = genvaldump_result

    segids_array = []
    for position in range(64):
        segids_array.append(segids[position])

    f = open("PRIVATE.json", "w+")
    f.write(json.dumps(segids_array))
    return(segids_array)


def getsegid(addr):
    byte0 = hashlib.sha256(addr.encode()).hexdigest()[:2].encode('utf-8')
    return(int(byte0, 16) & 63)

if os.path.isfile('PRIVATE.json'):
    print('Please move PRIVATE.json to generate another.')
    sys.exit(0)
    
NAME = input('Please input your name: ')
    
segids = genaddresses()
addrs = []

for i in segids:
    addrs.append(i[3])
    
with open('participants.json') as part:
    participants = json.load(part)
participants[NAME] = addrs
f = open("participants.json", "w+")
f.write(json.dumps(participants))

print('PRIVATE.json created. THIS FILE CONTAINS PRIVATE KEYS. KEEP IT SAFE.')
