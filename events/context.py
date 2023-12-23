# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:14:41
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 16:59:44

import config # noqa
import logging


class Context:

    subscriptions = {}

    def add_subscription(
        self, subscription
    ):
        if subscription.simulation_id not in self.subscriptions:
            self.subscriptions[subscription.simulation_id] = [subscription]
        else:
            if subscription not in \
                    self.subscriptions[subscription.simulation_id]:
                self.subscriptions[subscription.simulation_id].append(
                    subscription
                )
        logging.info(
            "A new subscription has been added to simulation " +
            f"{subscription.simulation_id}: ({subscription})"
        )

    def get_subscriptions(self, simulation_id: int):
        return self.subscriptions.get(simulation_id)

    def remove_subscription(self, subscription):
        if subscription.simulation_id in self.subscriptions:
            if subscription in self.subscriptions[subscription.simulation_id]:
                self.subscriptions[subscription.simulation_id].remove(
                    subscription
                )
                logging.info(
                    "A subscription has been removed from simulation " +
                    f"{subscription.simulation_id}: ({subscription})"
                )
