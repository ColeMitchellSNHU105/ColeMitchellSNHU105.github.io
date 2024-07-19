from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
import pprint

class db_CRUD:

    def __init__(self, username, password):
        # Connection Variables, still hardcoded
        if username: USER = username
        if password: PASS = password
        HOST = 'localhost'
        PORT = 27017
        DB = 'Cole_Fish'
        COL = 'Feesh'
        #
        # Initialize Connection
        #
        # self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.client = MongoClient('mongodb://localhost:27017/')
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]
        
    # Create new document.
    def create(self, data):
        if data is None:
            # print('No data to insert.')
            return False
        
        dataF = []
        #Format data into a list:
        if isinstance(data, list):
            dataF = data
        else:
            dataF.append(data)
            
        try:
            result = self.database.collection.insert_many(dataF)
            return True
        except:
            print('Could not insert.')
            return False
        
        return False # any other error

    # Return documents from database. Use projection to filter results.
    def read(self, filter, project=None):
        if (project):
            return self.collection.find(filter, project)
        else:
            return self.collection.find(filter)

    # Print to console number of documents.
    def doc_count(self):
        print('Documents:', self.collection.count_documents({}))

    # Delete specified documents. Returns number of documents destroyed.
    def delete(self, data):
        result = self.collection.delete_many(data)
        print('Deleted:', result.deleted_count)
        return result.deleted_count
    
    def update(self, filter, data):
        result = self.collection.update_many(filter, data)
        print('Found:', result.matched_count, 'Modified:', result.modified_count)
        return result.modified_count

    # Determines if software is actively connected to the MongoDB.
    def checkConnection(self):
        try:
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False