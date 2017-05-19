#!/usr/bin/python3
from Chip import *


def load_specs(path='specs.yml'):
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
        
    from yaml import load
    
    
    #load specs from file
    dram = None
    with open(path, 'r') as specs:
        data = load(specs)
        #we expect just one dram item in file
        dram = [data[item] for item in data][0]
    specs.close
    
    if not dram:
        raise Exception('Something went wrong reading DRAM specs')
    
    DRAM = {}
    DRAM.update(dram)

    #check if the DRAM has a proper specification
    if not positive_integers(DRAM['chips'].values()):
        raise Exception('Something in the chip specification is wrong')
        
    #check if DRAM has proper specification
    specs = list(DRAM['times'].values())
    specs.append(DRAM['clock'])
    if not positive_integers(specs):
        return Exception('Something in the DRAM specification is wrong')
        
    DC = DRAM['chips']
    chips_capacity = DC['number'] * DC['capacity']
    #for the total chip capacity divide by 1024 to convert to GB
    if (DRAM['capacity'] != chips_capacity/1024):
        raise Exception('Chips capacity ({c}MB) not compatible with DRAM capacity ({d}GB)'.format(c=chips_capacity, d=DRAM['capacity']))
    
    """
    check if the given specs for the chip are correct for total capacity of chip
        Pass chip capacity to KB by multiplying 1000 to MB 
        and pass from Bytes to KB dividing the product of rows, banks and columns by 1000
    """
    if (DC['capacity'] * 1000 != ((DC['rows'] * DC['banks'] * DC['columns']) / 1000)):
        raise Exception('Chips capacity ({c}MB) not compatible with chip specs ({cs})'.format(c=chips_capacity, cs=DC))
    
    #create chips
    chips = []
    for _ in range(DC['number']):
        chips.append(Chip(DC['capacity'], DC['rows'], DC['columns'], DC['banks']))
    
    return DRAM, chips, DRAM['times'], DRAM['wait']


if __name__ == '__main__':
    from sys import argv
    
    filename = argv[1] if len(argv) > 1 else 'specs.yml'
    load_specs(filename)

