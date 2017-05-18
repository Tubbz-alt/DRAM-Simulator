#!/usr/bin/python3
from sys import argv, exit
from yaml import load
from math import log2, ceil
from os import remove
from os.path import isfile
from time import sleep
from Chip import *


SLEEP = 1000 #useconds


#DRAM specs
TIMES = {
    'RP': 1, #row precharge (closing)
    'RCD': 1, #row to column delay
    'CL': 1, #column latency
    'WR': 1 #write recovery time for writing mode
    }

#wait time
WAIT = {
    'latency': 0,
    'bus_free': 0, #initially 0, memory bus is free
    }

#testing DRAM
DRAM = {
    'capacity': 1,
    'clock': 4,
    'chips': {
        'number': 2,
        'capacity': 512, #MB
        'rows': 1000,
        'banks': 16,
        'columns': 32000 #Bytes
        },
    'times': TIMES,
    }

#store the memory content provided by the simplescalar
MEMORY_CONTENT = []

#for statistics purposes. Average times
STATISTICS = {
    'num_access': 0,
    'total': 0,
    'wait': 0,
    'latency': 0,
    'transfer': 0,
    'write': 0,
    'page_hits': 0,
    'page_misses': 0,
    }


usleep = lambda x: sleep(x/1000000.0)


def check_params(DRAM=DRAM):
    """
    #./dram <dram_capacity> <chip number> <chip_capacity> <rows> <columns> <banks>
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
        #incorrect value, or show help
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

    #check if the DRAM has a proper specification
    if not positive_integers(DRAM['chips'].values()):
        message = "ERROR: Something in the chip specification is wrong"
        
    #check if DRAM has proper specification
    specs = list(DRAM['times'].values())
    specs.append(DRAM['clock'])
    if not positive_integers(specs):
        message = "ERROR: Something in the DRAM specification is wrong"
        
    DC = DRAM['chips']
    chips_capacity = DC['number'] * DC['capacity']
    #for the total chip capacity divide by 1024 to convert to GB
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
    
    #bit stream
    bit_stream = MEMORY_CONTENT[2][2:] #remove 2 first characters
    
    #log2([row,chip,bank,column])
    dc = DRAM['chips']
    rcbc = list(map(lambda x: ceil(log2(x)), [dc['rows'],dc['number'],dc['banks'],dc['columns']] ))
    
    #now corresponding bits for [row,chip,bank,columns]
    bits = []
    for e in rcbc:
        #following the MSB strategy
        bits.append(bit_stream[:e]) #get the first corresponding bits
        bit_stream = bit_stream[e:] #update the list, get the remainings
    
    #print("row: {0}\nchip: {1}\nbank: {2}\ncolumn: {3}\n".format(bits[0],bits[1],bits[2],bits[3]))
    #transform list from binary to integer and return it unpacked
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
        
        #first, we need to transform it to a true bit stream
        #and remove '0b' from string in order to work better
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


    while not isfile(path):
        #print("..")
        usleep(SLEEP)

    halt = False
    with open(path, 'r') as memory:
        #read line by line the given file and split the
        #line in order to get the words
        for line in [line.split() for line in memory]:
            
            if line[0] != 'HALT':
                MEMORY_CONTENT.clear()
                MEMORY_CONTENT.append(int(line[0])) #block size
                MEMORY_CONTENT.append(line[1]) #mode
                MEMORY_CONTENT.append(bit_transform(line[2])) #address
                MEMORY_CONTENT.append(int(line[3])) #now
            else:
                halt = True
                
    memory.closed
    #delete after reading
    remove(path)
    
    #halt condition means the simulation is over
    if halt:
        #check if the statistics dictionary is ready
        if any(STATISTICS.values()):
            print_statistics()
            
        exit("HALT")
            

def read_specs(path='specs.yml'):
    dram = None
    with open(path, 'r') as specs:
        data = load(specs)
        #we expect just one dram item in file
        dram = [data[item] for item in data][0]
        
    specs.close
    return dram


def update_statistics(total, wait, latency, transfer, STATISTICS=STATISTICS):
    """Updates STATISTICS dictionary with the given times
    
    Parameters:
    The times
    """
    #account the access
    STATISTICS['num_access'] += 1
    #update the statistics values
    STATISTICS['total'] += total
    STATISTICS['wait'] += wait
    STATISTICS['latency'] += latency
    STATISTICS['transfer'] += transfer


def print_statistics(STATISTICS=STATISTICS):
    
    num_access = STATISTICS['num_access']
    
    #average values
    STATISTICS['wait'] /= num_access
    STATISTICS['latency'] /= num_access
    STATISTICS['transfer'] /= num_access
    STATISTICS['total'] /= num_access
    
    aux = STATISTICS['page_hits'] + STATISTICS['page_misses']
    #open page hit probability = open page hits / (open page hits + open page misses)
    p_page_hit = STATISTICS['page_hits'] / aux
    #open page miss probability = open page misses / (open page hits + open page misses)
    p_page_miss = STATISTICS['page_misses'] / aux
    
    with open('statistics.txt','w') as s:
        for key, value in STATISTICS.items():
            s.write(key + ": " + str(value) + "\n")
        s.write("P(page hit): " + str(p_page_hit) + "\n")
        s.write("P(page miss): " + str(p_page_miss) + "\n")
    s.close


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
        #create chips
        chips = []
        DC = DRAM['chips']
        for _ in range(DC['number']):
            chips.append(Chip(DC['capacity'],DC['rows'],DC['columns'],DC['banks']))
        
        processor_clock = DRAM['clock'] #for further time transformations
        try:
            while True:
                read_memory('memory_content.txt')

                #check timings
                wait_time = 0
                now_time = MEMORY_CONTENT[3]
                if now_time < WAIT['bus_free']:
                    #this time is already in clock cycles
                    wait_time = WAIT['bus_free'] - now_time
                    
                #retrieve indexes
                i_row,i_chip,i_bank,i_column = bit_reading()
                
                #access selected chip
                chip = chips[i_chip]
                #access selected bank
                bank = chip.banks[i_bank]
                #access selected row
                row = bank[i_row]

                #calculate timings
                if row:
                    #print("Same row")
                    WAIT['latency'] = TIMES['CL']
                    #it means we have a page-hit
                    STATISTICS['page_hits'] += 1
                else:
                    #use any(): returns true if any value is true
                    if any(bank):
                        #print("Open row")
                        WAIT['latency'] = (TIMES['RCD'] + TIMES['CL'] + TIMES['RP'])
                        #page miss
                        STATISTICS['page_misses'] += 1
                    else:
                        #print("First access")
                        WAIT['latency'] = (TIMES['RCD'] + TIMES['CL'])
                
                #close all rows except selected for next iteration
                chip.update(i_bank, i_row)

                #calculate timings
                latency_time = WAIT['latency'] * processor_clock
                
                #block size / 8 = how many clock needed for dram
                transfer_time = (MEMORY_CONTENT[0] / 8) * processor_clock
                total_time = sum([wait_time,latency_time,transfer_time])
                
                #check the mode, if we are writing we need to add a new time
                if MEMORY_CONTENT[1] == 'w':
                    total_time += (TIMES['WR'] * processor_clock)
                    STATISTICS['write'] += 1
                
                #update bus free time
                WAIT['bus_free'] = now_time + total_time
                
                update_statistics(total_time, wait_time, latency_time, transfer_time)
                
                #write signal file with the total_time
                signal(total_time)

        except KeyboardInterrupt:
            if any(STATISTICS.values()):
                print_statistics()
            exit("Execution was manually halted")

    else:
        exit(message)
