# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 10:54:41
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-08 10:36:03
# coding: utf-8

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from routers.location_retrieval_api import router \
    as LocationRetrievalApiRouter
from routers.location_verification_api import router\
    as LocationVerificationApiRouter
from routers.geofencing_api import router\
    as GeofencingApiRouter
from routers.sim_swap_api import router\
    as SimSwapRouter
from routers.simulation_api import router\
    as SimulationApiRouter
from routers.simple_edge_discovery_api import router\
    as SimpleEdgeDiscoveryApiRouter
from routers.device_status_api import router\
    as DeviceStatusApiRouter
import config # noqa

open_api_json_path = "/openapi.json"
docs_path = "/docs"
redoc_path = "/redoc"

device_location_retrieval_app_prefix = "/location-retrieval/v0"
device_location_verification_app_prefix = "/location-verification/v0"
device_location_geofencing_app_prefix = "/geofencing/v0"
sim_swap_app_prefix = "/sim-swap/v0"
simple_edge_discovery_app_prefix = "/eds/v0"
device_status_app_prefix = "/device-status/v0"
simulation_app_prefix = "/simulation"

##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                           Location Retrieval API                           #
#                                                                            #
##############################################################################

simulation_app = FastAPI(
    title="GSMA Open Gateway Simulation API",
    description=(
        "Simulation API"
    ),
    version="0.0.1",
    openapi_url=simulation_app_prefix + open_api_json_path,
    docs_url=simulation_app_prefix + docs_path,
    redoc_url=simulation_app_prefix + redoc_path,
)

simulation_app.include_router(
    router=SimulationApiRouter,
    prefix=simulation_app_prefix
)


##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                           Location Retrieval API                           #
#                                                                            #
##############################################################################

device_location_retrieval_app = FastAPI(
    title="Location retrieval API",
    description=(
        "This API provides the ability to retrieve a device location.\n\n"
        "# Introduction\n\n"
        "With this API, customers can retrieve the area where a certain "
        "user device is localized. The area provided in the response "
        "could be described:\n\n"
        "- by a circle determined by coordinates (latitude and longitude) "
        "and a radius.\n"
        "- by a simple polygon delimited by segments connecting consecutively "
        "an array of coordinates (points). The last point connects to the "
        "first point to delimit a closed shape bounded with straight sides."
        "\n\n"
        "The retrieved shape depends on the network conditions at the "
        "subscriber's  location and any of the supported shapes could be "
        "received.\n\n"
        "The requester could optionally ask for a freshness of the "
        "localization information by providing a maxAge (\"I want a location "
        "not older than 600 seconds\").\n\n"
        "The result accuracy depends on the network's ability and accuracy "
        "to locate the device.\n\n"
        "Additionally to location information, the answer will also provide "
        "indication about the location time.\n\n"
        "Location retrieval API could be useful in scenarios such as:\n\n"
        "- Fraud protection to ensure a given user is located in the region, "
        "country or location authorized for financial transactions\n"
        "- Verify the GPS coordinates reported by the app on a device to "
        "ensure the GPS was not faked e.g. for content delivery with regional "
        "restrictions\n"
        "- Location-based advertising: trigger targeted advertising after "
        "retrieving the area where the user is localized\n"
        "- Smart Mobility (Vehicle/bikes renting): obtain the location of a "
        "vehicle/bike to guarantee they are rented correctly\n\n"
        "**Note**: Location is in most jurisdictions considered to be "
        "sensitive data and thereby consent by device owner/user must be "
        "verified before providing it to the developer.\n\n"
        "# Relevant terms and definitions\n\n"
        "* **Device**: A device refers to any physical entity that can "
        "connect to a network and participate in network communication.\n"
        "* **Area**: It specifies the geographical surface where a device "
        "may be physically located.\n"
        "* **Max Age**: Maximum age of the location information which is "
        "accepted for the location retrieval (in seconds).\n"
        "* **Last Location Time** : Last date and time when the device was "
        "localized.\n\n"
        "# API Functionality\n\n"
        "The API exposes a single endpoint/operation:\n\n"
        "- `/retrieve` : Retrieve where the device is localized.\n"
        "The operation returns:\n"
        "  * a localization defined with a circle with center specified by "
        "the latitude and longitude, and radius for answer accuracy,\n"
        "  * a timestamp about location information freshness.\n\n"
        "# Further info and support\n\n"
        "(FAQs will be added in a later version of the documentation)"
    ),
    version="0.1.0-wip",
    openapi_url=device_location_retrieval_app_prefix + open_api_json_path,
    docs_url=device_location_retrieval_app_prefix + docs_path,
    redoc_url=device_location_retrieval_app_prefix + redoc_path,
)

