#!/usr/bin/python3

class Chip(object):
    def __init__(self, capacity=0, rows=2, columns=2, banks=1):
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
    def capacity(self):
        return self.__capacity


    @capacity.setter
    def capacity(self, value):
        self.__capacity = positive(value)

    @property
    def rows(self):
        doc = "The rows."
        return self.__rows

    @rows.setter
    def rows(self, value):
        self.__rows = positive(pair(value))


    @property
    def columns(self):
        doc = "The columns."
        return self.__columns

    @columns.setter
    def columns(self, value):
        self.__columns = positive(pair(value))


    @property
    def banks(self):
        doc = "The banks property."
        return self.__banks

    @banks.setter
    def banks(self, value):
        self.__banks = positive(value)

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


