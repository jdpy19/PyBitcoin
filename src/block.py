from .helper import (
  bits_to_target,
  hash256,
  int_to_little_endian,
  little_endian_to_int,
)

GENESIS_BLOCK = bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c')
TESTNET_GENESIS_BLOCK = bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff001d1aa4ae18')
LOWEST_BITS = bytes.fromhex('ffff001d')

class Block:
  def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce):
    self.version = version
    self.prev_block = prev_block
    self.merkle_root = merkle_root
    self.timestamp = timestamp
    self.bits = bits
    self.nonce = nonce

  @classmethod
  def parse(cls, s):
    version = little_endian_to_int(s.read(4))
    prev_block = s.read(32)[::-1]
    merkle_root = s.read(32)[::-1]
    timestamp = little_endian_to_int(s.read(4))
    bits = s.read(4)
    nonce = s.read(4)
    return cls(version, prev_block, merkle_root, timestamp, bits, nonce)

  def serialize(self):
    result = int_to_little_endian(self.version, 4)
    result += self.prev_block[::-1]
    result += self.merkle_root[::-1]
    result += int_to_little_endian(self.timestamp, 4)
    result += self.bits
    result += self.nonce
    return result

  def hash(self):
    return hash256(self.serialize())[::-1]

  def bip9(self):
    return self.version >> 29 == 0b001

  def bip91(self):
    return self.version >> 4 & 1 == 1

  def bip141(self):
    return self.version >> 1 & 1 == 1

  def target(self):
    return bits_to_target(self.bits)

  def difficulty(self):
    exponent = self.bits[-1]
    coefficient = little_endian_to_int(self.bits[:-1])
    target = coefficient*256**(exponent-3)
    return 0xffff * 256**(0x1d - 3) / target

  def check_pow(self):
    return little_endian_to_int(hash256(self.serialize())) < self.target()