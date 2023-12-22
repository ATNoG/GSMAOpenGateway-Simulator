# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 19:04:36
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-21 21:09:28
import pytest
from unittest.mock import call
import config # noqa
from datetime import datetime, timedelta
from geofencing_subscriptions_manager import GeofencingSubscriptionsManager
from common.subscriptions.subscription_types import SubscriptionType
from common.simulation.simulation_types import SimulationType
from notifications import Notifications
from common.message_broker.schemas import (
    SimulationData,
    GeofencingSubscription,
    DeviceLocationSimulationData
)
from common.apis.device_location_schemas import (
    SubscriptionEventType,
    Circle,
    Webhook,
    Point
)


def get_simulated_data():
    strftime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    return [
        SimulationData(
            simulation_id=1,
            child_simulation_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                latitude=32.67809867905849,
                longitude=-17.622633942472735,
                timestamp=datetime.utcnow().strftime(strftime_format)
            )
        ),
        SimulationData(
            simulation_id=1,
            child_simulation_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                latitude=32.77298854063671,
                longitude=-17.13037010791792,
                timestamp=datetime.utcnow().strftime(strftime_format)
            )
        ),
        SimulationData(
            simulation_id=1,
            child_simulation_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                latitude=32.44551578131866,
                longitude=-17.259338468442383,
                timestamp=datetime.utcnow().strftime(strftime_format)
            )
        ),
        SimulationData(
            simulation_id=1,
            child_simulation_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                latitude=32.69540592103866,
                longitude=-16.99218572668454,
                timestamp=datetime.utcnow().strftime(strftime_format)
            )
        ),
        SimulationData(
            simulation_id=1,
            child_simulation_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                latitude=32.73397576083184,
                longitude=-16.824103575407136,
                timestamp=datetime.utcnow().strftime(strftime_format)
            )
        ),
        SimulationData(
            simulation_id=1,
            child_simulation_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                latitude=32.316487028304884,
                longitude=-16.50248551307069,
                timestamp=datetime.utcnow().strftime(strftime_format)
            )
        )
    ]


def test_if_area_related_events_are_being_triggered(mocker):
    area_entered_geofencing_subscription = GeofencingSubscription(
        subscription_id="1",
        subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
        simulation_id=1,
        area=Circle(
            center=Point(
                latitude=32.74513588903821,
                longitude=-17.0078912128889
            ),
            radius=22.84*1000
        ),
        geofencing_subscription_type=SubscriptionEventType.AREA_ENTERED,
        ue=1,
        webhook=Webhook(
            notification_url='https://webhook.site/44623dab-5634-46cc-a5ff-' +
            'd9f1828057e8',
            notification_auth_token='c8974e592c2fa383d4a3960714'
        ),
        expire_time=datetime.utcnow() + timedelta(minutes=2),
    )

    area_left_geofencing_subscription = GeofencingSubscription(
        subscription_id="2",
        subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
        simulation_id=1,
        area=Circle(
            center=Point(
                latitude=32.74513588903821,
                longitude=-17.0078912128889
            ),
            radius=22.84*1000
        ),
        geofencing_subscription_type=SubscriptionEventType.AREA_LEFT,
        ue=1,
        webhook=Webhook(
            notification_url='https://webhook.site/44623dab-5634-46cc-a5ff-' +
            'd9f1828057e8',
            notification_auth_token='c8974e592c2fa383d4a3960714'
        ),
        expire_time=datetime.utcnow() + timedelta(minutes=2),
    )

    simulated_data = get_simulated_data()

    # Expected behavior
    # UE Positions
    # 1 -> Outside Area (area-left)
    # 2 -> Inside Area (area-entered)
    # 3 -> Outside Area (area-left)
    # 4 -> Inside Area (area-entered)
    # 5 -> Inside Area
    # 6 -> Outside Area (area-left)

    # Expected notifications
    # 2 area-entered
    # 3 area-left
    # 5 in total

    # Set mocks
    notifications_mock = mocker.patch(
        target="notifications.Notifications.send_and_record_notification",
        return_value=True
    )

    # Create Geofencing Subscriptions Manager
    geo_subs_manager = GeofencingSubscriptionsManager()

    # Add two test subscriptions
    geo_subs_manager.add_subscription(area_entered_geofencing_subscription)
    geo_subs_manager.add_subscription(area_left_geofencing_subscription)

    # Simualte that UE device location simulation data is arriving
    for simulation_data in simulated_data:
        geo_subs_manager.handle_ue_location_message(
            simulation_data=simulation_data
        )

    # Assert that the noficiation method was called 5 times
    assert notifications_mock.call_count == 5

    # Assert the order of the different calls to that method
    expected_calls = [
        call(area_left_geofencing_subscription),
        call(area_entered_geofencing_subscription),
        call(area_left_geofencing_subscription),
        call(area_entered_geofencing_subscription),
        call(area_left_geofencing_subscription)
    ]
    notifications_mock.assert_has_calls(
        expected_calls, any_order=False
    )


@pytest.mark.parametrize(
    'subscription, expected_return',
    [
        (
            GeofencingSubscription(
                subscription_id="1",
                subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
                simulation_id=1,
                area=Circle(
                    center=Point(
                        latitude=32.74513588903821,
                        longitude=-17.0078912128889
                    ),
                    radius=22.84*1000
                ),
                geofencing_subscription_type=SubscriptionEventType
                .AREA_ENTERED,
                ue=1,
                webhook=Webhook(
                    notification_url='https://webhook.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow(),
            ),
            True
        ),
        (
            GeofencingSubscription(
                subscription_id="2",
                subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
                simulation_id=1,
                area=Circle(
                    center=Point(
                        latitude=32.74513588903821,
                        longitude=-17.0078912128889
                    ),
                    radius=22.84*1000
                ),
                geofencing_subscription_type=SubscriptionEventType
                .AREA_ENTERED,
                ue=1,
                webhook=Webhook(
                    notification_url='https://aklsjdklh.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow(),
            ),
            False
        )
    ]
)
def test_if_area_related_events_notifications(subscription, expected_return):
    ret = Notifications.send_and_record_notification(subscription)
    assert ret == expected_return
