#!/usr/bin/python3
"""
Simulates writings from simplescalar to the memory content file

Waits for dram simulator to delete the memory file.
Uses backup_memory.txt file to get random lines that are true acceses from
simplescalar and writes it to a file.
Finally reads signal file and deletes it.

This process is the same followed between simplescalar and the dram simulator
"""
from os.path import exists
from os import remove, argv
from time import sleep
from random import choice


filename = 'memory_content.txt'
if len(argv) > 1:
    filename = argv[1]

try:
    while True:
        while exists(filename):
            print("Wait for it...")
            sleep(1)
            
        print("Read random line from backup file")
        random_line = ""
        with open('backup_memory.txt', 'r') as memory:
            # read line by line the given file and split the
            # line in order to get the words
            aux = choice([line.split() for line in memory])
            # pass the elements of the list to the line
            for a in aux:
                random_line += a+" "
            random_line+"\n"
        memory.close
        
        #put line into memory file
        if not exists(filename):
            print("Creating memory file")
            with open(filename, 'w') as f:
                f.write(random_line)
            f.close
        
        # signal
        if exists('signal'):
            with open('signal', 'r') as f:
                print("Total wait it",f.read())
            f.close
            print("Deleting signal file")
            remove('signal')
except KeyboardInterrupt:
    create_memory(filename,"HALT\n")

