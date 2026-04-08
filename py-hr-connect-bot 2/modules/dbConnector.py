class mongoConnector:
    from pymongo import MongoClient

    def __init__(self, connectionString, db, poolSize = 5) -> None:
        self.CLIENT = self.MongoClient(connectionString, maxPoolSize=poolSize)
        self.DB = self.CLIENT[db]
        
        pass

    def find(self, collection, q):
        r = self.DB[collection].find(q)

        return list(r)
    
