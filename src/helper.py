import hashlib

SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
TWO_WEEKS = 60 * 60 * 24 * 14
SATOSHIS = 100000000

def hash160(s):
  '''sha256 followed by ripemd160'''
  return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

def hash256(s):
  '''two rounds of sha256'''
  return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def encode_base58(s):
  count = 0
  for c in s:
    if c == 0:
      count += 1
    else:
      break
  num = int.from_bytes(s, 'big')
  prefix = '1' * count
  result = ''
  while num > 0:
    num, mod = divmod(num, 58)
    result = BASE58_ALPHABET[mod] + result
  return prefix + result

def encode_base58_checksum(b):
  return encode_base58(b + hash256(b)[:4])

def decode_base58(s):
  num = 0
  for c in s:
    num *= 58
    num += BASE58_ALPHABET.index(c)
  combined = num.to_bytes(25, byteorder='big')
  checksum = combined[-4:]
  if hash256(combined[:-4])[:4] != checksum:
    raise ValueError('bad address: {} {}'.format(checksum, hash256(combined[:-4])[:4]))
  return combined[1:-4]

def little_endian_to_int(b):
  '''little_endian_to_int takes byte sequence as a little-endian number.
  Returns an integer'''
  return int.from_bytes(b, 'little')

def int_to_little_endian(n, length):
  '''endian_to_little_endian takes an integer and returns the little-endian
  byte sequence of length'''
  return n.to_bytes(length, 'little')
  
def read_varint(s):
  '''read_varint reads a variable integer from a stream'''
  i = s.read(1)[0]
  if i == 0xfd:
    # 0xfd means the next two bytes are the number
    return little_endian_to_int(s.read(2))
  elif i == 0xfe:
    # 0xfe means the next four bytes are the number
    return little_endian_to_int(s.read(4))
  elif i == 0xff:
    # 0xff means the next eight bytes are the number
    return little_endian_to_int(s.read(8))
  else:
    # anything else is just the integer
    return i

def encode_varint(i):
  '''encodes an integer as a varint'''
  if i < 0xfd:
    return bytes([i])
  elif i < 0x10000:
    return b'\xfd' + int_to_little_endian(i, 2)
  elif i < 0x100000000:
    return b'\xfe' + int_to_little_endian(i, 4)
  elif i < 0x10000000000000000:
    return b'\xff' + int_to_little_endian(i, 8)
  else:
    raise ValueError('integer too large: {}'.format(i))

def h160_to_p2pkh_address(h160, testnet=False):
  prefix = b'\x6f' if testnet else b'\x00'
  return encode_base58_checksum(prefix + h160)

def h160_to_p2sh_address(h160, testnet=False):
  prefix = b'\xc4' if testnet else b'\x05'
  return encode_base58_checksum(prefix + h160)

def bits_to_target(bits):
  exponent = bits[-1]
  coefficient = little_endian_to_int((bits[:-1]))
  return coefficient * 256**(exponent - 3)

def target_to_bits(target):
  raw_bytes = target.to_bytes(32, 'big')
  raw_bytes = raw_bytes.lstrip(b'\x00')
  if raw_bytes[0] > 0x7f:
    exponent = len(raw_bytes) + 1
    coefficient = b'\x00' + raw_bytes[:2]
  else:
    exponent = len(raw_bytes)
    coefficient = raw_bytes[:3]
  new_bits = coefficient[::-1] + bytes([exponent])
  return new_bits

def calculate_new_bits(previous_bits, time_differential):
  if time_differential > TWO_WEEKS * 4:
    time_differential = TWO_WEEKS * 4
  if time_differential < TWO_WEEKS // 4:
    time_differential = TWO_WEEKS // 4
  new_target = bits_to_target(previous_bits) * time_differential // TWO_WEEKS
  return target_to_bits(new_target)

def merkle_parent(hash1, hash2):
  raise NotImplementedError

def merkle_parent_level(hashes):
  raise NotImplementedError

def merkle_root(hashes):
  raise NotImplementedError

def bit_field_to_bytes(bit_fields):
  raise NotImplementedError

def bytes_to_bit_field(some_bytes):
  raise NotImplementedError
