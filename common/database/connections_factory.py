# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 11:34:16
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-11 20:58:08
from common.database.database import SessionLocal


def new_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
