# MinecraftMuralMaker

## Intro

This is a project to help contstruct large murals in survival Minecraft! Pass in an image, and it will be turned into minecraft blocks, and you will recieve an additional text file that tells how much of each block you will need to build it!

## Installation

This assumes you already have downloaded some version of Python (preferably >=3.7)

To install, run `git clone https://github.com/michaelwoolsey/MinecraftMuralMaker` in whatever folder you would like to install the project into, then run `cd MinecraftMuralMaker`

To install dependencies, run `pip install -r requirements.txt` (you may choose to run `python -m venv .` before this command)

## Usage

To use MMM, put an image called `input.png` in the working directory, or pass in a path to an image with the `-i` argument

Optionally you can define the height of the mural in blocks with the optional argument `-h integer`
> NOTE: if you are working with large images, I would advise using this argument as otherwise it will be a 1 to 1 conversion from pixel to block, which will take a long time!

`-d` will dither the result, which may make photographs look more realistic
  
Usage: `mmm.py -r <"creative, glowing, crafting, expensive, shulker, glazed, ugly, bee, sideways, ore, copper, all"> -i <filepath> (OPTIONAL: -h <integer> -d) `
> When passing in more than 1 argument, you must surround them with \"\", (ex. `-r "shulker ore expensive"`)

The program will not use any invalid or transparent blocks, (ex. chests, glass), but you can choose to remove other blocks:
* Creative: Bedrock
* Glowing: Glowstone, Jack o' Lantern, Shroomlite
* Crafting: Crafting Table, Furnace, Smoker, Blast Furnace, Smithing Table, Loom, Fletching Table, Dropper, Dispenser, Barrel
* Expensive: Ancient Debris, Netherite Block, Diamond Block, Emerald Block, Gilded Blackstone, Amethyst block, Calcite, Lodestone, Rooted dirt
* Shulker: Shulker Boxes
* Glazed: Glazed Terracotta
* Ugly: Bookshelf, TNT, Quartz Ore, Pistons, Target Block, Carved Pumpkin, Copper ore, Muddy Mangrove Roots
* Bee: Beehives, Bee Nest, Honey Block
* Sideways: Tops of all Logs and top of Piston
* Ore: All Ore blocks and Ancient Debris
* Copper: All Copper blocks that can weather
* All: All of the above

The results will appear in the `output` folder, which will contain the outputted image, the image with a grid on it for easier building reference, and a file listing all blocks needed to build

## Examples!
![before](https://i.imgur.com/mUTdpNR.png)
![after](https://i.imgur.com/yH3UrZi.png)
![grid](https://i.imgur.com/1FQrixf.png)
