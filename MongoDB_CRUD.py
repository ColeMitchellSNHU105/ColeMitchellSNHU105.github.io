from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class db_CRUD:

    def __init__(self, username, password, host, port, database, collection):
        # Connection Variables, still hardcoded
        if username and password:
            self.client = MongoClient('mongodb://%s:%s@%s:%d' % (username, password, host, port))
        else:
            self.client = MongoClient('mongodb://%s:%d' % (host, port))
        self.database = self.client['%s' % database]
        self.collection = self.database['%s' % collection]
        
    # Create new document.
    def create(self, data):
        if data is None:
            return False
        
        dataF = []
        # Format data into a list:
        if isinstance(data, list):
            dataF = data
        else:
            dataF.append(data)
            
        try:
            result = self.database.collection.insert_many(dataF)
            return True
        except:
            return False
        
        return False # any other error

    # Return documents from database. Use projection to filter results.
    def read(self, filter, project=None):
        if (project):
            return self.collection.find(filter, project)
        else:
            return self.collection.find(filter)

    # Returns number of documents.
    def doc_count(self):
        return self.collection.count_documents({})

    # Delete specified documents. Returns number of documents destroyed.
    def delete(self, data):
        result = self.collection.delete_many(data)
        return result.deleted_count

    # Updates documents matching filter with new data.
    def update(self, filter, data):
        result = self.collection.update_many(filter, data)
        print('Found:', result.matched_count, 'Modified:', result.modified_count)
        return result.modified_count

    # Determines if software is actively connected to the MongoDB.
    def checkConnection(self):
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False