#!/usr/bin/python3

class Chip(object):
    def __init__(self, capacity, rows, columns, banks):
        self.__capacity = positive(capacity)
        self.__rows = positive(pair(rows))
        self.__columns = positive(pair(columns))
        self.__num_banks = banks
        self.__banks = [[False for i in range(self.__rows)] for i in range(banks)] 


    def __repr__(self):
        return ("Capacity: {capacity}MB\n"
                "Rows: {rows} \n"
                "Columns: {columns} \n"
                "Banks: {banks} \n".format(
                    capacity = self.__capacity,
                    rows = self.__rows,
                    banks = self.__banks,
                    columns = self.__columns
                ))


    @property
    def banks(self):
        return self.__banks


    def update(self,bank,row):
        self.__banks = [[False for i in range(self.__rows)] for i in range(self.__num_banks)]
        self.__banks[bank][row] = True


def positive(value):
    if value < 0:
        raise ValueError("Value must be positive")
    return value


def pair(value):
    if value % 2 != 0:
        raise ValueError("Value must be pair")
    return value

