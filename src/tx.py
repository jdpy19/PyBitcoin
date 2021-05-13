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