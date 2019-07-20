#! /usr/bin/env python3

# Shitty LZ78
def compress_78(data):
	data = data.decode('latin-1')
	start = b'\x00\x00'
	stop = b'\xFF\xFF'
	stack = ['']
	output = bytearray(start)
	i = 0
	size = len(data)
	chunks = 1
	while True:
		w = 1
		symbol = str(data[i])
		while symbol in stack and i + w <= size:  # <= so that things close to the end of a block get indexed correctly
			symbol = data[i:i+w]
			w += 1
		glyph = symbol[-1]
		if len(symbol) == 1:
			i += 1
			if glyph not in stack:
				output += bytearray((0, ord(glyph)))
				stack.append(glyph)
			else:
				idx = stack.index(glyph)
				output += bytearray((idx, 0))
		else:
			lookup = symbol[:-1]
			idx = stack.index(lookup)
			if idx < 255:
				i += w - 1
				output += bytearray((idx, ord(glyph)))
				stack.append(symbol)
			else:
				i += 1
				glyph = symbol[0]
				stack = ['', glyph]
				output += stop + start + bytearray((0, ord(glyph)))
				chunks += 1
		if i >= size:
			output += stop
			break
	print('{0}%'.format(round(len(output)/size * 100, 2)))
	print('{0} data chunks'.format(chunks))
	return output


def decompress_78(data):
	assert data[:2] == b'\x00\x00', 'This may not have been compressed with this software - expansion halted'
	output = bytearray()
	frames = data[0:-2:2]  # -2 to drop the ending \xFF to reduce code needed for .split replacement
	glyphs = data[1:-2:2]  # -2 to drop the ending \xFF to reduce code needed for .split replacement
	size = len(frames)
	i = 1
	while i < size:
		current_frame_content = frames[i]
		assert current_frame_content != i, 'POTENTIAL ZIP BOMB - EXPANSION HALTED'
		if current_frame_content == 255:  # this is to replace using .split on the data, which caused issues with certain patterns
			frames = frames[i+1:]
			glyphs = glyphs[i+1:]
			size = len(frames)
			i = 1
			continue
		elif current_frame_content == 0:
			output.append(glyphs[i])
		else:
			work = bytearray()
			# if glyphs[i] != 0:
			if i + 1 != size or (i + 1 == size and glyphs[i] != 0):  # this is to catch 0-glyphs that aren't at the end of a block
				work.append(glyphs[i])
			pointer = i
			while frames[pointer] != 0:  # add next glyph
				# issue with multiple zero reconstruction resolved
				pointer = frames[pointer]
				work.append(glyphs[pointer])
			output += work[::-1]
		i += 1
	return bytes(output)


if __name__ == '__main__':
	# TODO: use sys.stdin to accept from pipe?
	# clean up args, maybe even use the args library?
	# redo the open to read files in as chunks, write/append as chunks
	from sys import argv
	with open(argv[-2], 'rb') as input:
		data = input.read()
	output = open(argv[-1],'wb')
	if '-d' in argv:
		output.write(decompress_78(data))
	elif '-c' in argv:
		output.write(compress_78(data))
	else:
		print('<(-c)ompress | (-d)ecompress> <input path> <output path>')
	output.close()
