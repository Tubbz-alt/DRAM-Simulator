#!/usr/bin/python3
from sys import exit
from statistics import *
from load_specs import *
from read_memory import *
from math import log2, ceil


def bit_reading(dram_chips, address):
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
    
    #log2([row,chip,bank,column])
    rcbc = list(map(lambda x: ceil(log2(x)), [dram_chips['rows'], dram_chips['number'], dram_chips['banks'], dram_chips['columns']]))
    
    #bit stream
    bit_stream = address[2:] #remove 2 first characters
    
    #now corresponding bits for [row,chip,bank,columns] (rcbc)
    bits = []
    for e in rcbc:
        #following the MSB strategy
        bits.append(bit_stream[:e]) #get the first corresponding bits
        bit_stream = bit_stream[e:] #update the list, get the remainings
    
    #transform list from binary to integer and return it unpacked
    return list(map(lambda x: int(x,2), bits))


def bit_transform(decimal_stream, capacity):
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
    bit_length = int(log2(capacity * 1024) + 20)
    
    return_stream = bit_stream[-bit_length:]
    if bit_length > address_length:
        return_stream = '0' * (bit_length - address_length) + bit_stream 
    
    return '0b' + str(return_stream)


if __name__ == '__main__':
    
    DRAM, chips, times, wait = load_specs()
    processor_clock = DRAM['clock'] #for further time transformations
    
    try:
        while True:
            block_size, mode, address, now_time = read_memory()
            
            address = bit_transform(address, DRAM['capacity'])

            #check timings
            wait_time = 0
            if now_time < wait['bus_free']:
                #this time is already in clock cycles
                wait_time = wait['bus_free'] - now_time
                
            #retrieve indexes
            i_row,i_chip,i_bank,i_column = bit_reading(DRAM['chips'], address)
            
            #access selected chip
            chip = chips[i_chip]
            #access selected bank
            bank = chip.banks[i_bank]
            #access selected row
            row = bank[i_row]

            #calculate timings
            if row:
                #same row
                wait['latency'] = times['CL']
                #it means we have a page-hit
                STATISTICS['page_hits'] += 1
            else:
                #use any(): returns true if any value is true
                if any(bank):
                    #open row
                    wait['latency'] = (times['RCD'] + times['CL'] + times['RP'])
                    #page miss
                    STATISTICS['page_misses'] += 1
                else:
                    #firs access
                    wait['latency'] = (times['RCD'] + times['CL'])
            
            #close all rows except selected for next iteration
            chip.update(i_bank, i_row)

            #calculate timings
            latency_time = wait['latency'] * processor_clock
            
            #block size / 8 = how many clock needed for dram
            transfer_time = (block_size / 8) * processor_clock
            total_time = sum([wait_time, latency_time, transfer_time])
            
            #check the mode, if we are writing we need to add a new time
            if mode == 'w':
                total_time += (times['WR'] * processor_clock)
                STATISTICS['write'] += 1
            
            #update bus free time
            wait['bus_free'] = now_time + total_time
            
            update_statistics(total_time, wait_time, latency_time, transfer_time)
            
            #write signal file with the total_time
            with open('signal','w') as s:
                s.write(str(total_time))
            s.close

    except KeyboardInterrupt:
        print('Execution was manually halted')
    except Exception as e:
        print(e)
    finally:
        write_statistics()
        exit()

