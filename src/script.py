from io import BytesIO
from logging import getLogger

from .helper import (
  encode_varint,
  int_to_little_endian,
  little_endian_to_int,
  read_varint,
)
from .op import (
  OP_CODE_FUNCTIONS,
  OP_CODE_NAMES,
)

LOGGER = getLogger(__name__)

class Script:
  def __init__(self, cmds=None):
    if cmds is None:
      self.cmds = []
    else:
      self.cmds = cmds

  def __repr__(self):
    result = []
    for cmd in self.cmds:
      if type(cmd) == int:
        if OP_CODE_NAMES.get(cmd):
          name = OP_CODE_NAMES.get(cmd)
        else:
          name = f'OP_[{cmd}]'
        result.append(name)
      else:
        result.append(cmd.hex())
    return ' '.join(result)
  
  def parse(cls, s):
    raise NotImplementedError

  def raw_serialize(self):
    raise NotImplementedError

  def serialize(self):
    raise NotImplementedError

  def evaluate(self, z):
    raise NotImplementedError 