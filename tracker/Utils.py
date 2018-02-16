import os

def reverse_strchr(characters):
    temp = characters[::-1]
    idx = temp.find("/")
    temp = temp[0:idx]
    return temp[::-1]

def read_all_contents(file_path):
    with open(file_path, 'r') as fp:
        return fp.read()

def new_write(path, datalist):
    buf = ''
    for data in datalist: buf += data + "\n"
    with open(path, 'w') as fp:
        fp.write(buf)

def getParseFunction(codeline):
    idx = codeline.replace("\n", "").rfind(" ")
    return codeline[idx + 1:]
