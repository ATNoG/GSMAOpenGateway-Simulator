# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:22:15
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-20 14:36:32
import config # noqa
import logging
from common.message_broker.schemas import (
    SimulationData,
    GeofencingSubscription
)
from subscriptions_manager import SubscriptionsManager
from common.apis.device_location_schemas import (
    SubscriptionEventType,
    VerificationResult
)
from common.helpers import device_location as DeviceLocationHelper
from notifications import Notifications


class GeofencingSubscriptionsManager(SubscriptionsManager):

    def __init__(self):
        super().__init__()

    def handle_ue_location_message(self, simulation_data: SimulationData):

        simulation_instance = simulation_data.simulation_id
        
        for subscription in self.get_subscriptions(simulation_instance):
            if subscription.geofencing_subscription_type == \
                SubscriptionEventType.AREA_ENTERED:
                self.has_ue_entered_geofence(simulation_data, subscription)
            elif subscription.geofencing_subscription_type == \
            SubscriptionEventType.AREA_LEFT:
                self.has_ue_left_geofence(simulation_data, subscription)
            elif subscription.geofencing_subscription_type == \
            SubscriptionEventType.SUBSCRIPTION_ENDS:
                #TODO: Implement Later
                pass

    def has_ue_entered_geofence(
        self, simulation_data: SimulationData,
        subscription: GeofencingSubscription
    ):
        # Get UE Position Circle and the subscription desirable area
        ue_area, subscription_desired_area = \
            self.parse_ue_and_subscription_area_to_shapely_polygons(
                simulation_data=simulation_data,
                subscription=subscription
            )

        # We consider that a UE entered a given are if it is fully inside that
        # area of partially inside it
        ue_inside_geofence = DeviceLocationHelper\
            .compute_location_verification_result(
                device=ue_area,
                area=subscription_desired_area
            ).verification_result in [
                VerificationResult.TRUE,
                VerificationResult.PARTIAL
            ]

        if ue_inside_geofence:
            logging.info(
                f"UE {simulation_data.data.ue} is INside the are defined " +
                f"by the subscription {subscription.subscription_id}"
            )
            self.send_notification_if_needed(subscription, "IN")

        # Update UE Geofencing subscription status
        subscription.ue_inside_geofence = ue_inside_geofence

    def has_ue_left_geofence(
        self, simulation_data: SimulationData,
        subscription: GeofencingSubscription
    ):
        # Get UE Position Circle and the subscription desirable area
        ue_area, subscription_desired_area = \
            self.parse_ue_and_subscription_area_to_shapely_polygons(
                simulation_data=simulation_data,
                subscription=subscription
            )
        # We consider that a UE entered a given are if it is fully inside that
        # area of partially inside it
        ue_inside_geofence = DeviceLocationHelper\
            .compute_location_verification_result(
                device=ue_area,
                area=subscription_desired_area
            ).verification_result in [
                VerificationResult.TRUE,
                VerificationResult.PARTIAL
            ]

        if not ue_inside_geofence:
            logging.info(
                f"UE {simulation_data.data.ue} is OUTside the are defined " +
                f"by the subscription {subscription.subscription_id}"
            )
            self.send_notification_if_needed(subscription, "OUT")

        # Update UE Geofencing subscription status
        subscription.ue_inside_geofence = ue_inside_geofence

    def send_notification_if_needed(
        self, subscription: GeofencingSubscription, ue_location: str
    ) -> bool:
        # Here we assume that the UE last position was uknown
        if subscription.ue_inside_geofence is None:
            subscription.ue_inside_geofence = ue_location == "IN"
            Notifications.send_and_record_notification(subscription)

        # subscription.ue_inside_geofence points to the last relative position
        # of the UE in regard to the geofence
        if (
            (ue_location == "IN" and not subscription.ue_inside_geofence)
            or
            (ue_location == "OUT" and subscription.ue_inside_geofence)
        ):
            Notifications.send_and_record_notification(subscription)

    def parse_ue_and_subscription_area_to_shapely_polygons(
        self, simulation_data: SimulationData,
        subscription: GeofencingSubscription
    ):
        # Get UE Position Circle
        ue_area = DeviceLocationHelper\
            .shapely_circle_from_coordinates_circle_without_radius(
                center_latitude=simulation_data.data.latitude,
                center_longitude=simulation_data.data.longitude
            )

        # Get the subscription desirable area
        subscription_desired_area = DeviceLocationHelper\
            .shapely_polygon_from_area(
                area=subscription.area
            )

        return ue_area, subscription_desired_area
