class MongoSqlStatement:
    def query_batch_oiltank_endpoint(self, dao, cretia):
        des_df = dao.read({}, collection='batch_oiltank_endpoint')
        return None


class MsSqlStatement:
    def query_batch_oiltank_endpoint(self, dao):
        pass
