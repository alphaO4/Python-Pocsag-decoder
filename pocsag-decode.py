def decode_pocsag(bits):
    sync_word = '0101010101010101'  # POCSAG sync word
    message = ''
    sync_found = False
    
    for i in range(len(bits)-15):
        if not sync_found and bits[i:i+16] == sync_word:
            sync_found = True
            i += 15
        elif sync_found:
            char_bits = bits[i:i+8]
            char_code = int(''.join(map(str, char_bits[::-1])), 2)  # reverse bit order and convert to integer
            if char_code == 0:  # end of message
                break
            if char_code >= 32 and char_code <= 127:  # printable ASCII characters
                message += chr(char_code)
            i += 7
    
    return message
