import redis
import time
import json
import os
from cryptography.fernet import Fernet

#Start a local Redis server
r = redis.StrictRedis(host='localhost', port=6379, db=0)

#Create a key with an expiration time of 10 seconds
r.setex("tempKey", 10, "Now you see me...")

#Show current value of key
val = r.get("tempKey")
print("Current value of tempKey: " + str(val))

#Print the remaining Time-To-Live
ttl = r.ttl("tempKey")
print("Remaining TTL on tempKey: " + str(ttl))

#Sleep for remaining time
print("\nWaiting for " + str(ttl) + " seconds...")
time.sleep(ttl)
print("Wait time over!\n")

#Check if key has expired
if r.exists("tempKey") == 0:\
   print("The tempKey has expired!")
else:
    ttl = r.ttl("tempKey")
    print("The remaining TTL is: " + str(ttl))

#Set an expiration time on an existing key
user = os.getlogin()
key = "persistKey"
value = "Hello " + user + "!"
r.set(key, value)
r.expire(key, 5)

#Show current value of key
print("\nCurrent value of persistKey: " + str(r.get(key)))

#Print the remaining Time-To-Live
ttl = r.ttl(key)
print("Remaining TTL on persistKey: " + str(ttl))

#Remove the expiration time on the key
r.persist(key)

#Sleep for remaining time
print("\nWaiting for " + str(ttl) + " seconds...")
time.sleep(ttl)
print("Wait time over!\n")

#Check if key has expired
if r.exists(key) == 0:
    print("The persistKey has expired!")
else:
    print("Expiration time was removed from persistKey!")
    print("Current value: " + str(r.get(key)))

#Set an encrypted value
print("\nEncrypting credit card information...")
cypher = Fernet(Fernet.generate_key())
publicKey = "CC Info"
privateData = { "name": user,
"ccNum": 1234567890123456,
"expDate": [2023, 1],
"cvv": 000 }
encryptedVal = cypher.encrypt(
json.dumps(privateData).encode("utf-8"))
r.set(publicKey, encryptedVal)

#Display encrypted value
print("\nThe current value of CC Info: ")
val = r.get(publicKey)
print(val)

#Display the decrypted value
print("\nOnce decrypted, the value of CC Info is: ")
val = cypher.decrypt(val)
print(val)

#Close the connection to the database
r.close()
