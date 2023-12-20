# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:14:41
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-20 11:41:49

import config # noqa
import common.message_broker.schemas as PikaSchemas


class Context:

    subscriptions = {}

    def add_subscription(
        self, subscription: PikaSchemas.GeofencingSubscription
    ):
        if subscription.simulation_id not in self.subscriptions:
            self.subscriptions[subscription.simulation_id] = [subscription]
        else:
            self.subscriptions[subscription.simulation_id].append(subscription)

    def get_subscriptions(self, simulation_id: int):
        return self.subscriptions[simulation_id]

    def remove_subscriptions(self, simulation_id: int):
        # Todo: Implement Later
        pass
