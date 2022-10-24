from mcpiImproved.mcpi.minecraft import Minecraft

# Assignment 3 main file
# Feel free to modify, and/or to add other modules/classes in this or other files

mc = Minecraft.create()
print(mc.conn.public_key.public_numbers())
#mc.setBlock(10,10,10,1)
# x = "1"
# mc.postToChat(x)
