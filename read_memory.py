#!/usr/bin/python3
class MemoryException(Exception):
    pass


def read_memory(path='memory_content.txt'):
    """Reads memory stuff from path file
    
    Parameters
    path: str
        file where the memory stuff is stored
    """
    from os import remove
    from os.path import isfile, getsize
    from time import sleep
    
    #wait for file to be ready (created and with content)
    usleep = lambda x: sleep(x/1000000.0)
    while not isfile(path) or getsize(path) == 0:
        # print("..")
        usleep(1000)
    
    #declare variables of memory content
    block_size = 0
    mode = ''
    address = ''
    now_time = 0
    #store the memory content provided by the simplescalar
    with open(path, 'r') as memory:
        #read line by line the given file and split the
        #line in order to get the words
        for line in [line.split() for line in memory]:
            
            if line[0] == 'HALT':
                raise MemoryException('HALT signal in memory content')
                
            block_size = int(line[0])
            mode = line[1]
            address = line[2]
            now_time = int(line[3])
                
    memory.closed
    #delete after reading
    remove(path)
    
    return block_size, mode, address, now_time


if __name__ == '__main__':
    print(read_memory())

