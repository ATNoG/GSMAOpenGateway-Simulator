# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:22:15
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 10:26:31
from context import Context


class SubscriptionsManager:

    context = Context()

    def add_subscription(self, subscription):
        self.context.add_subscription(subscription)

    def get_subscriptions(self, simulation_id):
        return self.context.get_subscriptions(simulation_id)

    def remove_subscription(self, subscription):
        self.context.remove_subscription(subscription)
