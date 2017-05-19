DRAM Simulator
===

This is a simulator of a dynamic random-access memory (DRAM) for the [simplescalar simulator](http://www.simplescalar.com/).

## Specs
The simulator has a file with specs definition. The file must follow the next structure:

```
dram:
    capacity: 1
    clock: 4
    chips:
        number: 2
        banks: 16
        rows: 1000
        columns: 32000
        capacity: 512
    times:
        RP: 1
        RCD: 1
        CL: 1
    wait:
        latency: 0
        bus_free: 0
```
_You can find this example in `specs.yml`._

To execute the simulator with a diferent specs file use `$ python dram.py <path>`


### Restrictions
A lot.
* The `capacity` of the DRAM must be expressed in GB
* The `clock` of the DRAM must expressed in __processor clock cycles__
* The `chips[capacity]` must be expressed in MB
* All of the `times` must be expressed in __DRAM clock cycles__
* The `DRAM[capacity]` must be equal to `chips[capacity]` * `chips[number]`. This is the chips capacity per number of chips equals the total capacity of the DRAM.
* The `chips[capacity]` in Bytes must be equal to the number of `chips[rows]` * `chips[banks]` * `chips[columns]` expressed in Bytes.
* All given valuen must be positive and all `DRAM[chips]` values must be pair


## Usage
To use this DRAM simulator as a simulator for the simplescalar we must run the `dram.py` script in one process and another process should be the simplescalar itself.
The simplescalar simulator will do its task (execute tests or benchmarks) and will write into a file called 'memory_content.txt' the next structure:
```
block_size mode address now_time
```
The dram script will process that data and return to simplescalar a 'signal' file with the total time of transfer time, latency time and wait of the simulated DRAM according to the given information by 'memory_content.txt'. 
simplescalar will acknowledge the 'signal' file and continue writing into 'memory_content.txt' more data.
After every file reading both programs delete the file they were reading from, simplescalar deletes signal and creates a memory_content.txt file every time and the dram script delete memory_content.txt and creates a signal file every time.