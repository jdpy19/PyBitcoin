from io import BytesIO
from src.block import Block, GENESIS_BLOCK, LOWEST_BITS
from src.network import SimpleNode, GetHeadersMessage, HeadersMessage
from src.helper import calculate_new_bits

def main():
  previous = Block.parse(BytesIO(GENESIS_BLOCK))
  first_epoch_timestamp = previous.timestamp
  expected_bits = LOWEST_BITS
  count = 1
  node = SimpleNode('mainnet.programmingbitcoin.com', testnet=False, logging=False)
  node.handshake()
  for _ in range(21):
    getHeaders = GetHeadersMessage(start_block=previous.hash())  
    node.send(getHeaders)
    headers = node.wait_for(HeadersMessage)
    for header in headers.blocks:
      if not header.check_pow():
        raise RuntimeError(f'Bad PoW at block {count}')
      if header.prev_block != previous.hash():
        raise RuntimeError(f'Discountinous block at {count}')
      if count % 2016 == 0:
        time_diff = previous.timestamp - first_epoch_timestamp
        expected_bits = calculate_new_bits(previous.bits, time_diff)
        print(expected_bits.hex())
        first_epoch_timestamp = header.timestamp
      if header.bits != expected_bits:
        raise RuntimeError(f'Bad bits at block {count}')
      previous = header
      count += 1
  
  

if __name__ == '__main__':
  main()