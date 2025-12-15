'''
Damien Harmon
12/14/2025
Guided Practice 5.3
'''

import sqlite3
import json

#Notify when script is starting
print("Connecting to local SQLite database...")
db = sqlite3.connect('ReviewData.db')

#Create lists to hold each category and product
categoryList = []
productList = []

#Import data from JSON file
for line in open('dataset_en_dev.json', 'r'):
    dataSet = json.loads(line)
    categoryList.append(dataSet["product_category"])
    productList.append([dataSet["product_id"],
dataSet["product_category"]])

#Filter out duplicate categories
categoryList = [*set(categoryList)]

# *** CREATE SECTION ***

#Prep query to create a Categories table
newTable = '''
        CREATE TABLE IF NOT EXISTS Categories (
        CategoryName TEXT PRIMARY KEY
        );
        '''

db.execute(newTable)
print("Categories Table Created!")

#Prep query to create a Products table
newTable = '''
        CREATE TABLE IF NOT EXISTS Products (
        ProductID TEXT PRIMARY KEY,
        CategoryName TEXT,
        FOREIGN KEY(CategoryName) REFERENCES
        Categories(CategoryName)
        );
        '''

db.execute(newTable)
print("Products Table Created!")

#Insert each category into the Categories table
print("Inserting data into Categories Table...")
for category in categoryList:
    insert = "INSERT INTO Categories (CategoryName) VALUES('" + category + "');"
    db.execute(insert)
    
#Insert each product into the Products table
print("Inserting data into Products Table...")
for product in productList:
    insert = "INSERT OR REPLACE INTO Products (ProductID, CategoryName) VALUES("
    insert += "'" + product[0] + "', '" + product[1] + "');"
    db.execute(insert)

#Commit these changes to the database
db.commit()

# *** READ SECTION ***

#Display the first 3 values in the Categories Table
print("\nDisplaying 3 Categories:")
query = "SELECT * FROM Categories LIMIT 3;"
resultSet = db.execute(query)
for row in resultSet:
    print(row)
    
#Display all categories with at least 300 products
print("\nDisplaying Categories with 300+ products:")
query = '''
        SELECT CategoryName, COUNT(ProductID) FROM Products
        GROUP BY CategoryName
        HAVING COUNT(ProductID) >= 300;
        '''

resultSet = db.execute(query)
for row in resultSet:
    print(row)
    
# *** UPDATE SECTION ***

#Add a new column to an existing table
print("\nAdding a new column to the Categories Table named Description.")
query = "ALTER TABLE Categories ADD COLUMN Description TEXT;"
resultSet = db.execute(query)

#Update existing data within the table
print("Updating Description data for the camera category:")
query = '''
        UPDATE Categories SET Description = 'DAMHAR2570'
        WHERE CategoryName = 'camera';
        '''

resultSet = db.execute(query)

#Commit the change to the database
db.commit()

#Display the changed data
query = '''
        SELECT ProductID, Products.CategoryName, Description
        FROM Products INNER JOIN Categories
        ON Products.CategoryName = Categories.CategoryName
        WHERE Products.CategoryName = 'camera'
        LIMIT 1;
        '''

resultSet = db.execute(query)
for row in resultSet:
    print(row)

# *** DELETE SECTION ***

#Remove all Products in the "other" category
print("\nRemoving all products listed as Other...")
print("Previous Product Count: ")
query = "SELECT COUNT(*) FROM Products;"
resultSet = db.execute(query)
for row in resultSet:
    print(row)

query = "DELETE from Products WHERE CategoryName = 'other';"

resultSet = db.execute(query)

#Commit this change to the database
db.commit()

print("Current Product Count: ")
query = "SELECT COUNT(*) FROM Products;"
resultSet = db.execute(query)
for row in resultSet:
    print(row)
resultSet.close()

#Remove both tables from the database
print("\nRemoving the Tables from the database...")
query = "DROP TABLE IF EXISTS Products;"
db.execute(query)

query = "DROP TABLE IF EXISTS Categories;"
db.execute(query)

print("Complete!")

#Close connection to database
db.close()
