# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:21:40
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-20 14:50:39

import requests
import requests.exceptions
import config # noqa
import logging


class Notifications:

    @staticmethod
    def send_and_record_notification(subscription):

        logging.info(
            "Sending notification to " +
            f"{subscription.webhook.notification_url}. This notification " +
            "is realated with a " +
            f"{subscription.geofencing_subscription_type.value} event."
        )
        try:
            response = requests.post(
                url=subscription.webhook.notification_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " +
                    subscription.webhook.notification_auth_token
                },
                timeout=15
            )
            # Raises an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            logging.info(
                f"Notification to {subscription.webhook.notification_url} " +
                "was successful."
            )
            # Store results in DB
            Notifications.store_notification_output_in_db(
                subscription=subscription,
                error_message=None
            )
            return True

        except Exception as exception:
            logging.error(
                    "Error on sending notification to " +
                    subscription.webhook.notification_url +
                    f". Reason: {exception}."
                )
            # Store results in DB
            Notifications.store_notification_output_in_db(
                subscription=subscription,
                error_message=str(exception)
            )
            return False

    @staticmethod
    def store_notification_output_in_db(subscription, error_message):
        # if error message -> notification unsuccessful
        # if no error message -> notification successful

        # Todo: Call DB CRUD methods
        pass
