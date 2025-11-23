"""
Damien Harmon
Richard Burns
Broderick Pride
"""


import json
from pymongo import MongoClient

# CONNECT TO MONGODB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["repo_db"]   # database name
collection = db["repos"] # collection name


#======================================================================================  
# Name:          JSON Loader  
# Parameters:    none  
# Return:        none  
# Description:   Loads JSON data into MongoDB collection 'repos' if not already loaded.  
#======================================================================================  
if collection.count_documents({"repo_id": 1}) == 0:
    print("Loading JSON repo data...")
    with open('Licenses.json', 'r') as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            repo_doc = {
                "repo_id": i+1,
                "repo_name": obj['repo_name'],
                "license": obj['license']
            }
            collection.insert_one(repo_doc)
    print("JSON repo documents loaded.\n")
else:
    print("Repo data already loaded.\n")


#======================================================================================  
# Name:          create_set  
# Parameters:    none  
# Return:        none  
# Description:   Prompts user for a set name and members, then inserts a new document  
#                into MongoDB collection 'sets'.  
#======================================================================================  
def create_set():
    set_name = input("Enter a name for the new set: ")

    members = []
    print("Enter members for the set (type 'done' to stop):")
    while True:
        member = input("> ")
        if member.lower() == "done":
            break
        members.append(member)

    doc = {"set_name": set_name, "members": members}
    db.sets.insert_one(doc)
    print(f"Set '{set_name}' created successfully!\n")


#======================================================================================  
# Name:          read_set  
# Parameters:    none  
# Return:        none  
# Description:   Prompts user for a set name, retrieves the document from MongoDB,  
#                and prints all members of the set.  
#======================================================================================  
def read_set():
    set_name = input("Enter the name of the set to retrieve: ")
    doc = db.sets.find_one({"set_name": set_name})

    if not doc:
        print("Set does not exist.\n")
        return

    print(f"\nMembers of '{set_name}':")
    for m in doc["members"]:
        print(f"- {m}")
    print()


#======================================================================================  
# Name:          update_set  
# Parameters:    none  
# Return:        none  
# Description:   Prompts user for a set name, then allows adding or removing members  
#                from the MongoDB document using $addToSet and $pull operations.  
#======================================================================================  
def update_set():
    set_name = input("Enter the name of the set to update: ")
    doc = db.sets.find_one({"set_name": set_name})

    if not doc:
        print("Set does not exist.\n")
        return

    print("\nWhat would you like to do?")
    print("1. Add a new member")
    print("2. Remove a member")

    choice = input("Choose an option (1/2): ")

    if choice == "1":
        member = input("Enter the member to add: ")
        db.sets.update_one({"set_name": set_name}, {"$addToSet": {"members": member}})
        print("Member added!\n")

    elif choice == "2":
        member = input("Enter the member to remove: ")
        db.sets.update_one({"set_name": set_name}, {"$pull": {"members": member}})
        print("Member removed!\n")

    else:
        print("Invalid choice.\n")


#======================================================================================  
# Name:          delete_set  
# Parameters:    none  
# Return:        none  
# Description:   Prompts user for a set name and deletes the corresponding document  
#                from MongoDB collection 'sets'.  
#======================================================================================  
def delete_set():
    set_name = input("Enter the name of the set to delete: ")
    result = db.sets.delete_one({"set_name": set_name})

    if result.deleted_count == 0:
        print("Set does not exist.\n")
    else:
        print(f"Set '{set_name}' deleted successfully!\n")


#======================================================================================  
# Name:          delete_all  
# Parameters:    none  
# Return:        none  
# Description:   Prompts user for confirmation and deletes all documents from both  
#                'sets' and 'repos' collections in MongoDB.  
#======================================================================================  
def delete_all():
    confirm = input("Are you sure you want to delete ALL data? (yes/no): ").lower()
    if confirm == "yes":
        db.sets.delete_many({})
        collection.delete_many({})
        print("All data deleted!\n")
    else:
        print("Cancelled.\n")


#======================================================================================  
# Name:          menu  
# Parameters:    none  
# Return:        none  
# Description:   Displays the main menu, handles user input, and calls the appropriate  
#                CRUD functions for MongoDB sets.  
#======================================================================================  
def menu():
    while True:
        print("All choices are made by entering the corresponding number only.\n")
        print("--------------------------------------")
        print("  MongoDB Set CRUD Application")
        print("--------------------------------------")
        print("1. Create a new set")
        print("2. Read a set")
        print("3. Update a set")
        print("4. Delete a set")
        print("5. Delete ALL database data")
        print("0. Exit")
        print("--------------------------------------")

        choice = input("Enter choice: ")

        if choice == "1":
            create_set()
        elif choice == "2":
            read_set()
        elif choice == "3":
            update_set()
        elif choice == "4":
            delete_set()
        elif choice == "5":
            delete_all()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid selection.\n")


#======================================================================================  
# Name:          main  
# Parameters:    none  
# Return:        none  
# Description:   Connects to MongoDB, verifies connection with ping, and starts the  
#                menu-driven CRUD application.  
#======================================================================================  
if __name__ == "__main__":
    print("Connecting to MongoDB database...")
    try:
        client.admin.command('ping')
        print("Connected successfully!\n")
    except Exception as e:
        print("Failed to connect to MongoDB. Make sure 'mongod' is running.")
        exit()

    menu()

