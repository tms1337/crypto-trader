import time

from bot.util.asserting import TypeChecker
from pymongo import MongoClient
from retrying import retry

from bot.strategy.pipeline.monitoring.infomonitor import InfoMonitor
from util.logging import LoggableMixin

mongo_balance_monitor_max_retry_attempts = None

class MongoBalanceMonitor(InfoMonitor, LoggableMixin):
    def __init__(self,
                 currencies,
                 name,
                 host="localhost",
                 port=27017,
                 db_name="db",
                 retry_attempts=3):
        TypeChecker.check_type(currencies, list)
        for c in currencies:
            TypeChecker.check_type(c, str)
        self.currencies = currencies

        TypeChecker.check_type(name, str)
        self.name = name

        self.mongo_client = MongoClient(host=host, port=port)

        TypeChecker.check_type(db_name, str)
        self.db_name = db_name

        TypeChecker.check_type(retry_attempts, int)
        global mongo_balance_monitor_max_retry_attempts
        mongo_balance_monitor_max_retry_attempts = retry_attempts

        LoggableMixin.__init__(self, MongoBalanceMonitor)

    def notify(self, monitored_data):
        super(MongoBalanceMonitor, self).notify(monitored_data)

        try:
            self._save_balance_record()
        except:
            self.logger.error("Could not save record")

    @retry(stop_max_attempt_number=mongo_balance_monitor_max_retry_attempts)
    def _save_balance_record(self):
        db = self.mongo_client[self.db_name]
        balance_records = db[self.name]

        informer = self.monitored_data
        record = {"time": time.time()}

        balance_matrix = informer.get_balances_matrix()
        stats_matrix = informer.get_stats_matrix()
        for e in balance_matrix.all_exchanges():
            for c in balance_matrix.all_currencies():
                assert e in stats_matrix.all_exchanges(), "Exchange %s not in "
                assert c in stats_matrix.all_currencies()

                if c not in record:
                    record[c] = 0
                value = balance_matrix.get(e, c).value

                record[c] += value

        balance_records.insert_one(record)
