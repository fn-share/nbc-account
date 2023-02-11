# The MIT License (MIT)
#
# Copyright (c) 2014 Richard Moore
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import struct, hashlib

from . import base58
from . import ecc
from . import key

from .hash import sha1, sha256, sha256d, ripemd160, hash160

__all__ = [ 'base58', 'ecc', 'key', 'sha1', 'sha256', 'sha256d', 'ripemd160', 'hash160' ]

#---- formatting helpers

def publickey_hash(pub_key):
    pubHash = hashlib.sha512(pub_key).digest()
    s1 = hashlib.new('ripemd160',pubHash[:32]).digest()
    s2 = hashlib.new('ripemd160',pubHash[32:]).digest()
    return hashlib.sha256(s1+s2).digest()


#---- block header helpers

_struct_head1 = struct.Struct('<II32s32sIII')  # full header
_struct_head2 = struct.Struct('<II32s32sII')   # header that excluding nonce

def get_block_header(ver, chain_no, prev_block, merkle_root, timestamp, bits, nonce):  # total 84 bytes
  return _struct_head1.pack(ver,chain_no,prev_block,merkle_root,timestamp,bits,nonce)

def get_block_header2(ver, chain_no, prev_block, merkle_root, timestamp, bits):  # total 80 bytes
  return _struct_head2.pack(ver,chain_no,prev_block,merkle_root,timestamp,bits)

def get_merkle_root(txns):
  branches = [t.hash for t in txns]
  
  while len(branches) > 1:
    if (len(branches) % 2) == 1:
      branches.append(branches[-1])
    branches = [sha256d(a+b) for a,b in zip(branches[0::2],branches[1::2])]
  
  return branches[0]