device_location_retrieval_app.include_router(
    router=LocationRetrievalApiRouter,
    prefix=device_location_retrieval_app_prefix
)


##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                      Device Location Verification API                      #
#                                                                            #
##############################################################################

device_location_verification_app = FastAPI(
    title="Device location verification API",
    description=(
        "This API provides the customer with the ability to verify "
        "the location of a device.\n\n"
        "# Introduction\n\n"
        "Customers can verify whether the location of a certain user "
        "device is within the specified area. Currently, the only "
        "supported area is a circle determined by provided coordinates "
        "(latitude, longitude) and expected accuracy (radius).\n\n"
        "The verification result depends on the network's ability and "
        "accuracy to locate the device at the requested area.\n\n"
        "* If the network locates the device within the requested area, "
        "the verification result is `TRUE`.\n"
        "* If the requested area does not match the area where the network "
        "locates the device, the verification result is `FALSE`.\n"
        "* If the requested area partially matches the area where the network "
        "locates the device, the verification result is `PARTIAL`. In this "
        "case, a `match_rate` could be included in the response, indicating "
        "an estimation of the likelihood of the match in percent.\n"
        "* If the network is unable to locate the device, the verification "
        "result is `UNKNOWN`.\n\n"
        "Location Verification could be useful in scenarios such as:\n\n"
        "- Fraud protection to ensure a given user is located in the region, "
        "country, or claimed location for financial transactions\n"
        "- Verify GPS coordinates reported by the app on a device to ensure "
        "the GPS was not faked (e.g., for content delivery with regional "
        "restrictions)\n - Location-based advertising: trigger targeted "
        "advertising after verifying  the user is in the area of interest\n"
        "- Smart Mobility (Vehicle/bikes renting): confirm the location of "
        "the device and the location of the vehicle/bike to guarantee they "
        " are rented correctly\n\n# Relevant terms and definitions\n\n"
        "* **Device**: A device refers to any physical entity that can "
        "connect to a network and participate in network communication.\n"
        "* **Area**: Specifies the geographical surface where a device may be "
        "physically located.\n"
        "* **Verification**: Process triggered in the API server to confirm "
        "or contradict the expectation assumed by the API client about the "
        "device location.\n\n"
        "# API Functionality\n\n"
        "The API exposes a single endpoint/operation:\n\n"
        "- Verify whether the device location is within a requested area, "
        "currently a circle with a center specified by latitude and "
        "longitude, and radius specified by accuracy. The operation "
        "returns a verification result and, optionally, a match rate "
        "estimation for the location verification in percent.\n\n"
        "# Further info and support\n\n"
        "(FAQs will be added in a later version of the documentation)"
    ),
    version="0.2.0-wip",
    openapi_url=device_location_verification_app_prefix + open_api_json_path,
    docs_url=device_location_verification_app_prefix + docs_path,
    redoc_url=device_location_verification_app_prefix + redoc_path,
)

device_location_verification_app.include_router(
    router=LocationVerificationApiRouter,
    prefix=device_location_verification_app_prefix
)


##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                       Device Location Geofencing API                       #
#                                                                            #
##############################################################################

