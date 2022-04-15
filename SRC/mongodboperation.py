import logging
import os
import pymongo



connString = os.environ['MONGODB_CONNSTRING']

logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"
logging.basicConfig(level=logging.INFO, format=logging_str)


class MongoDB:
    '''class for mongo db operations'''

    def __init__(self, db_name, collection):
        """Initialize the class with the database name and collection name
        the class initialization the class with the below argument 

        Args:
            db : database name
            collection : collection name
            
        """

        logging.debug('init function db %s collection %s', str(db_name), str(collection))
        self.db_name = db_name

        logging.debug('get connection to mongo db')

        try:
            mongourl = connString
            logging.info('connection string %s', mongourl)
            self.conn = pymongo.MongoClient(mongourl)
            logging.debug('connection to mongo db successful')
            self.db = self.conn[self.db_name]
            self.collection = self.db[collection]

        except Exception as e:
            logging.error('error in get connection to mongo db %s', e)
        logging.debug('connection to mongo db successful')

    def checkExistence_DB(self, DB_NAME):
        """"It verifies the existence of database name
        DB_NAME: database name 
        return True if database exists else False"""

        DBlist = self.conn.list_database_names()
        if DB_NAME in DBlist:
            logging.debug(f"DB: '{DB_NAME}' exists")
            return True
        logging.error(f"DB: '{DB_NAME}' not yet present OR no collection is present in the DB")
        return False

    def checkExistence_COL(self, COLLECTION_NAME):

        """It verifies the existence of collection name
        Collection_NAME: collection name
        returns True if collection exists else False"""

        collection_list = self.db.list_collection_names()

        if COLLECTION_NAME in collection_list:
            logging.debug(f"Collection:'{COLLECTION_NAME}' in Database:'' exists")
            return True

        logging.error(f"Collection:'{COLLECTION_NAME}' in Database:' does not exists OR \n\
        no documents are present in the collection")
        return False

    def get_databases(self):
        '''This function will return the list of databases'''
        logging.debug('get database')
        return self.conn.list_database_names()

    def insert_one(self, data):
        """insert one data into mongo dd

        Args:
            data (formated ): data to be inserted into mongo db
            
            {Key : Value}
            

        Returns:
            True if insertion is successful else False
        """
        try:
            self.collection.insert_one(data)
        except Exception as e:
            logging.debug('error in insert data into mongo db %s', e)
            return False
        logging.debug('insert data into mongo db successful%s')
        return True

    def insert_many(self, data):
        """insert many data into mongo dd

        Args:
            data (formated ): data to be inserted into mongo db
            
            {Key : Value}
            

        Returns:
            True if insertion is successful else False
        """
        logging.debug('insert many data into mongo db')
        try:
            self.collection.insert_many(data)
        except Exception as e:
            logging.critical('error in insert many data into mongo db %s', e)
            print(e)
            return False
        logging.debug('insert many data into mongo db successful')
        return True

    def find_one(self, query={}):
        """find one data from mongo db
        if query is not provided then it will return the first document
        """

        logging.debug('find one data from mongo db')
        try:
            return self.collection.find_one(query)
        except Exception as e:
            logging.critical('error in find one data from mongo db %s', e)
            return None

    def find_many(self, query={}, limit=2000):
        """find many data from mongo db
        if query is not provided then it will return all the documents
        """

        try:
            logging.debug('find many data from mongo db')
            return self.collection.find(query).limit(limit)
        except Exception as e:
            logging.critical('error in find many data from mongo db %s', e)
            return False

    def update_one(self, query, data):
        """update one data from mongo db

        Args:
            query (Arg): Arguments to be matched
            data (formated): data to be updated

        Returns:
            _True if update is successful else False
        """

        try:
            logging.debug('update one data from mongo db query %s data %s', query, data)
            self.collection.update_one(query, data)
        except Exception as e:
            logging.critical('error in update one data from mongo db %s', e)
            return False
        logging.debug('update one data from mongo db successful')
        return True

    def update_many(self, query, data):
        """update many data from mongo db
        Args:
            query (Arg): Arguments to be matched
            data (formated): data to be updated

        Returns:
            True if update is successful else False
        """
        try:
            logging.debug('update many data from mongo db query %s data %s', query, data)
            self.collection.update_many(query, data)
        except Exception as e:
            logging.critical('error in update many data from mongo db %s', e)
            return False
        logging.debug('update many data from mongo db successful')
        return True

    def delete_one(self, query):
        """delete one data from mongo db
        Args:
            query (Arg): Arguments to be matched
    
        Returns:
            True if delete is successful else False
        """
        try:
            logging.debug('delete one data from mongo db query %s', query)
            self.collection.delete_one(query)
        except Exception as e:
            logging.critical('error in delete one data from mongo db %s', e)
            return False
        logging.debug('delete one data from mongo db successful')
        return True

    def delete_many(self, query):
        """delete many data from mongo db
        Args:
            query (Arg): Arguments to be matched
           

        Returns:
            True if delete is successful else False"""
        try:
            logging.debug('delete many data from mongo db query %s', query)
            self.collection.delete_many(query)
        except Exception as e:
            logging.critical('error in delete many data from mongo db %s', e)
            return False
        logging.debug('delete many data from mongo db successful')
        return True

    def drop_collection(self, collection):
        """drop collection from mongo db
        Args:
            Collection: collection name to be dropped
           
        Returns:
            True if drop is successful else False"""

        if self.checkExistence_COL(collection):
            logging.debug('drop collection found in DB')
            try:
                logging.debug('drop collection from mongo db')
                self.collection = self.db[collection]
                self.collection.drop()
            except Exception as e:
                logging.critical('error in drop collection from mongo db %s', e)
                return False
            logging.debug('drop collection from mongo db successful')
            return True
        else:
            logging.error('collection not present in the database')
            return 'collection not present in the database'

    def drop_database(self, db):
        """drop database from mongo db
        Args:
            Collection: database name to be dropped
           
        Returns:
            True if drop is successful else False
        """
        if self.checkExistence_DB(db):
            logging.debug('drop database found in DB')
            try:
                logging.debug('drop database from mongo db')
                self.conn.drop_database(db)
            except Exception as e:
                logging.critical('error in drop database from mongo db %s', e)
                return False
            logging.debug('drop database from mongo db successful')
            return True
        else:
            logging.error('database not present in the database')
            return 'database not present in the database'

    def close_connection(self):
        '''close connection with mongo db'''
        logging.debug('close connection with mongo db')
        try:
            self.conn.close()
        except Exception as e:
            logging.critical('error in close connection with mongo db %s', e)
            return False
        logging.debug('close connection with mongo db successful')
        return True

    if __name__ == '__main__':
        pass
