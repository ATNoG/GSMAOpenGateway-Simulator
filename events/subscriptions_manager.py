# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:22:15
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 21:43:03
from common.database import connections_factory as DBFactory
from notifications import Notifications
from datetime import datetime


class SubscriptionsManager:

    def __init__(self):
        self.last_subscriptions_update_timestamp = datetime.utcnow()
        self.active_subscriptions = []
        self.has_looked_for_subscriptions = False
        self.db = DBFactory.new_db_session()
        self.notifications = Notifications(
            db=self.db
        )

    def get_subscriptions(self, root_simulation_id):
        # Should be implemented in the child classes
        pass
