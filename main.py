import json
import sys

# import bencodepy - available if you need it!
# import requests - available if you need it!

def decode_string(x):
    colon_index = x.find(b":")

    if colon_index == -1:
        raise ValueError('Invalid value')
    
    if x[0:colon_index].isdigit():
        size_of_x = int(x[0:colon_index])
    else:
        raise ValueError('Invalid value')

    if len(x[colon_index+1:]) != size_of_x:
        raise ValueError('Invalid string')
    
    return x[colon_index+1:]

def decode_integer(x):
    if not x.endswith(b'e'):
        raise ValueError("Invalid Integer: Must start with 'i' and end with 'e'.")
    elif x[1:-1] == b'-0' or x[1:-1].startswith(b'0') and len(x[1:-1]) > 1:
        raise ValueError("Invalid Integer")
    elif chr(x[1]) == '-' and x[2:-1].isdigit():
        return int(x[1:-1])
    elif x[1:-1].isdigit():
        return int(x[1:-1])
    else:
        raise ValueError("Invalid Input")

def decode_list(x):
    
    index = 1
    decoded_list = []
    while index != len(x):
        if index > len(x):
            raise ValueError("Invalid List")
        if chr(x[index]) == 'i':
            e_index = x[index:].find(b'e')
            if e_index == -1:
                raise ValueError("Invalid List")
            decoded_list.append(decode_integer(x[index:index + e_index + 1]))
            index += e_index + 2
        elif chr(x[index]).isdigit():
            colon_index = x.find(b':')
            if x[index:colon_index].isdigit():
                size_of_x = int(x[index:colon_index])
            else:
                raise ValueError('Invalid List')
            decoded_list.append(decode_string(x[index:colon_index + size_of_x+1]))
            index = colon_index + size_of_x+1
        else:
            raise ValueError('Invalid List')
    return decoded_list


# Examples:
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"
def decode_bencode(bencoded_value):

    if chr(bencoded_value[0]).isdigit():
        return decode_string(bencoded_value)
    elif chr(bencoded_value[0]) == 'i':
        return decode_integer(bencoded_value)
    elif chr(bencoded_value[0] == 'l'):
        return decode_list(bencoded_value)

    raise NotImplementedError("Only strings are supported at the moment")

def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")

if __name__ == "__main__":
    main()
