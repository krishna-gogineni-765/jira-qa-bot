from src.utils.metaclasses import Singleton


class IntegrationStore(metaclass=Singleton):
    def __init__(self):
        self.db = {}

    def add_integration(self, integration_id, integration):
        self.db[integration_id] = integration

    def get_integration(self, integration_id):
        return self.db.get(integration_id)

    def delete_integration(self, integration_id):
        del self.db[integration_id]

    def get_all_integrations(self):
        if not self.db:
            return []
        return self.db.keys()