device_location_geofencing_app = FastAPI(
    title="Device geofencing API",
    description=(
        "API to create, retrieve, and delete event subscriptions "
        "for geofencing a user device. \n\n# Introduction\n\nWith this "
        "API, customers can create subscriptions for their devices "
        "to receive notifications when a device enters or exits a "
        "specified area.\n\nThe area provided in the request is "
        "described by a circle determined by coordinates (latitude "
        "and longitude) and an accuracy defined by the radius.\n\nUpon "
        "successfully creating a subscription, the API will provide "
        "an Event Subscription ID, and it will indicate the "
        "subscription's expiration date.\n\nIf the geofencing-state of "
        "a device changes, the event subscriber will be notified "
        "back to the provided Notification-Url given by the "
        "subscription-request.\n\nDevice geofencing API could be useful "
        "in scenarios such as:\n\n- Tracking devices for Presetting of "
        "Home-Settings\n\n- Tracking of logistics\n\n# Relevant terms and "
        "definitions\n\n* **Device**: A device refers to any physical "
        "entity that can connect to a network and participate in "
        "network communication.\n\n* **Area**: It specifies the "
        "geographical surface which a device is planned to enter or "
        "exit.\n\n# API Functionality\n\nThe API exposes the following "
        "capabilities:\n\n## Device Geofencing subscription\n\nThese "
        "endpoints allow managing event subscription on geofencing "
        "device location event.\n\nThe CAMARA subscription model is "
        "detailed in the CAMARA API design guideline document and "
        "follows CloudEvents specification.\n\nIt is mandatory in the "
        "subscription to provide the event `type` for which the "
        "client would like to subscribe.\n\nFollowing event`type` are "
        "managed for this API:\n\n- "
        "`org.camaraproject.geofencing.v0.area-entered` - Event "
        "triggered when the device enters the given area\n\n- "
        "`org.camaraproject.geofencing.v0.area-left` - Event "
        "triggered when the device leaves the given area\n\nNote: "
        "Additionally to these lists, "
        "`org.camaraproject.geofencing.v0.subscription-ends` "
        "notification `type` is sent when the subscription ends. "
        "This notification does not require a dedicated subscription. "
        "It is used when the subscription expiration time (required "
        "by the requester) has been reached or if the API server has "
        "to stop sending notification prematurely.\n\n### Notification "
        "callback\n\nThis endpoint describes the event notification "
        "received on the subscription listener side when the event "
        "occurred. As for the subscription, detailed description of "
        "the event notification is provided in the CAMARA API design "
        "guideline document.\n\n**WARNING**: This callback endpoint "
        "must be exposed on the consumer side as "
        "`POST /{$request.body#/webhook/notificationUrl}`. Developers "
        "may provide a callback URL on which notifications regarding "
        "geofencing can be received from the service provider. If an "
        "event occurs, the application will send events to the "
        "provided webhook - 'notificationUrl'.\n\n# Further info and "
        "support\n\n(FAQs will be added in a later version of the "
        "documentation)\n\n"
        "[Terms of service](http://swagger.io/terms/?_ga=2.111714564.1249190"
        "960.1703280247-990327894.1703280247)\n\n"
        "[Contact the developer](mailto:project-email@sample.com)\n\n"
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.html)\n\n"
        "[Product documentation at Camara](https://github.com/camaraproject"
        "/)\n\n"
    ),
    version="0.1.0-rc",
    openapi_url=device_location_geofencing_app_prefix + open_api_json_path,
    docs_url=device_location_geofencing_app_prefix + docs_path,
    redoc_url=device_location_geofencing_app_prefix + redoc_path,
)

device_location_geofencing_app.include_router(
    router=GeofencingApiRouter,
    prefix=device_location_geofencing_app_prefix
)

##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                                SIM Swap API                                #
#                                                                            #
##############################################################################


sim_swap_app = FastAPI(
    title="SIM Swap",
    description=(
        "SIM Swap API provides the customer the ability to "
        "obtain information on any recent SIM pairing change "
        "related to the User's mobile account.\n\nThis API derives "
        "from the GSMA Mobile Connect Account Takeover Protection "
        "specification [Mobile Connect Account Takeover Protection]"
        "(https://www.gsma.com/identity/wp-content/uploads/2022/12/"
        "IDY.24-Mobile-Connect-Account-Takeover-Protection-Definition-"
        "and-Technical-Requirements-v2.0.pdf). For more about Mobile "
        "Connect, please see [about Mobile Connect]"
        "(https://mobileconnect.io/).\n\nThe API provides 2 operations: "
        "\n\n- POST retrieve-date : Provides timestamp of latest SIM swap "
        "\n\n- POST check: Checks if SIM swap has been performed during a "
        "past period (defined in the request with 'maxAge' attribute).\n\n"
        "[Terms of service](http://swagger.io/terms/)\n\n"
        "[Contact the developer](mailto:project-email@sample.com)\n\n"
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.html)\n\n"
        "[Product documentation at Camara](https://github.com/camaraproject"
        "/)\n\n"
    ),
    version="0.4.0",
    openapi_url=sim_swap_app_prefix + open_api_json_path,
    docs_url=sim_swap_app_prefix + docs_path,
    redoc_url=sim_swap_app_prefix + redoc_path,
)

