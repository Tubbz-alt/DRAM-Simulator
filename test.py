#!/usr/bin/env python

from Chip import *
from dram import *

#dram testing
read_memory('memory_content.txt')
print("Memory content: {mc}\n".format(mc=MEMORY_CONTENT))
print("Total memory of DRAM: {m}MB\n".format(m=DRAM['capacity']))

check_params() # for user input

print("DRAM {d}\n".format(d=DRAM))

#chips testing
capacities = [1024, 512]
for c in capacities:
    my_chip = Chip(capacity=c)
    print(my_chip)

    #play around with properties of chip
    my_chip.rows = 2
    my_chip.banks = 100
    my_chip.columns = 8

    print(my_chip)


