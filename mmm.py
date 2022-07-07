from math import ceil
import os
from PIL import Image
import numpy as np
import sys
import getopt
import random


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
	if "bedrock" in name or 'deepslate_coal_ore' in name:
		return False
	return True


def remove_glowing_blocks(name):
	if "glowstone" in name or \
			"jack" in name or \
			"crying_obsid" in name or \
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
			"lodestone" in name or \
			"rooted_dirt" in name or \
			"calcite" in name or \
			"amethyst" in name or \
			"emerald" in name:
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
			"carved" in name or \
			"gilded_blackstone" in name or \
			"muddy_mangrove_roots" in name or \
			"birch_log" in name or \
			"redstone_ore" in name or \
			"copper_ore" in name:
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


def remove_copper_blocks(name):
	if "copper" in name:
		return "ore" in name or "raw" in name  # copper ore and raw copper block allowed, all others not
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
	# remove copper blocks (only the ones that weather)
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
	block_removals = 0b00000000000
	# block_removals = 0b11111111111

	valid_blocks = []
	input_filepath = None
	dither = False
	x_given = False
	y_given = False

	test_img = Image.new(mode="RGB", size=(LEN*16, 32), color=(255, 255, 255))

	try:
		options, args = getopt.getopt(sys.argv[1:], "h:i:r:d:x:y:", ["help", "remove="])
	except getopt.GetoptError:
		print("Usage: mmm.py -r <\"creative, glowing, crafting, expensive, shulker, glazed, ugly, bee, sideways, ore, copper, all\">")
		exit(0)

	for opt, arg in options:
		if opt == "--help":
			print("\nWelcome to Minecraft Mural Maker! A tool made specifically for building murals in survival Minecraft\n\n"
				  "To use MMM, put an image called \'input.png\' in the working directory, or pass in a path to"
				  " an image with the -i argument\nOptionally you can define the height of the mural in blocks "
				  "with the optional argument -h <integer>\n\tNOTE: if you are working with large images, I would"
				  " advise using this argument as otherwise it will be a 1 to 1 conversion from pixel to block, which"
				  " will take a long time!\n"
				  "For the building guide text file, you can choose to define a starting coordinate for the bottom left corner block, "
				  "and this can be done through the -x <integer representing the bottom left block's x or z coordinate> -y <integer rerpreseting the bottom left block's y coordinate> arguments\n"
				  "NOTE: I recommend measuring this by physically placing a block down in your world where you think the bottom left should be (even if the block in the mural will be transparent), "
				  "and then using the 'Targeted Block' values on the right side of the F3 screen to define that point\n"
				  "-d will dither the image, it may make the result look better, or it might make it worse!\n\n"
				  "Usage: mmm.py -r <\"creative, glowing, crafting, expensive, shulker, glazed, ugly, bee, sideways, ore, all\">\n"
				  "When passing in more than 1 argument, you must surround them with \"\", (ex. -r \"shulker, ore\")\n"
				  "What each option removes:\n"
				  "\tCreative: Bedrock\n"
				  "\tGlowing: Glowstone, Jack o' Lantern, Shroomlite, Crying Obsidian\n"
				  "\tCrafting: Crafting Table, Furnace, Smoker, Blast Furnace, Smithing Table, Loom, Fletching Table, Dropper, Dispenser, Barrel\n"
				  "\tExpensive: Ancient Debris, Netherite Block, Diamond Block, Emerald Block, Gilded Blackstone, Lodestone, Rooted Dirt, Amethyst Block, Calcite\n"
				  "\tShulker: Shulker Boxes\n"
				  "\tGlazed: Glazed Terracotta\n"
				  "\tUgly: Bookshelf, TNT, Quartz Ore, Pistons, Target Block, Carved Pumpkin, Muddy Mangrove Roots\n"
				  "\tBee: Beehives, Bee Nest, Honey Block\n"
				  "\tSideways: Tops of all Logs and top of Piston\n"
				  "\tOre: All Ore blocks and Ancient Debris\n"
				  "\tCopper: All Copper blocks that can become weathered\n"
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
			if "copper" in arg:
				block_removals |= 0b1 << 10
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
		elif opt == "-x":
			x_coord_val = int(arg)
			x_given = True
		elif opt == "-y":
			y_coord_val = int(arg)
			y_given = True
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
						((block_removals & (0b1 << 9)) == 0 or (remove_ore_blocks(filepath))) and \
						((block_removals & (0b1 << 10)) == 0 or (remove_copper_blocks(filepath))):
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

	# there is an infuriating problem with PIL that i am not in the place mentally to solve for now, but
	# the palettedata can only contain 256 colours at the most, and currently we have 297 when using all blocks,
	# so the workaround for now is to remove random blocks until we get 256
	if len(palettedata)//3 > 256:  
		num_to_remove = len(palettedata)//3 - 256
		print(f'NOTE: Due to package limitations, {num_to_remove} random blocks have been removed from the palette for the program to work\n')
		to_remove = random.sample(range(1, 256), num_to_remove)
		to_remove = [elm * 3 for _, elm in enumerate(to_remove)]
		to_remove.sort()
		to_remove = [elm - i*3 for i, elm in enumerate(to_remove)]
		for i in to_remove:
			del palettedata[i]
			del palettedata[i]
			del palettedata[i]



	# print('\n\n\n')

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
	palimage.putpalette(list(palettedata))
	newimage = quantizetopalette(input_img, palimage, dither=dither)
	print("Quantizing            ", end='\r')

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
			block_name = get_col_name(px)
			increment_block_count(px)
			if not block_name == "TSP":
				txt = Image.open("blocks" + os.sep + block_name + ".png")
				final_img.paste(txt, (x*16, y*16))
	progress_bar(newimage.height, newimage.height, strprg="Making into blocks")

	block_str = ""
	block_str_csv = ""
	block_sep = " | "
	block_sep_csv = ", "
	# print(f'\n\n{blocks}')
	# print(list(itm for itm in blocks))
	longest_block_len = max([len(itm['name']) for itm in blocks])
	y_val = newimage.height if not y_given else y_coord_val + newimage.height -1
	x_val_start = 1 if not x_given else x_coord_val

	for y in range(newimage.height):
		progress_bar(y, newimage.height, strprg="Counting blocks")
		block_str += str(y_val).ljust(len(str(newimage.height + newimage.height -1)) + 1, " ")
		block_str_csv += str(y_val) + block_sep_csv
		for x in range(newimage.width):
			px = newimage.getpixel((x, y))
			block_name = get_col_name(px)
			if block_name == "TSP":
				block_str += ' ' * longest_block_len + block_sep
				block_str_csv += block_sep_csv
			else:
				block_str += block_name.center(longest_block_len, " ") + block_sep
				block_str_csv += block_name + block_sep_csv
		block_str = block_str[:-len(block_sep)] + "\n"
		block_str_csv += '\n'
		y_val -= 1

	block_str += " " * (len(str(newimage.height)) + 1)
	xv = x_val_start
	x_coord_str = "index, "
	for x in range(newimage.width):
		block_str += str(xv).center(longest_block_len, " ") + " " * len(block_sep)
		x_coord_str += str(xv) + block_sep_csv
		xv += 1
	
	progress_bar(newimage.height, newimage.height, strprg="Counting blocks")

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
	
	total_stacks = 0
	total_blocks = 0
	final_string = ""
	for i, bc in enumerate(block_counts):
		progress_bar(i, len(block_counts), strprg="Counting blocks")
		if bc[1] > 63:
			if bc[1] % 64 == 0:
				final_string += bc[0] + ': ' + str(bc[1] // 64) + ' stacks\n'
				total_stacks += bc[1] // 64
			else:
				final_string += bc[0] + ': ' + str(bc[1]//64) + ' stacks + ' + str(bc[1] % 64) + '\n'
				total_stacks += (bc[1] // 64) + 1
		else:
			final_string += bc[0] + ': ' + str(bc[1]) + '\n'
			total_stacks += 1
		total_blocks += bc[1]
	
	f.write(f'WIDTH: {newimage.width}, HEIGHT: {newimage.height}, UNIQUE BLOCKS: {len(block_counts)}, TOTAL BLOCKS: {total_blocks}, TOTAL STACKS: {total_stacks}, TOTAL SHULKERS NEEDED: {ceil(total_stacks / 30)}\n')
	f.write(f'(Note: If your image is transparent, the width may not be fully accurate since transparent spaces to the side of the mural will be counted for the number)\n\n')
	f.write(final_string)
	f.write(f'\n\nIn order to see the following block guide, you will have to open this file in a text editor where the lines don\'t wrap (like Visual Studio Code)\n\n{block_str}')
	
	print("Complete! You can find the resulting images and block counts in the output directory")
	# exit()
	f.close()

	fcsv = open(f'output{os.sep}building_guide.csv', 'w')
	fcsv.write(x_coord_str+'\n'+block_str_csv)
	fcsv.close()

