from mcpi.minecraft import Minecraft
import rsa

# Assignment 3 main file
# Feel free to modify, and/or to add other modules/classes in this or other files

mc = Minecraft.create()
publicKey, privateKey = rsa.newkeys(512)
message = "Hello world"
encMessage = rsa.encrypt(message.encode(),publicKey)
print(encMessage)
# mc.postToChat(message)
decMessage = rsa.decrypt(encMessage, privateKey).decode()
print(decMessage)