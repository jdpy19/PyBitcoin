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
  
  @classmethod
  def parse(cls, s):
    length = read_varint(s)
    cmds = []
    count = 0
    while count < length:
      current = s.read(1)
      count += 1
      current_byte = int(current[0])
      if current_byte >= 1 and current_byte <= 75:
        n = current_byte
        cmds.append(s.read(n))
        count += n
      elif current_byte == 76: # op_pushdata1
        data_length = little_endian_to_int(s.read(1))
        cmds.append(s.read(data_length))
        count += data_length + 1
      elif current_byte == 77: # op_pushdata2
        data_length = little_endian_to_int(s.read(2))
        cmds.append(s.read(data_length))
        count += data_length + 2
      else:
        op_code = current_byte
        cmds.append(op_code)
    if count != length:
      raise SyntaxError('Parsing Script Failed.')
    return cls(cmds)

  def raw_serialize(self):
    result = b''
    for cmd in self.cmds:
      if type(cmd) == int:
        result += int_to_little_endian(cmd, 1)
      else:
        length = len(cmd)
        if length < 75:
          result += int_to_little_endian(length, 1)
        elif length > 75 and length < 0x100: # OP_PUSHDATA1
          result += int_to_little_endian(76, 1)
          result += int_to_little_endian(length, 1)
        elif length >= 0x100 and length <= 520: # OP_PUSHDATA2
          result += int_to_little_endian(77, 1)
          result += int_to_little_endian(length, 2)
        else:
          raise ValueError('cmd too long.')
        result += cmd
    return result

  def serialize(self):
    result = self.raw_serialize()
    total = len(result)
    return encode_varint(total) + result

  def evaluate(self, z):
    cmds = self.cmds[:]
    stack = []
    altstack = []
    while len(cmds) > 0:
      cmd = cmds.pop(0)
      if type(cmd) == int:
        operation = OP_CODE_FUNCTIONS[cmd]
        if cmd in (99, 100): #op_if/op_notif require the cmds array
          if not operation(stack, cmds):
            LOGGER.info(f'Bad OP: {OP_CODE_NAMES[cmd]}')
            return False
        elif cmd in (107, 108): # OP_TOALTSTACK/OP_FROM_ALTSTACK require the altstack
          if not operation(stack, altstack):
            LOGGER.info(f'Bad OP: {OP_CODE_NAMES[cmd]}')
            return False
        elif cmd in (172, 173, 174, 175): # Signing operations, require sig_hash
          if not operation(stack, z):
            LOGGER.info(f'Bad OP: {OP_CODE_NAMES[cmd]}')
            return False
        else:
          if not operation(stack):
            LOGGER.info('bad op: {}'.format(OP_CODE_NAMES[cmd]))
            return False
      else:
        stack.append(cmd)
    if len(stack) == 0:
      return False
    if stack.pop() == b'':
      return False
    return True

