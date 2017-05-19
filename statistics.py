#!/usr/bin/python3


STATISTICS = {
    'num_access': 0,
    'total': 0,
    'wait': 0,
    'latency': 0,
    'transfer': 0,
    'write': 0,
    'page_hits': 0,
    'page_misses': 0,
    }


def update_statistics(total, wait, latency, transfer):
    """Updates STATISTICS dictionary with the given times
    
    Parameters:
    The times
    """
    #account the access
    STATISTICS['num_access'] += 1
    #update the statistics values
    STATISTICS['total'] += total
    STATISTICS['wait'] += wait
    STATISTICS['latency'] += latency
    STATISTICS['transfer'] += transfer


def write_statistics(filename='results.txt'):
    
    if any(STATISTICS.values()):
        try:
            num_access = STATISTICS['num_access']
            
            #average values
            STATISTICS['wait'] /= num_access
            STATISTICS['latency'] /= num_access
            STATISTICS['transfer'] /= num_access
            STATISTICS['total'] /= num_access
            
            aux = STATISTICS['page_hits'] + STATISTICS['page_misses']
            #open page hit probability = open page hits / (open page hits + open page misses)
            p_page_hit = STATISTICS['page_hits'] / aux
            #open page miss probability = open page misses / (open page hits + open page misses)
            p_page_miss = STATISTICS['page_misses'] / aux
            
            with open(filename,'w') as s:
                for key, value in STATISTICS.items():
                    s.write(key + ": " + str(value) + "\n")
                s.write("P(page hit): " + str(p_page_hit) + "\n")
                s.write("P(page miss): " + str(p_page_miss) + "\n")
            s.close
        except ZeroDivisionError as z:
            print("Statistics error ({}): Some values were not ready".format(z))

