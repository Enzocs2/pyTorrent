import sys
import hashlib

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
            ans_list.append(decode_integer(x[index:e_index+1]))
            index = e_index + 1
        elif chr(x[index]) == 'd':
            ans, nested_index = decode_dictionary(x[index:])
            ans_list.append(ans)
            index += nested_index + 1
        elif chr(x[index]) == 'l':
            ans, nested_index = decode_list(x[index:])
            ans_list.append(ans)
            index += nested_index + 1
    return (ans_list, index)

def decode_dictionary(x):
    index = 1
    dict = {}
    while not(chr(x[index]) == 'e'):
        number_part = x[index:].find(b':') + index
        if x[index:number_part].isdigit():
            size_of_x = int(x[index:number_part])
        else:
            raise ValueError('Invalid string size')
        name = decode_string(x[index:number_part + size_of_x + 1])
        index = number_part + size_of_x + 1
        if chr(x[index]).isdigit():
            number_part = x[index:].find(b':') + index
            if x[index:number_part].isdigit():
                size_of_x = int(x[index:number_part])
            else:
                raise ValueError('Invalid string size')
            value = decode_string(x[index:number_part + size_of_x + 1])
            index = number_part + size_of_x + 1
        elif chr(x[index]) == 'i':
            e_index = x[index:].find(b'e') + index
            value =  decode_integer(x[index:e_index+1])
            index = e_index + 1
        elif chr(x[index]) == 'd':
            value, nested_index = decode_dictionary(x[index:])
            index += nested_index + 1
        elif chr(x[index]) == 'l':
            value, nested_index = decode_list(x[index:])
            index += nested_index + 1
        dict[name] = value
    return (dict, index)
    
def decode_bencode(x):
    if chr(x[0]).isdigit():
        return decode_string(x)
    elif chr(x[0]) == 'i':
        return decode_integer(x)
    elif chr(x[0]) == 'd':
        return decode_dictionary(x)
    elif chr(x[0] == 'l'):
        return decode_list(x)

def encode_dict(x):
    encoded_value = b''
    for key, val in x.items():
        try:
            encoded_value += f"{len(key)}:".encode('ascii') + key
            if isinstance(val, int):
                encoded_value += f"i{val}e".encode('ascii')
            elif isinstance(val, bytes):
                encoded_value += f"{len(val)}:".encode('ascii') + val
            elif isinstance(val, list):
                encoded_list = b"".join([encode_dict(item) for item in val])
                encoded_value += b'l' + encoded_list + b'e'
        except Exception as e:
            print("Error: ", e)
    return b'd' + encoded_value + b'e'


def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")
        print(decode_bencode(bencoded_value))
    if command == "info":
        try:
            file_name = sys.argv[2].encode()
            with open(file_name, 'rb') as f:
                content = f.read()
                val, _ = decode_bencode(content) # type: ignore
                print('Tracker URL: ', val[b'announce'], '\nLength: ', val[b'info'][b'length'] )
                print('Info: ', val[b'info'])
                print('Info_hash: ',(hashlib.sha1(encode_dict(val[b'info'])).hexdigest()))
                print('Piece Length: ', val[b'info'][b'piece length'])
                pieces = val[b"info"][b"pieces"].hex()
                pieces_hashes = [pieces[i:i+40] for i in range(0,len(pieces),40)]
                print(pieces_hashes)

        except FileNotFoundError:
            print("Error: The file was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        raise NotImplementedError(f"Unknown command {command}")

if __name__ == "__main__":
    main()
