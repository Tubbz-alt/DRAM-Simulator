#!/usr/bin/python3

from sys import argv, exit
from math import log2
from yaml import load
from Chip import *


# DRAM specs
TIMES = {
    'RP': 1, # row precharge (closing)
    'RCD': 1, # row to column delay
    'CL': 1 # column latency
}

# testing DRAM
DRAM = {
    'chips': {
        'number': 2,
        'capacity': 512, #MB
        'rows': 2,
        'banks': 8,
        'columns': 6
        },
    'times': TIMES,
    'capacity': 1 
    }

# store the memory content provided by the simplescalar
MEMORY_CONTENT = []


def check_params():
    """
    # ./dram <dram_capacity> <chip number> <chip_capacity> <rows> <columns> <banks>
    """

    num_args = len(argv)

    if num_args == 7:
        DRAM['capacity'] = int(argv[1])
        chips = int(argv[2])
        for chip in range(chips):
            DRAM['chips']['number'] = chips
            DRAM['chips']['capacity'] = int(argv[3])
            DRAM['chips']['rows'] = int(argv[4])
            DRAM['chips']['columns'] = int(argv[5])
            DRAM['chips']['banks'] = int(argv[6])

    elif num_args > 1:
        # incorrect value, or show help
        help_string = """Usage: ./dram.py <dram_capacity> <number_chips> <chip_capacity> <rows> <columns> <banks>
        <dram_capacity>: (int) Total capacity of the DRAM expressed in GB
        <chip_number>: (int) Number of chips of DRAM 
        <chip_capacity>: (int) Capacity of the chip expressed in MB
        <rows>: (int) Row number of the chip
        <columns>: (int) Column number of the chip
        <banks>: (int) Banks number of the chip
        \nWARNING:
        * Every value must be positive pair integer
        * DRAM capacity must be equal to total chips capacity"""
        exit(help_string)


def ok_specs(DRAM=DRAM):
    """Check the DRAM total capacity while creating the chips

    Of a given DRAM dictionary checks if the specs are correct comparing
    the total DRAM capacity with the total chips' capacity.


    DRAM: Optional, Dictionary
        The DRAM specification
        
    Returns
    boolean
        Wheter the chips capacity equals total dram capacity
    """

    # for the total chip capacity divide by 1024 to convert to GB
    return DRAM['capacity'] == (DRAM['chips']['number'] * DRAM['chips']['capacity'])/1024


def bit_transform(decimal_stream):
    """Returns truncated binary value for the decimal parameter
    
    Gets the memory address and returns a suitable binary string according
    to the number of bits needed to represent the DRAM capacity (bit length)
    If bit length is > address length then stuff with 0s in MSB, 
    if not, truncate the memory address to the bit length 

    Parameters
    decimal_stream: str
        A decimal value

    Returns
    String with the binary value truncated
    """

    # first, we need to transform it to a true bit stream
    # and remove '0b' from string in order to work better
    bit_stream = bin(int(decimal_stream))[2:]

    address_length = len(bit_stream)

    """
    we will need the total number of bits needed to represent the dram total quantity
        log2(DRAM capacity in mb) + 20
    Example:
        log2(1GB) = log2(1024) = 1; 1 + 20 = 30 bits needed to represent 1GB
    """
    bit_length = int(log2(DRAM['capacity'] * 1024) + 20)

    return '0b' + str('0' * (bit_length - address_length) + bit_stream if bit_length > address_length else bit_stream[-bit_length:])


def read_memory(path):
    """Reads memory stuff from path file

    Parameters
    path: str
        file where the memory stuff is stored
    """

    with open(path, 'r') as memory:
        # read line by line the given file and split the
        # line in order to get the words
        for line in [line.split() for line in memory]:
            # treat data
            mode = line[0]
            address = bit_transform(line[1])
            now = line[2]
            MEMORY_CONTENT.append([mode,address,now])

    memory.closed


def read_specs(path='specs.yml'):
    dram = None
    with open(path, 'r') as specs:
        data = load(specs)
        # we expect just one dram item in file
        dram = [data[item] for item in data][0]

    specs.close
    return dram


if __name__ == '__main__':
    check_params()
    read_memory('memory_content.txt')
    if ok_specs():
        print("Memory content: {mc}\nDRAM {d}".format(mc=MEMORY_CONTENT, d=DRAM))
    else:
        chips_capacity = DRAM['chips']['number'] * DRAM['chips']['capacity']
        exit("ERROR: Chips capacity ({c}MB) not compatible with DRAM capacity ({d}GB)".format(c=chips_capacity, d=DRAM['capacity']))
