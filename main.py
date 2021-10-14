from src.secp256k1 import PrivateKey
from src.helper import (
  little_endian_to_int, 
  hash256, 
  decode_base58, 
  SIGHASH_ALL,
  SATOSHIS
)
from src.tx import TxIn, TxOut, Tx, TxFetcher
from io import BytesIO

def create_testnet_private_key(passphrase):
  secret = little_endian_to_int(hash256(passphrase))
  private_key = PrivateKey(secret)
  return private_key

def main():
  passphrase = b'IREALLYNEEDTOPOOPRIGHTNOW'
  private_key = create_testnet_private_key(passphrase)
  print(private_key.secret)
  change_address = private_key.point.address(compressed=True, testnet=True)
  print(f'Change Address: {change_address}')

  passphrase2 = b'IREALLYNEEDTOPOOPRIGHTNOW3'
  private_key_2 = create_testnet_private_key(passphrase2)
  target_address = private_key_2.point.address(compressed=True, testnet=True)
  print(f'Target Address: {target_address}')
  # Address: mhd478kdPu9QjcwWhisnpim5fSBcZESURd
  # Send them back to: tb1qm5tfegjevj27yvvna9elym9lnzcf0zraxgl8z2

  wallet_total_amount = 0.0011
  send_amount = 0.001
  fee = 0.00005

  tx_ins = [
    TxIn(bytes.fromhex('791457a6f2ed5aecf4d9b9dd24488a2a9c60aa745759f0855e2d05b9fa823ae6'), 0),
    TxIn(bytes.fromhex('4accf114a2ba3342204fbfb247079196372d25e5482a603eb07cabb8a490027d'), 0)
  ]
  tx_outs = []
  
  change_h160 = decode_base58(change_address)
  change_amount = int((wallet_total_amount - (send_amount + fee)) * SATOSHIS)
  change_script = p2pkh_script(change_h160)
  change_output = TxOut(amount=change_amount, script_pubkey=change_script)

  target_amount = int(send_amount * SATOSHIS)
  target_h160 = decode_base58(target_address)
  target_script = p2pkh_script(target_h160)
  target_output = TxOut(amount=target_amount, script_pubkey=target_script)
  tx_obj = Tx(1, tx_ins, [change_output, target_output], 0, testnet=True)

  tx_obj.sign_input(0, private_key)
  tx_obj.sign_input(1, private_key)
  print(tx_obj.serialize().hex())
  for tx_in in tx_ins:
    print(tx_in.value())
if __name__ == '__main__':
  main()