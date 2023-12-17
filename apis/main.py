# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 10:54:41
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-14 19:51:12
# coding: utf-8

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from routers.location_retrieval_api import router \
    as LocationRetrievalApiRouter
from routers.location_verification_api import router\
    as LocationVerificationApiRouter
from routers.simulation_api import router\
    as SimulationApiRouter
import config # noqa

open_api_json_path = "/openapi.json"
docs_path = "/docs"
redoc_path = "/redoc"

device_location_retrieval_app_prefix_doc = "/location-retrieval/v0"
device_location_retrieval_app_prefix_router = "/location-retrieval/v0"

device_location_verification_app_prefix = "/location-verification/v0"
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
    openapi_url=device_location_retrieval_app_prefix_doc + open_api_json_path,
    docs_url=device_location_retrieval_app_prefix_doc + docs_path,
    redoc_url=device_location_retrieval_app_prefix_doc + redoc_path,
    
)

device_location_retrieval_app.include_router(
    router=LocationRetrievalApiRouter,
    prefix=device_location_retrieval_app_prefix_router
)


@device_location_retrieval_app.exception_handler(RequestValidationError)
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
