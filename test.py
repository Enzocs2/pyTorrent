import json
import sys

import bencodepy
import hashlib
# import requests - available if you need it!

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"

def bytes_to_str(data):
    return data.decode()

def main():
    command = sys.argv[1]

    # You can use print statements as follows for debugging, they'll be visible when running tests.

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.

        bc = bencodepy.Bencode(
            encoding="utf-8"
        )
        decoded = bc.decode(bytes_to_str(bencoded_value))
        if  type(decoded) == str:
            print(f'"{decoded}"')
        else:
            print(str(decoded).replace("'","\""))
    elif command == "info":
        with open(sys.argv[2], "rb") as f:
            bencoded_value = f.read()
            decoded = bencodepy.decode(bencoded_value)
            encoded_info = bencodepy.encode(decoded[b"info"])
            pieces = decoded[b"info"][b"pieces"].hex()
            print(type(pieces))
            print(f"Tracker URL: {decoded[b"announce"].decode()}")
            print(f"Length: {decoded[b"info"][b"length"]}")
            print(f"Info Hash: {hashlib.sha1(encoded_info).hexdigest()}")
            print(f"Piece Length: {decoded[b"info"][b"piece length"]}")
            print(f"Piece Hashes: \n{"\n".join([pieces[i:i+40] for i in range(0,len(pieces),40)])}")
            f.close()
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()