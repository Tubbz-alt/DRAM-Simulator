#!/usr/bin/python3

from os.path import exists
from os import remove
from time import sleep
from random import choice


filename = 'memory_content.txt'

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
    
    if not exists(filename):
        print("Creating memory file")
        with open(filename, 'w') as f:
            f.write(random_line)
        f.close
    
    # signal
    if exists('signal'):
        print("Deleting signal file")
        remove('signal')