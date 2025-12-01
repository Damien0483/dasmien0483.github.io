"""
Damien Harmon
12/01/2025
Guided Practice 3.3
"""

import json
from cassandra.cluster import Cluster

# ***CREATE SECTION***
print("Connecting to local Cassandra database...")

# Connect to a local Cassandra cluster
cluster = Cluster()
session = cluster.connect()

# Create a keyspace and connect to it
keyspace = '''
    CREATE KEYSPACE IF NOT EXISTS ReviewData
    WITH replication = {'class':'SimpleStrategy','replication_factor':1};
'''
session.execute(keyspace)
session.execute('USE ReviewData;')

# Create Reviews table
newTable = '''
    CREATE TABLE IF NOT EXISTS Reviews(
        ReviewID text PRIMARY KEY,
        ReviewerID text,
        ProductID text,
        Category text,
        Stars int,
        Title text,
        Content text,
        Language text
    );
'''
session.execute(newTable)

# Create Categories table
newTable = '''
    CREATE TABLE IF NOT EXISTS Categories(
        ProductID text,
        Category text,
        Stars int,
        PRIMARY KEY((Category), Stars)
    );
'''
session.execute(newTable)

# ***IMPORT SECTION***
print("Importing data from file...")
for line in open('dataset_en_dev.json', 'r'):
    dataSet = json.loads(line)

    # Corrected INSERT with 8 placeholders
    insertReviewsPrep = '''
        INSERT INTO Reviews (ReviewID, ReviewerID, ProductID, Category, Stars, Title, Content, Language)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    '''
    session.execute(insertReviewsPrep, (
        dataSet["review_id"],
        dataSet["reviewer_id"],
        dataSet["product_id"],
        dataSet["product_category"],
        int(dataSet["stars"]),
        dataSet["review_title"],
        dataSet["review_body"],
        dataSet["language"]
    ))

    # Insert into Categories
    insertCategoriesPrep = '''
        INSERT INTO Categories (Category, Stars, ProductID)
        VALUES (%s, %s, %s);
    '''
    session.execute(insertCategoriesPrep, (
        dataSet["product_category"],
        int(dataSet["stars"]),
        dataSet["product_id"]
    ))

print("Data imported successfully!")

# ***READ SECTION***
rowCount = session.execute('SELECT COUNT(*) FROM Reviews;')
print("Number of rows: " + str(rowCount.one()))

rowCount = session.execute('SELECT COUNT(*) FROM Reviews WHERE Stars = 5 ALLOW FILTERING;')
print("Number of 5 star reviews: " + str(rowCount.one()))

results = session.execute('SELECT DISTINCT Category FROM Categories LIMIT 10;')
print("\n10 Product Categories: ")
for row in results:
    print(row)

results = session.execute("SELECT COUNT(*) FROM Reviews WHERE Category = 'wireless' AND Stars > 3 ALLOW FILTERING;")
print("\nNumber of 4 and 5 star reviews of wireless products: " + str(results.one()))

rowCount = session.execute("SELECT MIN(Stars), MAX(Stars) FROM Reviews WHERE ProductID = 'product_en_0947733' ALLOW FILTERING;")
print("\nMinimum and maximum stars for product 0947733: ")
print(rowCount.one())

# ***UPDATE SECTION***
print("\nRemoving Language from the Reviews table...")
session.execute('ALTER TABLE Reviews DROP Language;')
print("Complete!")

# ***DELETE SECTION***
print("\nRemoving 1 star reviews from pc products...")
session.execute("DELETE FROM Categories WHERE Stars = 1 AND Category = 'pc';")
print("Complete!")

print("\nRemoving the ProductID from any 2 star pc reviews...")
# If you want to remove the whole row:
session.execute("DELETE FROM Categories WHERE Stars = 2 AND Category = 'pc';")
print("Complete!")

print("\nRemoving Categories table...")
session.execute('DROP TABLE IF EXISTS Categories;')
print("Complete!")

print("Removing ReviewData Keyspace...")
session.execute('DROP KEYSPACE IF EXISTS ReviewData;')
print("Complete!")
