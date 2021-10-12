from .ecc import FieldElement, Point
from random import randint
from .helper import hash160, encode_base58_checksum

from io import BytesIO
import hashlib
import hmac

A = 0
B = 7
P = 2**256 - 2**32 - 977
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Field(FieldElement):
  def __init__(self, num, prime=None):
    super().__init__(num=num, prime=P)

  def __repr__(self):
    return '{:x}'.format(self.num).zfill(64)

  def sqrt(self):
    return self**((P + 1) // 4)

class S256Point(Point):
  def __init__(self, x, y, a=None, b=None):
    a, b = S256Field(A), S256Field(B)
    if type(x) == int:
      super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
    else:
      super().__init__(x=x, y=y, a=a, b=b)

  def __repr__(self):
    if self.x is None:
      return 'S256Point(infinity)'
    else:
      return 'S256Point({}, {})'.format(self.x, self.y)

  def __rmul__(self, coefficient):
    coef = coefficient % N
    return super().__rmul__(coef)

  def hash160(self, compressed=True):
    return hash160(self.sec(compressed))

  def verify(self, z, sig):
    s_inv = pow(sig.s, N-2, N)
    u = z * s_inv % N
    v = sig.r * s_inv % N
    total = u * G + v * self
    return total.x.num == sig.r

  def sec(self, compressed=True):
    '''Retuns thse binary version of the SEC format'''
    if compressed:
      if self.y.num % 2 == 0:
        return b'\x02' + self.x.num.to_bytes(32, 'big')
      else:
        return b'\x03' + self.x.num.to_bytes(32, 'big')
    else:
      return b'\x04' + self.x.num.to_bytes(32, 'big') + self.y.num.to_bytes(32, 'big')

  def address(self, compressed=True, testnet=False):
    '''returns the address string'''
    h160 = self.hash160(compressed)
    prefix = b'\x6f' if testnet else b'\x00'
    return encode_base58_checksum(prefix + h160)

  @classmethod
  def parse(self, sec_bin):
    '''returns a Point object from a SEC binary (not hex)'''
    if sec_bin[0] == 4:
      x = int.from_bytes(sec_bin[1:33], 'big')
      y = int.from_bytes(sec_bin[33:65], 'big')
      return S256Point(x=x, y=y)
    else:
      x = S256Field(int.from_bytes(sec_bin[1:], 'big'))
      alpha = x**3 + S256Field(B)
      beta = alpha.sqrt()

      even_beta = beta if beta.num % 2 == 0 else S256Field(P - beta.num)
      odd_beta =  beta if beta.num % 2 != 0 else S256Field(P - beta.num)

      if sec_bin[0] == 2: # Even
        return S256Point(x, even_beta)
      elif sec_bin[0] == 3: # ODD
        return S256Point(x, odd_beta)

G = S256Point(
  0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
  0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)

def der_preparation(i):
  i_bin = i.to_bytes(32, 'big')
  i_bin = i_bin.lstrip(b'\x00')
  if i_bin[0] & 0x80:
    i_bin = b'\x00' + i_bin
  return i_bin

class Signature:
  def __init__(self, r, s):
    self.r = r
    self.s = s

  def __repr__(self):
    return 'Signature({:x}, {:x})'.format(self.r, self.s)

  def der(self):
    r_bin = der_preparation(self.r)
    s_bin = der_preparation(self.s)
    result = bytes([2, len(r_bin)]) + r_bin + bytes([2, len(s_bin)]) + s_bin
    return bytes([0x30, len(result)]) + result

  @classmethod
  def parse(cls, signature_bin):
    s = BytesIO(signature_bin)
    compound = s.read(1)[0]
    if compound != 0x30:
      raise SyntaxError("Bad Signature")
    length = s.read(1)[0]
    if length + 2 != len(signature_bin):
      raise SyntaxError("Bad Signature Length")
    marker = s.read(1)[0]
    if marker != 0x02:
      raise SyntaxError("Bad Signature")
    rlength = s.read(1)[0]
    r = int.from_bytes(s.read(rlength), 'big')
    marker = s.read(1)[0]
    if marker != 0x02:
      raise SyntaxError("Bad Signature")
    slength = s.read(1)[0]
    s = int.from_bytes(s.read(slength), 'big')
    if len(signature_bin) != 6 + rlength + slength:
      raise SyntaxError("Signature too long")
    return cls(r, s)

class PrivateKey:
  def __init__(self, secret):
    self.secret = secret
    self.point = secret * G

  def hex(self):
    return '{:x}'.format(self.secret).zfill(64)

  def deterministic_k(self, z):
    k = b'\x00' * 32
    v = b'\x01' * 32
    if z > N:
      z -= N
    z_bytes = z.to_bytes(32, 'big')
    secret_bytes = self.secret.to_bytes(32, 'big')
    s256 = hashlib.sha256
    k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
    v = hmac.new(k, v, s256).digest()
    k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
    v = hmac.new(k, v, s256).digest()
    while True:
      v = hmac.new(k, v, s256).digest()
      candidate = int.from_bytes(v, 'big')
      if candidate >= 1 and candidate < N:
        return candidate
      k = hmac.new(k, v + b'\x00', s256).digest()
      v = hmac.new(k, v, s256).digest()
      
  def sign(self, z):
    k = self.deterministic_k(z)
    r = (k*G).x.num
    k_inv = pow(k, N-2, N)
    s = (z + r * self.secret) * k_inv % N
    if s > N/s:
      s = N - s
    return Signature(r, s)

  def wif(self, compressed=True, testnet=False):
    secret_bytes = self.secret.to_bytes(32, 'big')
    prefix = b'\xef' if testnet else b'\x80'
    suffix = b'\x01' if compressed else b''
    return encode_base58_checksum(prefix + secret_bytes + suffix)
  

