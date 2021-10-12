from .script import Script

def p2pk_script():
  return Script(
    [
      0xac
    ]
  )

def p2pkh_script(h160):
  return Script([
    0x76, # OP_DUP
    0xa9, # OP_HASH160
    h160, # hash
    0x88, # OP_EQUALVERIFY
    0xac # OP_CHECKSIG
  ])

# efficient multisig compared to bare multisig
def p2sh_script(h160):
  raise NotImplementedError