#!/usr/bin/python3


from yaml import load, dump

with open('specs.yml', 'r') as stream:
    data = load(stream)
    print(data)
