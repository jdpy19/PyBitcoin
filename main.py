from src.secp256k1 import PrivateKey
from src.helper import little_endian_to_int, hash256

# Create a testnet address
passphrase = b'IREALLYNEEDTOPOOPRIGHTNOW'
secret = little_endian_to_int(hash256(passphrase))
private_key = PrivateKey(secret)
print(private_key.point.address(compressed=True, testnet=True))
# Address: mhd478kdPu9QjcwWhisnpim5fSBcZESURd
# Send them back to: tb1qm5tfegjevj27yvvna9elym9lnzcf0zraxgl8z2