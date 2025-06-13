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
    ans_list = []
    while not(chr(x[index]) == 'e'):
        if chr(x[index]).isdigit():
            number_part = x[index:].find(b':') + index
            if x[index:number_part].isdigit():
                size_of_x = int(x[index:number_part])
            else:
                raise ValueError('Invalid string size')
            ans_list.append(decode_string(x[index:number_part + size_of_x + 1]))
            index = number_part + size_of_x + 1
        elif chr(x[index]) == 'i':
            e_index = x[index:].find(b'e') + index
            print(x[index:e_index+1])
            ans_list.append(decode_integer(x[index:e_index+1]))
            index = e_index + 1
        elif chr(x[index]) == 'd':
            ans_list.append(decode_dictionary(x[index:]))
        elif chr(x[index]) == 'l':
            ans, nested_index = decode_list(x[index:])
            print(ans, nested_index)
            ans_list.append(ans)
            index += nested_index
    return (ans_list, index)

def decode_dictionary(x):
    index = 1
    name_value = 0
    while index != len(x):
        name = decode_string(x[index])
        index += len(name)
        decode_bencode(x[index:])
    
def decode_bencode(x):
    if chr(x[0]).isdigit():
        return decode_string(x)
    elif chr(x[0]) == 'i':
        return decode_integer(x)
    elif chr(x[0]) == 'd':
        return decode_dictionary(x)
    elif chr(x[0] == 'l'):
        return decode_list(x)

def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")

if __name__ == "__main__":
    main()
