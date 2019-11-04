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
__todo__ = '* set-up to use the argument module'

from sys import argv
import chunks

stop = b'\xFF\xFF'

def compress_78(path, output_path=None):
    if output_path is None: output_path = path + '.s78'

    input_file = chunks.read(path, 1, 'rb')


    with open(output_path, 'xb') as output_file:
        stack = ['']
        symbol = bytes()
        while True:
            # grow symbol by one character from the input file
            try:
                symbol += next(input_file)
            except StopIteration:
                if len(symbol) != 0:
                    output_file.write(bytes((stack.index(symbol),)))
                break

            # if the symbol is a single character not in the stack
            if len(symbol) == 1 and symbol not in stack:
                stack.append(symbol)
                output_file.write(b'\x00' + symbol)
                symbol = bytes()

            # if the symbol is line not in the stack
            elif symbol not in stack:
                position = stack.index(symbol[:-1])
                if position < 255:
                    stack.append(symbol)
                    block = bytes((position, symbol[-1]))
                    output_file.write(block)
                    symbol = bytes()
                else:
                    if len(symbol) > 2:
                        position = bytes((stack.index(symbol[:-2]),))
                        output_file.write(position + stop)
                    hold = bytes((symbol[-2],))
                    stack = ['', hold]
                    output_file.write(b'\x00' + hold)
                    symbol = bytes((symbol[-1],))
                    if symbol != hold:
                        stack.append(symbol)
                        output_file.write(b'\x00' + symbol)
                        symbol = bytes()


def decompress_78(path, output_path=False):
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
        compress_78(path, output_path)
    else:
        print(__doc__)

        # if ends in ffff, it's the old version of decompress
