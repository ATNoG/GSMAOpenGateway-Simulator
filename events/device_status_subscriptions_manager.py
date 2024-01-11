# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:22:15
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 14:29:05
import config # noqa
import logging
from common.message_broker.schemas import SimulationData, SubscriptionType
from common.subscriptions.schemas import DeviceStatusSubscription
from subscriptions_manager import SubscriptionsManager
from common.apis.device_status_schemas import (
    SubscriptionEventType,
    ConnectivityStatus,
    Webhook
)
from datetime import datetime, timedelta
import json
from common.database import crud


class DeviceStatusSubscriptionsManager(SubscriptionsManager):

    def __init__(self):
        super().__init__()

    def handle_ue_status_message(self, simulation_data: SimulationData):

        # CLEANUP
        if "stop" in simulation_data.data:
            i = len(self.active_subscriptions) - 1
            while i >= 0:
                if self.active_subscriptions[i].simulation_id == \
                        simulation_data.simulation_id:
                    logging.info(
                        "Will delete Simulation: " +
                        f"({self.active_subscriptions[i]})."
                    )
                    del self.active_subscriptions[i]

                i -= 1
            return

        for subscription in self.get_subscriptions(
            simulation_data.simulation_id
        ):
            # Only consider the simulations that relate with the current UE
            # Only considered not expired subscriptions
            if (
                simulation_data.data["ue"] != subscription.ue
                or
                datetime.utcnow() > subscription.expire_time
            ):
                continue  # SKIP

            if subscription.device_status_subscription_type in [
                SubscriptionEventType.CONNECTIVITY_SMS,
                SubscriptionEventType.CONNECTIVITY_DATA,
                SubscriptionEventType.CONNECTIVITY_DISCONNECTED
            ]:
                self.process_connectivity_status_subscription(
                     simulation_data, subscription,
                )

            elif subscription.device_status_subscription_type in [
                SubscriptionEventType.ROAMING_ON,
                SubscriptionEventType.ROAMING_OFF,
            ]:
                self.process_roaming_subscription(
                     simulation_data, subscription,
                )

            elif subscription.device_status_subscription_type == \
                    SubscriptionEventType.ROAMING_STATUS:
                self.process_roaming_change_subscription(
                     simulation_data, subscription,
                )

            elif subscription.device_status_subscription_type == \
                    SubscriptionEventType.ROAMING_CHANGE_COUNTRY:
                self.process_roaming_country_code_change_subscription(
                     simulation_data, subscription,
                )

            # Finally, update the subscription data
            self.update_subscription(simulation_data, subscription)
            
    def update_subscription(
        self, simulation_data: SimulationData,
        subscription: DeviceStatusSubscription,
    ):
        if simulation_data.data["connectivity_status"] is not None:
            subscription.current_connectivity_status = simulation_data.data[
                "connectivity_status"
            ]

        if simulation_data.data["roaming"] is not None:
            subscription.current_roaming = simulation_data.data[
                "roaming"
            ]
        if simulation_data.data["country_code"] is not None:
            subscription.current_country_code = simulation_data.data[
                "country_code"
            ]
        if simulation_data.data["country_name"] is not None:
            subscription.current_country_name = simulation_data.data[
                "country_name"
            ]

    def process_connectivity_status_subscription(
        self, simulation_data: SimulationData,
        subscription: DeviceStatusSubscription,
    ):
        # Get the target connectivity status from subscription
        connectivity_status = self.map_subscription_to_connectivity_status(
            subscription.device_status_subscription_type
        )

        if (
            simulation_data.data["connectivity_status"] == connectivity_status
            .value
            and
            simulation_data.data["connectivity_status"] != subscription
            .current_connectivity_status
        ):
            # Send notification
            # But update it before sending the notification
            self.update_subscription(simulation_data, subscription)
            self.notifications.send_and_record_device_status_notification(
                subscription=subscription
            )

    def process_roaming_subscription(
        self, simulation_data: SimulationData,
        subscription: DeviceStatusSubscription,
    ):
        # Get the target roaming status from subscription
        roaming_status = True \
            if subscription.device_status_subscription_type \
            == SubscriptionEventType.ROAMING_ON \
            else False

        if (
            simulation_data.data["roaming"] == roaming_status
            and
            simulation_data.data["roaming"] != subscription
            .current_roaming
        ):
            # Send notification
            # But update it before sending the notification
            self.update_subscription(simulation_data, subscription)
            self.notifications.send_and_record_device_status_notification(
                subscription=subscription
            )

    def process_roaming_change_subscription(
        self, simulation_data: SimulationData,
        subscription: DeviceStatusSubscription,
    ):
        # Simulation data must contain a roaming status
        if simulation_data.data["roaming"] is not None:
            if simulation_data.data["roaming"] != subscription.current_roaming:
                # Send notification
                # But update it before sending the notification
                self.update_subscription(simulation_data, subscription)
                self.notifications.send_and_record_device_status_notification(
                    subscription=subscription
                )

    def process_roaming_country_code_change_subscription(
        self, simulation_data: SimulationData,
        subscription: DeviceStatusSubscription,
    ):
        # Simulation data must contain a roaming status
        if simulation_data.data["country_code"] is not None:
            if simulation_data.data["country_code"] != \
                    subscription.current_country_code:
                # Send notification
                # But update it before sending the notification
                self.update_subscription(simulation_data, subscription)
                self.notifications.send_and_record_device_status_notification(
                    subscription=subscription
                )

    def map_subscription_to_connectivity_status(
        self, subs_event_type: SubscriptionEventType
    ):
        if subs_event_type == SubscriptionEventType.CONNECTIVITY_DISCONNECTED:
            return ConnectivityStatus.NOT_CONNECTED
        elif subs_event_type == SubscriptionEventType.CONNECTIVITY_SMS:
            return ConnectivityStatus.CONNECTED_SMS
        elif subs_event_type == SubscriptionEventType.CONNECTIVITY_DATA:
            return ConnectivityStatus.CONNECTED_DATA

    def get_subscriptions(self, root_simulation_id):

        if (
            not self.has_looked_for_subscriptions
            or
            self.last_subscriptions_update_timestamp + timedelta(seconds=5) <
                datetime.utcnow()
        ):
            self.has_looked_for_subscriptions = True

            logging.info(
                "Will collect the most recent subscriptions for Root " +
                f"Simulation {root_simulation_id}..."
            )

            # Update the last subscriptions update timestamp
            self.last_subscriptions_update_timestamp = datetime.utcnow()

            # Store the current active subscriptions
            current_active_subscriptions = []

            for sub in crud\
                .get_active_device_status_subscriptions_for_root_simulation(
                    db=self.db,
                    root_simulation_id=root_simulation_id
                    ):

                # Get the Simulated UE Instance
                simulated_ue_instance = crud\
                    .get_device_instance_based_on_simulated_ue(
                        db=self.db,
                        root_simulation_id=root_simulation_id,
                        simulated_ue_id=sub.ue
                    )

                # Get simulation instance
                simulation_instance = crud\
                    .get_last_simulation_instance_from_root_simulation(
                        db=self.db,
                        root_simulation_id=root_simulation_id
                    )

                # Get initial simulation datae
                device_status_data = crud.get_last_device_status_entry(
                    db=self.db,
                    simulation_instance=simulation_instance.id,
                    ue_id=simulated_ue_instance.id
                )

                current_active_subscriptions.append(
                    DeviceStatusSubscription(
                        simulation_id=root_simulation_id,
                        subscription_id=sub.id,
                        subscription_type=SubscriptionType
                        .DEVICE_STATUS,
                        device_status_subscription_type=sub.subscription_type,
                        ue=sub.ue,
                        webhook=Webhook(
                            notificationUrl=sub.webhook_url,
                            notificationAuthToken=sub.webhook_auth_token
                        ),
                        expire_time=sub.expire_time,
                        current_connectivity_status=device_status_data
                        .connectivity_status,
                        current_country_code=device_status_data.country_code,
                        current_roaming=device_status_data.roaming,
                        current_country_name=json.loads(
                            device_status_data.country_name
                        )
                    )
                )

            # Check if the simulation is already loaded or not
            loaded_subscriptions_ids = [
                sub.subscription_id
                for sub
                in self.active_subscriptions
            ]

            for current_active_subscription in current_active_subscriptions:
                # Add a new subscription
                if current_active_subscription.subscription_id not in \
                        loaded_subscriptions_ids:
                    self.active_subscriptions.append(
                        current_active_subscription
                    )

            return self.active_subscriptions
