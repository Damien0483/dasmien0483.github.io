import json
from pymongo import MongoClient

# CONNECT TO MONGODB
print("Connecting to MongoDB...")

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["repo_db"]            # Database name
collection = db["repos"]          # Collection name (CRUD uses this)

try:
    client.admin.command("ping")
    print("Connected successfully!\n")
except Exception:
    print("MongoDB is not running. Start mongod first.")
    exit()


# LOAD JSON FILE INTO repos COLLECTION (ONLY ONCE)
if collection.count_documents({}) == 0:
    print("Loading JSON repo data into 'repos' collection...")

    with open("Licenses.json", "r") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)

            repo_doc = {
                "repo_id": i + 1,
                "repo_name": obj.get("repo_name", "Unknown"),
                "license": obj.get("license", "None")
            }

            collection.insert_one(repo_doc)

    print("JSON repo documents loaded.\n")
else:
    print("'repos' collection already contains data.\n")


# CREATE A NEW DOCUMENT
def create_repo():
    print("\n--- Create New Repo Document ---")

    repo_name = input("Enter repo name: ")
    license_name = input("Enter license: ")

    new_doc = {
        "repo_name": repo_name,
        "license": license_name
    }

    collection.insert_one(new_doc)
    print("Document created.\n")


# READ Documents
def read_repo():
    print("\n--- Read Repo Document ---")
    repo_name = input("Enter repo name to search: ")

    doc = collection.find_one({"repo_name": repo_name})

    if not doc:
        print("Document not found.\n")
    else:
        print("Document found:")
        print(doc, "\n")


def read_all_repos():
    print("\n--- Display First 5 Repo Documents ---")
    for doc in collection.find().limit(5):
        print(doc)
    print()


# UPDATE A DOCUMENT
def update_repo():
    print("\n--- Update Repo Document ---")

    repo_name = input("Enter repo name to update: ")
    doc = collection.find_one({"repo_name": repo_name})

    if not doc:
        print("Document not found.\n")
        return

    print("1. Update repo name")
    print("2. Update license")

    choice = input("Choose an option: ")

    if choice == "1":
        new_name = input("New repo name: ")
        collection.update_one(
            {"repo_name": repo_name},
            {"$set": {"repo_name": new_name}}
        )
        print("Repo name updated.\n")

    elif choice == "2":
        new_license = input("New license: ")
        collection.update_one(
            {"repo_name": repo_name},
            {"$set": {"license": new_license}}
        )
        print("License updated.\n")

    else:
        print("Invalid choice.\n")


# DELETE A DOCUMENT
def delete_repo():
    print("\n--- Delete Repo Document ---")
    repo_name = input("Enter repo name to delete: ")

    result = collection.delete_one({"repo_name": repo_name})

    if result.deleted_count == 0:
        print("Document not found.\n")
    else:
        print("Document deleted.\n")


# DELETE ALL DOCUMENTS
def delete_all():
    print("\n--- Delete ALL Documents ---")
    confirm = input("Are you SURE? This removes ALL docs (yes/no): ")

    if confirm.lower() == "yes":
        deleted = collection.delete_many({})
        print(f"Deleted {deleted.deleted_count} documents.\n")
    else:
        print("Cancelled.\n")


# DELETE COLLECTION
def delete_collection():
    print("\n--- Delete Entire Collection ---")
    confirm = input("This will DELETE the 'repos' collection. Continue? (yes/no: ")

    if confirm.lower() == "yes":
        collection.drop()
        print("Collection deleted.\n")
    else:
        print("Cancelled.\n")


# MENU SYSTEM
def menu():
    while True:
        print("--------------------------------------")
        print("       MongoDB CRUD Application       ")
        print("--------------------------------------")
        print("1. Create New Repo Document")
        print("2. Read One Repo Document")
        print("3. Read First 5 Repo Documents")
        print("4. Update Repo Document")
        print("5. Delete Repo Document")
        print("6. Delete ALL Documents")
        print("7. Delete Collection")
        print("0. Exit")
        print("--------------------------------------")

        choice = input("Enter choice: ")

        if choice == "1":
            create_repo()
        elif choice == "2":
            read_repo()
        elif choice == "3":
            read_all_repos()
        elif choice == "4":
            update_repo()
        elif choice == "5":
            delete_repo()
        elif choice == "6":
            delete_all()
        elif choice == "7":
            delete_collection()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid selection.\n")


# RUN THE PROGRAM
if __name__ == "__main__":
    menu()

