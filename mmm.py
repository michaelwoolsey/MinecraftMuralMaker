import os
from PIL import Image
import numpy as np
import sys
import getopt


def has_transparency(image):
	extrema = image.getextrema()
	try:
		if extrema[3][0] < 255:
			return True
	except IndexError:
		return True


def is_valid_block_from_name(name):
	if not name[-4:] == ".png":  # if image is not png
		return False
	if name[-8:-4] == "_top":
		if name[-12:-8] == "_log" or \
			"stem" in name:
			return True
		return False
	if name[-11:-4] == "_bottom":
		return False
	if name[-10:-4] == "_inner":
		return False
	if name[:5] == "grass":
		return False
	if name == "ERROR.png":
		return False
	return True


def remove_noncreative_blocks(name):
	if "bedrock" in name:
		return False
	return True


def remove_glowing_blocks(name):
	if "glowstone" in name or \
			"jack" in name or \
			"shrooml" in name:
		return False
	return True


def remove_crafting_blocks(name):
	if "crafting" in name or \
			"furnace" in name or \
			"smoker" in name or \
			"smith" in name or \
			"loom" in name or \
			"fletch" in name or \
			"drop" in name or \
			"dispen" in name or \
			"barrel" in name:
		return False
	return True


def remove_expensive_blocks(name):
	if "debris" in name or \
			"netherite" in name or \
			"diamond_b" in name or \
			"gilded_blackstone" in name or \
			"emerald_b" in name:
		return False
	return True


def remove_shulker_blocks(name):
	if "shulker" in name:
		return False
	return True


def remove_glazed_blocks(name):
	if "glazed" in name:
		return False
	return True


def remove_ugly_blocks(name):
	if "booksh" in name or \
			"tnt" in name or \
			"z_ore" in name or \
			"target" in name or \
			"piston" in name or \
			"carved" in name:
		return False
	return True


def remove_bee_blocks(name):
	if "bee" in name or \
		"honey" in name:
		return False
	return True


def remove_sidewaysfacing_blocks(name):
	if "log_top" in name or \
		"stem_top" in name or \
		"piston_top" in name:
		return False
	return True


def remove_ore_blocks(name):
	if "_ore" in name or \
		"debris" in name:
		return False
	return True


def is_valid_block_from_image(image):
	return image.height == image.width == 16


def get_avg_colour(image):
	return (int(round(np.mean(image.getdata(band=0)))),
		int(round(np.mean(image.getdata(band=1)))),
		int(round(np.mean(image.getdata(band=2)))))


#  https://stackoverflow.com/questions/29433243/convert-image-to-specific-palette-using-pil-without-dithering <3
def quantizetopalette(silf, palette, dither=False):
	"""Convert an RGB or L mode image to use a given P image's palette."""

	silf.load()

	# use palette from reference image
	palette.load()
	if palette.mode != "P":
		raise ValueError("bad mode for palette image")
	if silf.mode != "RGB" and silf.mode != "L":
		raise ValueError(
			"only RGB or L mode images can be quantized to a palette"
			)
	im = silf.im.convert("P", 1 if dither else 0, palette.im)
	# the 0 above means turn OFF dithering

	# Later versions of Pillow (4.x) rename _makeself to _new
	try:
		return silf._new(im)
	except AttributeError:
		return silf._makeself(im)


#  https://stackoverflow.com/questions/6169217/replace-console-output-in-python <3
def progress_bar(current, total, barLength=20, strprg="Progress"):
	percent = float(current) * 100 / total
	arrow = '-' * int(percent / 100 * barLength - 1) + '>'
	spaces = ' ' * (barLength - len(arrow))
	print('%s: [%s%s] %d %%                 ' % (strprg, arrow, spaces, percent), end='\r')

