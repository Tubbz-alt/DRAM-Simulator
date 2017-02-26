DRAM Simulator
===

This is a simulator of a Dynamic random-access memory (DRAM) for the [simplescalar simulator](http://www.simplescalar.com/).

## Specs
The simulator can have a YAML file (a file with `.yml` extension) as specs definition. The file must follow the next structure:

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
```
_You can find this example in `specs.yml`._

To execute the simulator with a specs file use `$ python dram.py specs.yml`.

The simulator can also have terminal arguments as DRAM values following the next structure:
```
$ python dram.py <dram_capacity> <number_chips> <chip_capacity> <rows> <columns> <banks>
    <dram_capacity>: (int) Total capacity of the DRAM expressed in GB
    <chip_number>: (int) Number of chips of DRAM 
    <chip_capacity>: (int) Capacity of the chip expressed in MB
    <rows>: (int) Row number of the chip
    <columns>: (int) Column number of the chip
    <banks>: (int) Banks number of the chip
```

### Restrictions
A lot.
* The `capacity` of the DRAM must be expressed in GB
* The `clock` of the DRAM must expressed in __processor clock cycles__
* The `chips[capacity]` must be expressed in MB
* All of the `times` must be expressed in __DRAM clock cycles__
* The `DRAM[capacity]` must be equal to `chips[capacity]` * `chips[number]`. This is the chips capacity per number of chips equals the total capacity of the DRAM.
* The `chips[capacity]` in Bytes must be equal to the number of `chips[rows]` * `chips[banks]` * `chips[columns]` expressed in Bytes.
* All given valuen must be positive and all `DRAM[chips]` values must be pair