sim_swap_app.include_router(
    router=SimSwapRouter,
    prefix=sim_swap_app_prefix
)


##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                          Simple Edge Discovery API                         #
#                                                                            #
##############################################################################

simple_edge_discovery_app = FastAPI(
    title="Simple Edge Discovery API",
    description=(
        "# Find the closest MEC platform\n\n---\n\n# Summary\n\nThe Simple "
        "Edge Discovery API returns the name of the closest operator MEC "
        "platform to a particular user device.\n\n# Purpose\n\nNetwork "
        "operators may host multiple Multi-access Edge Computing (MEC, "
        "or &#39;Edge&#39;) platforms in a given territory. Connecting "
        "your application to a server on the closest MEC platform means "
        "packets travel the shortest distance between endpoints, "
        "typically resulting in the lowest round-trip latency. Note, the "
        "physical (GPS) location of a user device is not a reliable way "
        "to determine the closest MEC platform, due to the way operator "
        "networks are routed - so the operator will calculate the MEC "
        "platform with the  _shortest network path_ to the "
        "network-attached device identified in the API request.\n\nOnce "
        "you have the name of the closest MEC platform to the user "
        "device, you may:\n\n* connect the application client on the user "
        "device to your application server instance on that MEC "
        "platform. Note: the address of that server instance is not "
        "part of the API response, but should be known in advance.\n\n* or, "
        "if you have no instance on that MEC platform, you may wish to "
        "deploy one there.\n\n# Usage\n\nThe API may be called either by "
        "an application client hosted on a device attached to the "
        "operator network (i.e. phone, tablet), or by a server.\n\nThere "
        "is a single API endpoint: `/mecplatforms?filter=closest`. "
        "To call this endpoint, the API consumer must "
        "first obtain a valid OAuth2 token from the token endpoint, and "
        "pass it as an `Authorization` header in the API "
        "request.\n\nThe API returns the closest MEC platform to a "
        "given device, so that device needs to be identifiable by the "
        "network:\n\n* if you call the API from a server, you must "
        "explicitly pass one or more device identifiers in the HTTP "
        "request header:\n\n   * `IP-Address`. This is the public "
        "IP address of the user device: this can be obtained by an "
        "application hosted on that device calling a public IP address "
        "API (e.g. GET https://api.ipify.org?format=json)\n\n   * "
        "`Phone-Number` . The international E.164 format "
        "(starting with country code), e.g. +4407123123456\n\n   * "
        "`Network-Access-Identifier` (where available from the "
        "API host operator)\n\n* if you call the API from a device "
        "attached to the operator network, you _may_ omit the explicit "
        "device identifier(s)from the request header. If such a request "
        "fails with a `404 Not Found` error then retry the "
        "request but this time include a device identifier.\n\nThe "
        "provider of the MEC Platform may be an operator, or a cloud "
        "provider.\n\n# Example requests:\n\nExamples for all API "
        "clients:\n\n```\nGET /mec-platforms?filter=closest HTTP/1.1\n"
        "Host: example.com Accept: application/json\n"
        "Network-Access-Identifier: "
        "4d596ac1-7822-4927-a3c5-d72e1f922c94@domain.com\n\n"
        "GET /mec-platforms?filter==closest HTTP/1.1\nHost: "
        "example.com\nAccept: application/json\nIP-Address: 84.125.93.10\n\n"
        "GET /mec-platforms?filter=closest HTTP/1.1\nHost: "
        "example.com\nAccept: application/json\nPhone-Number: "
        "441234567890\n```\n\nExample where API client is on a "
        "network-attached device:\n\n```GET /mec-platforms?filter="
        "closest HTTP/1.1\nHost: example.com\nAccept: application/json\n```"
        "\n\n# Responses \n\n## Success\n\nA JSON object is returned "
        "containing a `MECPlatforms` array with a single member, along with "
        "the HTTP `200 OK` status code. The value of the "
        "`edgeCloudProvider` object is the name of the operator "
        "or cloud provider of the MEC Platform. `edgeResourceName` "
        "object is the name of the closest MEC platform to the user "
        "device. An example of this JSON object is as follows:"
        "\n```\n{\n  \"MecPlatforms\": [\n\t{       "
        "\n\t  \"edgeCloudProvider\": \"AWS\",       "
        "\n\t  \"edgeResourceName\": \"eu-west-2-wl1-man-wlz-1\""
        "\n\t}"
        "\n  ]\n} \n"
        "```\n\n## Errors\n\nIf the authentication token is "
        "not valid, a `401 UNAUTHENTICATED` error is returned\n\n"
        "If the mobile subscription parameters contain a formatting "
        "error, a `400 INVALID_ARGUMENT` error is returned.\n\n"
        "If the mobile subscription cannot be identified from the "
        "provided parameters, a `404 NOT_FOUND` error is "
        "returned.\n\nAny more general service failures will result in an "
        "error in the `5xx`range with an explanation.\n\n# Note "
        "for Simple Edge API publishers\n\nThe API publisher (i.e. the "
        "operator implementation) must ensure that the tuple of "
        "edgeCloudProvider+edgeResourceName in the success reponse is "
        "unique.\n\n# Further info and support\n\n ---\n\n"
        "[Contact the developer](mailto:project-email@sample.com)\n\n"
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.html)\n\n"
        "[Product documentation at Camara](https://github.com/camaraproject"
        "/)\n\n"
    ),
    version="0.9.3",
    openapi_url=simple_edge_discovery_app_prefix + open_api_json_path,
    docs_url=simple_edge_discovery_app_prefix + docs_path,
    redoc_url=simple_edge_discovery_app_prefix + redoc_path,
)