#  //////////////////////////////////////////////MAIN FUNCTION//////////////////////////////////////////////////////////
if __name__ == '__main__':

	LEN = 253
	HEIGHT = None

	# 		bits from left to right:
	# remove ore blocks
	# remove sideways facing logs
	# remove bee blocks (ex. beehives, honey blocks)
	# remove ugly blocks (ex. target block, bookshelf, tnt)
	# remove glazed terracotta
	# remove shulker boxes
	# remove expensive blocks (ex. netherite block, debris, diamond block)
	# remove crafting blocks (ex. furnaces)
	# remove glowing blocks (ex. glowstone)
	# remove creative exclusive blocks (ex. bedrock)
	block_removals = 0b0000000000
	# block_removals = 0b1111111111

	valid_blocks = []
	input_filepath = None
	dither = False

	test_img = Image.new(mode="RGB", size=(LEN*16, 32), color=(255, 255, 255))

	try:
		options, args = getopt.getopt(sys.argv[1:], "h:i:r:d", ["help", "remove="])
	except getopt.GetoptError:
		print("Usage: mmm.py -r <\"creative, glowing, crafting, expensive, shulker, glazed, ugly, bee, sideways, ore, all\">")
		exit(0)

	for opt, arg in options:

		if opt == "--help":
			print("\nWelcome to Minecraft Mural Maker! A tool made specifically for building murals in survival Minecraft\n\n"
				  "To use MMM, put an image called \'input.png\' in the working directory, or pass in a path to"
				  " an image with the -i argument\nOptionally you can define the height of the mural in blocks "
				  "with the optional argument -h <integer>\n\tNOTE: if you are working with large images, I would"
				  " advise using this argument as otherwise it will be a 1 to 1 conversion from pixel to block, which"
				  " will take a long time!\n"
				  "-d will dither the image, it may make the result look better, or it might make it worse!\n\n"
				  "Usage: mmm.py -r <\"creative, glowing, crafting, expensive, shulker, glazed, ugly, bee, sideways, ore, all\">\n"
				  "When passing in more than 1 argument, you must surround them with \"\", (ex. -r \"shulker, ore\")\n"
				  "What each option removes:\n"
				  "\tCreative: Bedrock\n"
				  "\tGlowing: Glowstone, Jack o' Lantern, Shroomlite\n"
				  "\tCrafting: Crafting Table, Furnace, Smoker, Blast Furnace, Smithing Table, Loom, Fletching Table, Dropper, Dispenser, Barrel\n"
				  "\tExpensive: Ancient Debris, Netherite Block, Diamond Block, Emerald Block, Gilded Blackstone\n"
				  "\tShulker: Shulker Boxes\n"
				  "\tGlazed: Glazed Terracotta\n"
				  "\tUgly: Bookshelf, TNT, Quartz Ore, Pistons, Target Block, Carved Pumpkin\n"
				  "\tBee: Beehives, Bee Nest, Honey Block\n"
				  "\tSideways: Tops of all Logs and top of Piston\n"
				  "\tOre: All Ore blocks and Ancient Debris\n"
				  "\tAll: All of the above")
			exit(1)
		elif opt == "-r":
			arg = arg.lower()
			if "creative" in arg:
				block_removals |= 0b1 << 0
			if "glowing" in arg:
				block_removals |= 0b1 << 1
			if "crafting" in arg:
				block_removals |= 0b1 << 2
			if "expensive" in arg:
				block_removals |= 0b1 << 3
			if "shulker" in arg:
				block_removals |= 0b1 << 4
			if "glazed" in arg:
				block_removals |= 0b1 << 5
			if "ugly" in arg:
				block_removals |= 0b1 << 6
			if "bee" in arg:
				block_removals |= 0b1 << 7
			if "sideways" in arg:
				block_removals |= 0b1 << 8
			if "ore" in arg:
				block_removals |= 0b1 << 9
			if "all" in arg:
				block_removals = -1
		elif opt == "-h":
			try:
				HEIGHT = int(arg)
			except TypeError:
				print("Invalid height entered, using image height\n")
		elif opt == "-i":
			input_filepath = arg
		elif opt == "-d":
			dither = True
	try:
		if input_filepath is not None:
			input_img = Image.open(input_filepath)
		else:
			input_img = Image.open("input.png")
	except:
		sys.stderr.write("There was no file called \'input.png\' in the working directory, or invalid file was passed in\n")
		exit()

	print("Starting...", end='\r')

	for subdir, dirs, files in os.walk(r'blocks'):  # for each texture
		for filename in files:
			filepath = subdir + os.sep + filename
			if is_valid_block_from_name(filename):
				texture = Image.open(filepath)
				if (texture.getbands() == ("R", "G", "B") or not has_transparency(texture)) and is_valid_block_from_image(texture) and \
						((block_removals & (0b1 << 0)) == 0 or (remove_noncreative_blocks(filepath))) and \
						((block_removals & (0b1 << 1)) == 0 or (remove_glowing_blocks(filepath))) and \
						((block_removals & (0b1 << 2)) == 0 or (remove_crafting_blocks(filepath))) and \
						((block_removals & (0b1 << 3)) == 0 or (remove_expensive_blocks(filepath))) and \
						((block_removals & (0b1 << 4)) == 0 or (remove_shulker_blocks(filepath))) and \
						((block_removals & (0b1 << 5)) == 0 or (remove_glazed_blocks(filepath))) and \
						((block_removals & (0b1 << 6)) == 0 or (remove_ugly_blocks(filepath))) and \
						((block_removals & (0b1 << 7)) == 0 or (remove_bee_blocks(filepath))) and \
						((block_removals & (0b1 << 8)) == 0 or (remove_sidewaysfacing_blocks(filepath))) and \
						((block_removals & (0b1 << 9)) == 0 or (remove_ore_blocks(filepath))):
					valid_blocks.append(filepath)
				texture.close()  # memory management :)
	valid_blocks.sort()
	blocks = []
	palettedata = []
	for index, img in enumerate(valid_blocks):
		texture = Image.open(img)
		avg_col = get_avg_colour(texture)
		block = {
			"name": img[7:-4],
			"colour": avg_col,
			"count": 0
		}
		blocks.append(block)
		palettedata.append(avg_col[0])
		palettedata.append(avg_col[1])
		palettedata.append(avg_col[2])

	print("Done Texture Parsing       ", end='\r')

	if HEIGHT is not None:
		input_img = input_img.resize((input_img.width * HEIGHT // input_img.height, HEIGHT), 5)
	# elif input_img.height > MAX_SZ:
	# 	input_img = input_img.resize((input_img.width * MAX_SZ // input_img.height, MAX_SZ), 5)

	def input_has_transparent_pixels(image):
		extrema = image.getextrema()
		try:
			if extrema[3][0] == 0:
				return True
		except IndexError:
			return False

	transparency_img = None  # acts as mask for transparent pixels
	if input_has_transparent_pixels(input_img):
		transparency_img = Image.new("RGBA", input_img.size, (255, 255, 255, 0))
		for y in range(input_img.height):
			progress_bar(y, input_img.height, strprg="Solving Transparency")
			for x in range(input_img.width):
				px = input_img.getpixel((x, y))
				if px[3] == 0:  # transparent px
					transparency_img.putpixel((x, y), (0, 0, 0, 255))

	input_img = input_img.convert("RGB")
	palimage = Image.new('P', (1, 1))
	palimage.putpalette(palettedata)
	newimage = quantizetopalette(input_img, palimage, dither=dither)
	print("one Quantizing         ", end='\r')

	newimage = newimage.convert("RGB").convert("RGBA")
	if transparency_img is not None:
		newimage.paste((0,0,0,0), (0,0), mask=transparency_img)

	def get_col_name(col_):
		if col_[3] == 0:
			return "TSP"
		for item in blocks:
			if item["colour"] == col_[0:3]:
				return item["name"]
		return "snow"  # error case, could not find

	def increment_block_count(col):
		if col[3] == 0:  # transparent
			return
		for item in blocks:
			if item["colour"] == col[0:3]:
				item["count"] += 1
				return
		for item in blocks:
			if item["name"] == "snow":
				item["count"] += 1  # error case, could not find
				return
		print("something bad has occurred", end="\r")

	final_img = Image.new("RGBA", (newimage.width * 16, newimage.height * 16), (0, 0, 0, 0))
	for y in range(newimage.height): #use getcolors ?
		progress_bar(y, newimage.height, strprg="Making into blocks")
		for x in range(newimage.width):
			px = newimage.getpixel((x, y))
			str2 = get_col_name(px)
			increment_block_count(px)
			if str2 == "TSP":
				pass
			else:
				# if str2 == "ERROR":
				# 	# newimage.putpixel((x, y), (249, 254, 254))
				# 	str2 = "snow"
				txt = Image.open("blocks" + os.sep + str2 + ".png")
				final_img.paste(txt, (x*16, y*16))
	progress_bar(newimage.height, newimage.height, strprg="Making into blocks")
	# newimage.show()

	# if transparency_img is not None:
	# 	transparency_img2 = transparency_img.resize((transparency_img.size[0] * 16, transparency_img.size[1] * 16))
	# 	final_img = final_img.convert("RGBA")
	# 	final_img.paste(transparency_img2, (0,0), mask=transparency_img2)

	# print(blocks, final_img.size)
	GRID_COLOUR_1 = (100, 120, 100, 75)
	GRID_COLOUR_2 = (100, 140, 100, 145)
	GRID_COLOUR_3 = (120, 170, 125, 195)
	GRID_COLOUR_4 = (80, 255, 215, 235)
	# final_img.show()
	progress_bar(0, 1, strprg="Saving images")
	if not os.path.exists("output"):
		os.makedirs("output")
	final_img.save("output" + os.sep + "mural.png")

	# grid_img = Image.new("RGBA", (final_img.width, final_img.height), (0, 0, 0, 0))
	# for y in range(grid_img.height):
	# 	progress_bar(y, grid_img.height, strprg="Making grid")
	# 	for x in range(grid_img.width):
	# 		if x % (16 * 16) == 0 or (y - final_img.height) % (16 * 16) == (16*16) - 1 or y == final_img.height - 1:
	# 			grid_img.putpixel((x, y), GRID_COLOUR_4)
	# 		elif x % (16 * 8) == 0 or (y - final_img.height) % (16 * 8) == (16*8) - 1:
	# 			grid_img.putpixel((x, y), GRID_COLOUR_3)
	# 		elif x % (16 * 4) == 0 or (y - final_img.height) % (16 * 4) == (16 * 4) - 1:
	# 			grid_img.putpixel((x, y), GRID_COLOUR_2)
	# 		elif x % 16 == 0 or y % 16 == 15:
	# 			grid_img.putpixel((x, y), GRID_COLOUR_1)
	# grid_img.save("grid.png")
	# progress_bar(grid_img.height, grid_img.height, strprg="Making grid")
	if max(final_img.height, final_img.width) <= 1024:  # 64 blocks
		grid_img = Image.open("utils" + os.sep + "grid1024.png")
	elif max(final_img.height, final_img.width) <= 2048:  # 128 blocks
		grid_img = Image.open("utils" + os.sep + "grid2048.png")
	elif max(final_img.height, final_img.width) <= 4096:  # 256 blocks
		grid_img = Image.open("utils" + os.sep + "grid4096.png")
	else:
		grid_img = Image.open("utils" + os.sep + "grid8192.png")

	# grid_img.save("grid.png")
	grid_img = grid_img.crop((0, grid_img.height - final_img.height, final_img.width, grid_img.height))
	# grid_img.show()
	final_grid_img = Image.alpha_composite(final_img, grid_img)
	# final_grid_img.show()
	final_grid_img.save("output" + os.sep + "mural_with_grid.png")
	progress_bar(0, 1, strprg="Saving images")
	block_counts = []
	for item in blocks:
		if item["count"] > 0:
			block_counts.append((item["name"], item["count"]))
	block_counts.sort(key=lambda tup: tup[1], reverse=True)
	f = open("output" + os.sep + "blocks_needed.txt", "w")
	for i, bc in enumerate(block_counts):
		progress_bar(i, len(block_counts), strprg="Counting blocks")
		if bc[1] > 63:
			if bc[1] % 64 == 0:
				f.write(bc[0] + ': ' + str(bc[1] // 64) + ' stacks\n')
			else:
				f.write(bc[0] + ': ' + str(bc[1]//64) + ' stacks + ' + str(bc[1] % 64) + '\n')
		else:
			f.write(bc[0] + ': ' + str(bc[1]) + '\n')

	print("Complete! You can find the resulting images and block counts in the output directory")
	exit()

	# TODO: add dithering option
