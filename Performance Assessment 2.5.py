"""
Author: [Your Name]
Date: [Current Date]
Assignment: MongoDB CRUD Application
Purpose: This program demonstrates CRUD (Create, Read, Update, Delete) operations
         on a MongoDB database using PyMongo. The application interacts with the
         Amazon MongoDB database and performs operations on the ReviewData collection.
"""

from pymongo import MongoClient

#======================================================================================
# Name:          MongoDB Connection
# Parameters:    none
# Return:        client object
# Description:   Establishes connection to Amazon MongoDB cluster using PyMongo.
#======================================================================================
client = MongoClient("mongodb+srv://<username>:<password>@<cluster-url>/test?retryWrites=true&w=majority")

#======================================================================================
# Name:          Database and Collection Access
# Parameters:    none
# Return:        db, collection objects
# Description:   Accesses AmazonDB database and ReviewData collection.
#======================================================================================
db = client["AmazonDB"]
collection = db["ReviewData"]

#======================================================================================
# Name:          create_review
# Parameters:    none
# Return:        none
# Description:   Prompts user for review details and inserts a new document into
#                ReviewData collection.
#======================================================================================
def create_review():
    review = {
        "review_id": input("Enter review_id: "),
        "product_id": input("Enter product_id: "),
        "reviewer_id": input("Enter reviewer_id: "),
        "stars": int(input("Enter stars (1-5): ")),
        "review_body": input("Enter review_body: "),
        "review_title": input("Enter review_title: "),
        "language": input("Enter language: "),
        "product_category": input("Enter product_category: ")
    }
    result = collection.insert_one(review)
    print(f"Review created with _id: {result.inserted_id}")

#======================================================================================
# Name:          read_one_review
# Parameters:    none
# Return:        none
# Description:   Retrieves and displays a single review document based on review_id.
#======================================================================================
def read_one_review():
    review_id = input("Enter review_id to find: ")
    review = collection.find_one({"review_id": review_id})
    print(review if review else "No review found.")

#======================================================================================
# Name:          read_reviews
# Parameters:    none
# Return:        none
# Description:   Retrieves multiple review documents using filter options:
#                stars >= value, stars < value, title contains word, body contains word.
#======================================================================================
def read_reviews():
    print("Filter options:")
    print("1. Stars >= value")
    print("2. Stars < value")
    print("3. Title contains word")
    print("4. Body contains word")
    choice = input("Enter choice: ")

    if choice == "1":
        stars = int(input("Enter minimum stars: "))
        results = collection.find({"stars": {"$gte": stars}})
    elif choice == "2":
        stars = int(input("Enter maximum stars: "))
        results = collection.find({"stars": {"$lt": stars}})
    elif choice == "3":
        word = input("Enter word to search in title: ")
        results = collection.find({"review_title": {"$regex": word, "$options": "i"}})
    elif choice == "4":
        word = input("Enter word to search in body: ")
        results = collection.find({"review_body": {"$regex": word, "$options": "i"}})
    else:
        print("Invalid choice.")
        return

    for r in results:
        print(r)

#======================================================================================
# Name:          update_review
# Parameters:    none
# Return:        none
# Description:   Updates a specific field in a review document identified by review_id.
#======================================================================================
def update_review():
    review_id = input("Enter review_id to update: ")
    field = input("Enter field to update: ")
    value = input("Enter new value: ")

    if field == "stars":
        value = int(value)

    result = collection.update_one({"review_id": review_id}, {"$set": {field: value}})
    print(f"Matched {result.matched_count}, Modified {result.modified_count}")

#======================================================================================
# Name:          delete_review
# Parameters:    none
# Return:        none
# Description:   Deletes a single review document from ReviewData collection.
#======================================================================================
def delete_review():
    review_id = input("Enter review_id to delete: ")
    result = collection.delete_one({"review_id": review_id})
    print(f"Deleted {result.deleted_count} document(s).")

#======================================================================================
# Name:          clear_collection
# Parameters:    none
# Return:        none
# Description:   Deletes all documents in ReviewData collection after user confirmation.
#======================================================================================
def clear_collection():
    confirm = input("Are you sure you want to delete ALL documents? (yes/no): ")
    if confirm.lower() == "yes":
        result = collection.delete_many({})
        print(f"Deleted {result.deleted_count} documents.")

#======================================================================================
# Name:          drop_collection
# Parameters:    none
# Return:        none
# Description:   Drops the entire ReviewData collection after user confirmation.
#======================================================================================
def drop_collection():
    confirm = input("Are you sure you want to DROP the collection? (yes/no): ")
    if confirm.lower() == "yes":
        collection.drop()
        print("Collection dropped.")

#======================================================================================
# Name:          menu
# Parameters:    none
# Return:        none
# Description:   Provides a menu-driven interface for CRUD operations on ReviewData.
#======================================================================================
def menu():
    while True:
        print("\n--- Amazon ReviewData CRUD Menu ---")
        print("1. Create a new review")
        print("2. Read one review")
        print("3. Read reviews with filters")
        print("4. Update a review")
        print("5. Delete a review")
        print("6. Clear all reviews")
        print("7. Drop the collection")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_review()
        elif choice == "2":
            read_one_review()
        elif choice == "3":
            read_reviews()
        elif choice == "4":
            update_review()
        elif choice == "5":
            delete_review()
        elif choice == "6":
            clear_collection()
        elif choice == "7":
            drop_collection()
        elif choice == "8":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

#======================================================================================
# Name:          Main Program Execution
# Parameters:    none
# Return:        none
# Description:   Runs the menu function when the script is executed directly.
#======================================================================================
if __name__ == "__main__":
    menu()
