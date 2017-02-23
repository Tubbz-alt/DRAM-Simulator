DRAM Simulator
===


## Specs
The simulator is ready to have a YAML file (a file with `.yml` extension) as
specs definition. The file must follow the next structure:

```
dram_1:
    capacity: 1
    clock: 4
    chips:
        number: 2
        banks: 1
        rows: 1
        columns: 1
        capacity: 512
    times:
        RP: 1
        RCD: 1
        CL: 1
```
_You can find this example in `specs.yml`._

### Restrictions
* The `capacity` of the DRAM must be expressed in GB
* The `clock` of the DRAM must expressed in clock cycles
* The `chips[capacity]` must be expressed in MB
* All of the `times` must be expressed in DRAM clock cycles

