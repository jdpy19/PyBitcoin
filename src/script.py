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