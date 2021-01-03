# MinecraftMuralMaker

To install dependencies, run `pip install -r requirements.txt`

To use MMM, put an image called `input.png` in the working directory, or pass in a path to an image with the -i argument

Optionally you can define the height of the mural in blocks with the optional argument -h `integer`
> NOTE: if you are working with large images, I would advise using this argument as otherwise it will be a 1 to 1 conversion from pixel to block, which will take a long time!
  
Usage: `mmm.py -r <"creative, glowing, crafting, hard, shulker, glazed, ugly, bee, sideways, ore, all">`
> When passing in more than 1 argument, you must surround them with \"\", (ex. -r \"shulker, ore\")

What each option removes:
* Creative: Bedrock
* Glowing: Glowstone, Jack o' Lantern, Shroomlite
* Crafting: Crafting Table, Furnace, Smoker, Blast Furnace, Smithing Table, Loom, Fletching Table, Dropper, Dispenser, Barrel
* Hard: Ancient Debris, Netherite Block, Diamond Block, Emerald Block
* Shulker: Shulker Boxes
* Glazed: Glazed Terracotta
* Ugly: Bookshelf, TNT, Quartz Ore, Pistons, Target Block, Carved Pumpkin
* Bee: Beehives, Bee Nest, Honey Block
* Sideways: Tops of all Logs and top of Piston
* Ore: All Ore blocks and Ancient Debris
* All: All of the above

The result will appear in the `output` folder, which will contain the outputted image, the image with a grid on it for easier building reference, and a file listing all blocks needed to build