simple_edge_discovery_app.include_router(
    router=SimpleEdgeDiscoveryApiRouter,
    prefix=simple_edge_discovery_app_prefix
)


##############################################################################
#                                                                            #
#                              GSMA Open Gateway                             #
#                            Device Location APIs                            #
#                              Device Status API                             #
#                                                                            #
##############################################################################

device_status_app = FastAPI(
    title="Device Status",
    description=(
        "This API provides the customer with the ability "
        "to query device: - Roaming Status - Connectivity "
        "Status Moreover, this API extends the functionality "
        "by allowing users customers to subscribe to events "
        "associated with these status queries. # Introduction "
        "## Roaming Status API consumer is able to verify "
        "whether a certain user device is in roaming situation "
        "(or not). This capability is provided in 2 ways: - via "
        "direct request with the roaming situation in the "
        "response. - via a subscription request - in this case "
        "the roaming situation is not in the response but event "
        "notification is sent back to the event subscriber when "
        "roaming situation has changed. The verification of the "
        "roaming situation depends on the network's ability. "
        "Additionally to the roaming status, when the device is "
        "in roaming situation, visited country information is "
        "send back in the response. ## Connectivity Status API "
        "consumer is able to verify whether a certain user "
        "device is connected to the network via data- or "
        "sms-usage. This capability is provided in 2 ways: - "
        "via direct request with the connectivity situation in "
        "the response. - via a subscription request - in this "
        "case the connectivity situation is not in the response "
        "but event notification is sent back to the event "
        "subscriber when connectivity situation has changed. ## "
        "Possible Use-Cases Device status verification could be "
        "useful in scenario such as (not exhaustive): - For "
        "regulatory reasons, where a customer may need to be "
        "within a certain jurisdiction, or out with others, in "
        "order for transactions to be authorized - For security "
        "/ fraud reasons, to establish that a customer is "
        "located where they claim to be - For service delivery "
        "reasons, to ensure that the customer has access to "
        "particular service, and will not incur roaming charges "
        "in accessing them # Relevant terms and definitions * "
        "**Device**: A device refers to any physical entity "
        "that can connect to a network and participate in "
        "network communication. At least one identifier for the "
        "device (user equipment) out of four options: IPv4 "
        "address, IPv6 address, Phone number, or Network Access "
        "Identifier assigned by the mobile network operator for "
        "the device. * **Roaming** : Roaming status - `true`, "
        "if device is in roaming situation - `false` else. * "
        "**Country** : Country code and name - visited country "
        "information, provided if the device is in roaming "
        "situation. * **Connectivity** : Connectivity status. - "
        "`CONNECTED_SMS`, if device is connected to the network "
        "via SMS usage - `CONNECTED_DATA`, if device is "
        "connected to the network via data usage' - "
        "`NOT_CONNECTED`, if device is not connected to the "
        "network' # API Functionality The API exposes following "
        "capabilities: ## Device roaming situation The endpoint "
        "`POST /roaming` allows to get roaming status and "
        "country information (if device in roaming situation) "
        "synchronously. ## Device connectivity situation The "
        "endpoint `POST /connectivity` allows to get current "
        "connectivity status information synchronously. ## "
        "Device status subscription These endpoints allow to "
        "manage event subscription on roaming device status "
        "event. The CAMARA subscription model is detailed in "
        "the CAMARA API design guideline document and follows "
        "CloudEvents specification. It is mandatory in the "
        "subscription to provide the event `type` subscribed "
        "are several are managed in this API. Following event "
        "`type` are managed for this API: - "
        "`org.camaraproject.device-status.v0.roaming-status` - "
        "Event triggered when the device switch from roaming ON "
        "to roaming OFF and conversely - "
        "`org.camaraproject.device-status.v0.roaming-on` - "
        "Event triggered when the device switch from roaming "
        "OFF to roaming ON - `org.camaraproject.device-status.v0.roaming-off`"
        ": Event triggered when the device switch from roaming ON "
        "to roaming OFF - "
        "`org.camaraproject.device-status.v0.roaming-change-country`: "
        "Event triggered when the device in roaming change "
        "country code - `org.camaraproject.device-status.v0.connectivity-data`"
        ": Event triggered when the device is connected to the "
        "network for Data usage. - "
        "`org.camaraproject.device-status.v0.connectivity-sms`: "
        "Event triggered when the device is connected to the "
        "network for SMS usage - "
        "`org.camaraproject.device-status.v0.connectivity-disconnected`: "
        "Event triggered when the device is not connected. "
        "Note: Additionally to these list, "
        "`org.camaraproject.device-status.v0.subscription-ends` "
        "notification `type` is sent when the subscription "
        "ends. This notification does not require dedicated "
        "subscription. It is used when the subscription expire "
        "time (required by the requester) has been reached or "
        "if the API server has to stop sending notification "
        "prematurely. ### Notifications callback The "
        "`notifications` callback describes the format of event "
        "notifications and expected responses to the messages "
        "sent when the event occurs. As for subscription, "
        "detailed description of the event notification is "
        "provided in the CAMARA API design guideline document. "
        "**WARNING**: This callback endpoint must be exposed "
        "and reachable on the listener side under "
        "`notificationUrl` defined in the `webhook` attribute. "
        "## Further info and support (FAQs will be added in a "
        "later version of the documentation) "),
    version="0.5.0-rc",
    openapi_url=device_status_app_prefix + open_api_json_path,
    docs_url=device_status_app_prefix + docs_path,
    redoc_url=device_status_app_prefix + redoc_path,
)

device_status_app.include_router(
    router=DeviceStatusApiRouter,
    prefix=device_status_app_prefix
)


# Custom Exception Handlers
@device_location_verification_app.exception_handler(RequestValidationError)
@device_location_retrieval_app.exception_handler(RequestValidationError)
@device_location_geofencing_app.exception_handler(RequestValidationError)
@sim_swap_app.exception_handler(RequestValidationError)
@simple_edge_discovery_app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "status": 400,
                "code": "INVALID_ARGUMENT",
                "message": "Invalid input"
            }
        ),
    )
