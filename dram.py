#!/usr/bin/python3

from sys import argv, exit
from yaml import load
from math import log2, ceil
from os import remove
from time import sleep
from Chip import *


# DRAM specs
TIMES = {
    'RP': 1, # row precharge (closing)
    'RCD': 1, # row to column delay
    'CL': 1 # column latency
}

# wait time
WAIT = {
    'latency': 0,
    'bus_free': 0, # initially 0, memory bus is free
}

# testing DRAM
DRAM = {
    'capacity': 1,
    'clock': 4,
    'chips': {
        'number': 2,
        'capacity': 512, #MB
        'rows': 1000,
        'banks': 16,
        'columns': 32000 # Bytes
        },
    'times': TIMES,
}

# store the memory content provided by the simplescalar
MEMORY_CONTENT = []


def check_params(DRAM=DRAM):
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

    elif num_args == 2 and argv[1].split('.')[-1] == 'yml':
        DRAM.clear()
        DRAM.update(read_specs())

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

    def positive_integers(elements):
        """Returns if all given values of a list are of integer type

        maps a list of elements to its element's type: [type, type, ...]
        the filter the mapped list to get if every element is equal to type(1) (which is int)
        if the length of the filter type it's equal to length of the first list, then
        all elements are integers

        Parameters
        elements: list
            list of elements to check its integerity

        Return
        boolean: All values passed by params are integer
        """
        types = list(map(lambda x: type(x) is type(1) and x > 0, elements))
        return len(list(filter(lambda x: x is True, types))) == len(types)


    message = None

    # check if the DRAM has a proper specification
    if not positive_integers(DRAM['chips'].values()):
        message = "ERROR: Something in the chip specification is wrong"

    # check if DRAM has proper specification
    specs = list(DRAM['times'].values())
    specs.append(DRAM['clock'])
    if not positive_integers(specs):
        message = "ERROR: Something in the DRAM specification is wrong"

    DC = DRAM['chips']
    chips_capacity = DC['number'] * DC['capacity']
    # for the total chip capacity divide by 1024 to convert to GB
    if (DRAM['capacity'] != chips_capacity/1024):
        message = "ERROR: Chips capacity ({c}MB) not compatible with DRAM capacity ({d}GB)".format(c=chips_capacity, d=DRAM['capacity'])
    
    """
    check if the given specs for the chip are correct for total capacity of chip
        Pass chip capacity to KB by multiplying 1000 to MB 
        and pass from Bytes to KB dividing the product of rows, banks and columns by 1000
    """
    if (DC['capacity'] * 1000 != ((DC['rows'] * DC['banks'] * DC['columns']) / 1000)):
        message = "ERROR: Chips capacity ({c}MB) not compatible with chip specs ({cs})".format(c=chips_capacity, cs=DC)

    return message is None, message


def bit_reading():
    """Returns the selected row, chip, bank and column from the 
    MEMORY_CONTENT in integer values
    
    Gets how many bits are needed for represent the chip entities 
        (row, chip number, banks and columns)
    Selects that quantity in order from the MEMORY_CONTENT content, 
    given us the bits needed for represent the entities and, finally, 
    returns those values in integers in an ordered list for further treatment
    
    Returns
    list: integer values from [row,chip,bank,column]
    """
    
    # bit stream
    bit_stream = MEMORY_CONTENT[1][2:] # remove 2 first characters
    
    # log2([row,chip,bank,column])
    dc = DRAM['chips']
    rcbc = list(map(lambda x: ceil(log2(x)), [dc['rows'],dc['number'],dc['banks'],dc['columns']] ))
    
    # now corresponding bits for [row,chip,bank,columns]
    bits = []
    for e in rcbc:
        # following the MSB strategy
        bits.append(bit_stream[:e]) # get the first corresponding bits
        bit_stream = bit_stream[e:] # update the list, get the remainings
    
    print("row: {0}\nchip: {1}\nbank: {2}\ncolumn: {3}\n".format(bits[0],bits[1],bits[2],bits[3]))
    # transform list from binary to integer and return it unpacked
    return list(map(lambda x: int(x,2), bits))


def read_memory(path):
    """Reads memory stuff from path file

    Parameters
    path: str
        file where the memory stuff is stored
    """
    
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


    try:
        with open(path, 'r') as memory:
            # read line by line the given file and split the
            # line in order to get the words
            for line in [line.split() for line in memory]:
                # treat data
                mode = line[0]
                address = bit_transform(line[1])
                now = line[2]
                MEMORY_CONTENT.clear()
                MEMORY_CONTENT.append(mode)
                MEMORY_CONTENT.append(address)
                MEMORY_CONTENT.append(now)

        memory.closed
        # delete after reading
        remove(path)
    except FileNotFoundError:
        print("Waiting for file to be created")
        sleep(1)
        read_memory(path)


def read_specs(path='specs.yml'):
    dram = None
    with open(path, 'r') as specs:
        data = load(specs)
        # we expect just one dram item in file
        dram = [data[item] for item in data][0]

    specs.close
    return dram


def signal(total_wait):
    """Makes a signal for the simulator
    
    Creates a file that indicates the total time for the last access
    """
    with open('signal','w') as s:
        s.write(str(total_wait))
    s.close


if __name__ == '__main__':
    
    check_params()
    ok_condition, message = ok_specs()
    if ok_condition:
        print("Creating DRAM {d}\n".format(d=DRAM))
        # create chips
        chips = []
        DC = DRAM['chips']
        for _ in range(DC['number']):
            chips.append(Chip(DC['capacity'],DC['rows'],DC['columns'],DC['banks']))
        
        while True:
            read_memory('memory_content.txt')
            print("\n\n=======================\n")
            print("Memory content: {mc}\n".format(mc=MEMORY_CONTENT))

            # check timings
            wait_time = 0
            now_time = int(MEMORY_CONTENT[2])
            if now_time < WAIT['bus_free']:
                wait_time =  WAIT['bus_free'] - now_time
                
            print("Last now: {}\nNow: {}\nWait time will be: {}\n".format(WAIT['bus_free'],now_time,wait_time))
            
            # retrieve indexes
            i_row,i_chip,i_bank,i_column = bit_reading()
            print("Selected row: {0}\nSelected chip: {1}\nSelected bank: {2}\nSelected column: {3}\n".format(i_row,i_chip,i_bank,i_column))
            
            # access selected chip
            chip = chips[i_chip]
            # access selected bank
            bank = chip.banks[i_bank]
            # access selected row
            row = bank[i_row]
            
            # calculate timings
            if row:
                print("Same row")
                WAIT['latency'] += TIMES['CL']
            else:
                # use any(): returns true if any value is true
                if any(bank):
                    print("Open row")
                    WAIT['latency'] += sum(TIMES.values())
                else:
                    print("First access")
                    WAIT['latency'] += (TIMES['RCD'] + TIMES['CL'])
                bank[i_row] = True
            
            total_time = sum([wait_time,WAIT['latency']])
            # update bus free time
            WAIT['bus_free'] = now_time + total_time
            
            # total time must be expressed in DRAM clocks
            total_time *= DRAM['clock']
            print("\nWait times: {}\nTotal time: {}\n".format(wait_time,total_time))
            
            # write signal file with the total_time
            signal(total_time)
            
    else:
        exit(message)
