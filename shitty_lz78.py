#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''shitty_lz78.py: A very bad implementation of the LZ78 algorithm.

Usage:  
shitty_lz78.py -(c|d) <path> <output_path>
-c(ompress):    Compresses the file at <path> to <output_path>.
                If <output_path> is not specified, the file will output
                to <path>.s78
-d(ecompress):  Decompresses the file at <path> to <output_path>.
                If <output_path> is not specified, the result will print
                to the console.
'''

__version__ = 'v1.0'
__author__ = 'rivard8490 at gmail.com'
__copyright__ = 'Copyright 2019'
'''TODO:
* set-up decompress to not freak out if 255 gets encoded at the end of a 
  block. Would need to make sure the next remnant doesn't start with 255
  and if it does - trim it and stick it on the end of the working chunk.
* implement a version flag
* add a "if file ends with \xFF\xFF: decompress with old formula"
* set-up a 16bit dictionary?
* set-up to use the argument module
'''

from sys import argv
import chunks

stop = b'\xFF\xFF'

def byter(value, size = 1):
    limit = int('ff' * size, 16)
    assert 0 <= value <= limit, '0 <= value <= {0}'.format(limit) 
    return value.to_bytes(size, 'big')


def compress(path, output_path=None):
    input_file = chunks.read(path, 1, 'rb')

    if output_path is None: 
        output_path = path + '.s78'

    with open(output_path, 'xb') as output_file:
        stack = ['']
        symbol = bytes()
        while True:
            # grow symbol by one character from the input file
            try:
                symbol += next(input_file)
            except StopIteration:
                if len(symbol) != 0:
                    output_file.write(stack.index(symbol).to_bytes(1, 'big'))
                break

            if symbol not in stack:
                if len(symbol) == 1:
                    stack.append(symbol)
                    output_file.write(b'\x00' + symbol)
                    symbol = bytes()

                else:
                    position = stack.index(symbol[:-1])
                    if position < 255:  # if continue w/ current block
                        stack.append(symbol)
                        block = bytes((position, symbol[-1]))
                        output_file.write(block)
                        symbol = bytes()

                    elif len(symbol) > 2:  # if new block, len symbol > 2
                        lead, stub = symbol[:-2], symbol[-2:]
                        position = stack.index(lead).to_bytes(1, 'big')
                        output_file.write(position + stop)

                        stub_a = stub[-2].to_bytes(1, 'big')
                        stub_b = stub[-1].to_bytes(1, 'big')

                        stack = ['', stub_a]
                        symbol = bytes()
                        output_file.write(b'\x00' + stub_a)
                        
                        if stub_a == stub_b:
                            output.write(b'\x01' + stub_b)
                        else:
                            stack.append(stub_b)
                            output_file.write(b'\x00' + stub_b)

                    else: # if new block, len symbol <= 2
                        stub_a = symbol[-2].to_bytes(1, 'big')
                        stub_b = symbol[-1].to_bytes(1, 'big')

                        if stack.index(stub_a) < 255:
                            position = stack.index(stub_a).to_bytes(1, 'big')
                            output_file.write(position + stop)
                            output_file.write(b'\x00' + stub_b)
                            stack = ['', stub_b]

                        else:
                            output_file.write(stop)
                            stack = ['', stub_a]
                            symbol = bytes()
                            output_file.write(b'\x00' + stub_a)
                            
                            if stub_a == stub_b:
                                output.write(b'\x01' + stub_b)
                            else:
                                stack.append(stub_b)
                                output_file.write(b'\x00' + stub_b)


def decompress(path, output_path=False):
    if output_path is not False: output_file = open(output_path, 'xb')

    input_file = chunks.read(path, 512, 'rb')
    block = next(input_file)

    while block != b'':
        output_buffer = bytes()

        while stop not in block:
            try:
                block += next(input_file)
            except StopIteration:
                break

        block = block.split(stop, 1)

        if len(block) == 1:
            work, block = block[0], bytes()
        else:
            work, block = block

        stack = tuple((tuple(work[i:i+2]) for i in range(0, len(work), 2)))

        for pair in stack:
            internal_buffer = bytes()

            if len(pair) == 2:
                lookup, glyph = pair
                if lookup == 0:
                    output_buffer += bytes((glyph,))
                else:
                    internal_buffer = bytes((glyph,))
                    while lookup != 0:
                        lookup, glyph = stack[lookup - 1]
                        internal_buffer += bytes((glyph,))

            else:  # half-tuple at end of stack
                lookup = pair[0]
                while lookup != 0:
                    lookup, glyph = stack[lookup - 1]
                    internal_buffer += bytes((glyph,))

            output_buffer += internal_buffer[::-1]

        if output_path is False:
            print(output_buffer, end='')
        else:
            output_file.write(output_buffer)


if __name__ == '__main__':
    if '-d' in argv:  # decompress
        pass
    elif '-c' in argv:  # compress
        compress(path, output_path)
    else:
        print(__doc__)
