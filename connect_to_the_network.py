import socket
from src.network import (
  NetworkEnvelope, 
  VersionMessage
)

def main():
  host = 'testnet.programmingbitcoin.com'
  port = 18333
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((host, port))
  stream = s.makefile('rb', None)
  version = VersionMessage()
  envelope = NetworkEnvelope(version.command, version.serialize(), testnet=True)
  s.sendall(envelope.serialize())
  while True:
    new_message = NetworkEnvelope.parse(stream, testnet=True)
    print(new_message)

if __name__ == '__main__':
  main()