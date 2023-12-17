# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 14:49:56
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-15 17:41:03


from common.database import models
from common.database import database
import time
import logging
import os

# If under test, do not execute
if "PYTEST_CURRENT_TEST" not in os.environ:
    # Initialize the database tables
    MODELS_INITIALIZED = False

    for i in range(10):
        try:
            models.Base.metadata.create_all(bind=database.engine)
            MODELS_INITIALIZED = True
            logging.info("All Database models have been initialized!")
            break
        except Exception as e:
            logging.error(f"Uncable of Initializing DB Tables{e}")
            time.sleep(10)

        if not MODELS_INITIALIZED:
            exit(2)
