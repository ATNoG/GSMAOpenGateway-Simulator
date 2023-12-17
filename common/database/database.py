# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-08 17:47:10
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 16:25:17
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import logging

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
print("ROOT_DIR:", ROOT_DIR)
DB_OK = False
DB_LOCATION = os.path.join(ROOT_DIR, "database.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_LOCATION}"
for i in range(10):
    try:
        logging.info("Trying to connect to the DB.")
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        Base = declarative_base()
        DB_OK = True
        break
    except Exception as e:
        logging.warning(f"Couldn't connect to DB. Reason: {e}.")
        logging.info("Waiting for DB. Will sleep 10 more seconds...")
        time.sleep(10)
else:
    if not DB_OK:
        logging.error("Unable to connect to database.")
        exit(1)
