from io import BytesIO
from unittest import TestCase

import json
import requests

from .helper import (
  encode_varint,
  hash256,
  int_to_little_endian,
  little_endian_to_int,
    read_varint,
)
from .script import Script

class TxFetcher:
  cache = {}

  @classmethod
  def get_url(cls, testnet=False):
    if testnet:
      return 'https://blockstream.info/testnet/api/'
    else:
      return 'https://blockstream.info/api/'

  @classmethod
  def fetch(cls, tx_id, testnet=False, fresh=False):
    raise NotImplementedError

  @classmethod
  def load_cache(cls, filename):
    raise NotImplementedError

  @classmethod
  def dump_cache(cls, filename):
    raise NotImplementedError

class Tx:
  def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
    self.version = version
    self.tx_ins = tx_ins
    self.tx_outs = tx_outs
    self.locktime = locktime
    self.testnet = testnet

  def __repr__(self):
    tx_ins = ''
    for tx_in in self.tx_ins:
      tx_ins += tx_in.__repr__() + '\n'
    tx_outs = ''
    for tx_out in self.tx_outs:
      tx_outs += tx_out.__repr__() + '\n'
    return f'tx: {self.id()}\nversion: {self.version}\ntx_ins:\n{tx_ins}\ntx_outs:\n{tx_outs}locktime:{self.locktime}'

  def id(self):
    '''Human-readable hexadecimal of the transaction hash'''
    return self.hash().hex()

  def hash(self):
    '''Binary hash of the legacy serialization'''
    return hash256(self.serialize())[::-1]

  @classmethod
  def parse(cls, s, testnet=False):
    raise NotImplementedError

  @classmethod
  def serialize(self):
    raise NotImplementedError

  def fee(self):
    raise NotImplementedError

class TxIn:
  def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
    self.prev_tx = prev_tx
    self.prev_index = prev_index
    if script_sig is None:  # <1>
      self.script_sig = Script()
    else:
      self.script_sig = script_sig
    self.sequence = sequence

  def __repr__(self):
    return f'{self.prev_tx.hex()}:{self.prev_index}'

  @classmethod
  def parse(cls, s):
    raise NotImplementedError

  def serialize(self):
    raise NotImplementedError

  def fetch_tx(self, testnet=False):
    raise NotImplementedError

  def value(self, testnet=False):
    raise NotImplementedError

  def value(self, testnet=False):
    raise NotImplementedError

  def script_pubkey(self, testnet=False):
    raise NotImplementedError

class TxOut:
  def __init__(self, amount, script_pubkey):
    self.amount = amount
    self.script_pubkey = script_pubkey

  def __repr__(self):
    return f'{self.amount}: {self.script_pubkey}'

  @classmethod
  def parse(cls, s):
    raise NotImplementedError

  def serialize(self):
    raise NotImplementedError