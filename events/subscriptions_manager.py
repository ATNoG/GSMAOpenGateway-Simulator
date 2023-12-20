# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:22:15
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-20 11:40:20
from context import Context


class SubscriptionsManager:

    context = Context()

    def add_subscription(self, subscription):
        self.context.add_subscription(subscription)

    def get_subscriptions(self, simulation_id):
        return self.context.get_subscriptions(simulation_id)

    def remove_subscriptions(self, simulation_id):
        self.context.remove_subscriptions(simulation_id)
