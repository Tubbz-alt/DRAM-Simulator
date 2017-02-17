#!/usr/bin/python3

from os.path import exists
from os import remove
from time import sleep


def create_file():
    print("Creating memory file")
    with open(filename, 'w') as f:
        f.write("r 536980608 51989\n")
    f.close

filename = 'memory_content.txt'

while True:
    while exists(filename):
        print("Wait for it...")
        sleep(1)
        
    if exists('signal') and not exists(filename):
        print("Deleting signal file")
        remove('signal')
        create_file()
    else:
        # bootstrap the thing
        create_file()        
