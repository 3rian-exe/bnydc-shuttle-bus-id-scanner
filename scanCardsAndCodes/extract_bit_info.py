from typing import Tuple

def get_bits_from_RFID_card(card_num: str) -> Tuple[int, str]:
    card_num.strip()

    # Count how many leading zeros are in the card number 
    # to be later added to the front of its binary representation.
    append_zeros = '0b'
    for digit in card_num:
        if digit != '0':
            break
        append_zeros += '0'

    # Convert the card number to binary, add the original leading zeros 
    # and get the length.
    card_bits = bin(int(card_num))
    card_bits = append_zeros + card_bits[2:]
    card_length = len(card_bits) - 2

    return (card_length, card_bits)


def get_facility_code_hotstamp(card_len: int, card_bits: str) -> Tuple[int, int]:

    if card_len == 26:
        facility_code = int(card_bits[2:12], 2)
        encoded_num = int(card_bits[13:], 2)

        return (facility_code, encoded_num)
    elif card_len == 37:
        pass


# Make API to retrieve the card format.
# Done in s2.py but no facility number associated card formats.

# Scan the card number.
card = input("Please scan your card: ")

print(card)
# Sanity check 
card_len, card_bits = get_bits_from_RFID_card(card)
facility_code, hotstamp = get_facility_code_hotstamp(card_len, card_bits)
print(f"card bits: {card_bits[2:]}")
print(f"card length: {card_len}")
print(f"encoded number: {hotstamp}")
print(f"facility code: {facility_code}")
    
