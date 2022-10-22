from email import message
from mcpi.minecraft import Minecraft
import rsa

# Assignment 3 main file
# Feel free to modify, and/or to add other modules/classes in this or other files

mc = Minecraft.create()
# x = "1"
# mc.postToChat(x)
x = mc.getPublicKey()
print(x)
