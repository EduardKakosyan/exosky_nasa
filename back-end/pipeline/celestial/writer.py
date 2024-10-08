"""Writer module for writing to the database.

This module contains the writer class for writing to the database.

Functions:
    writer: Inserts data into the specified table.

:author: Eduard Kakosyan
:date: 2024-10-05
"""

import psycopg2
import numpy as np
import logging

from psycopg2 import sql, extras


def writer(data, table_name, conn):
    """Inserts data into the specified table.

    :param data: the data to insert
    :param table_name: the table to insert the data into
    :param conn: the database connection

    :return: the count of inserted rows
    """
    if not data:
        return 0

    insert_query = sql.SQL(
        "INSERT INTO {} (source_id, x, y, z, parallax, phot_g_mean_mag, bp_rp, bp_g, g_rp) "
        "VALUES %s"
    ).format(sql.Identifier(table_name))

    try:
        with conn.cursor() as cursor:
            # Using execute_values for batch inserts
            extras.execute_values(cursor, insert_query, data)
        conn.commit()
        return len(data)  # Return the count of inserted rows
    except Exception as e:
        logging.error(f"Error inserting data into {table_name}: {e}")
        conn.rollback()
        return 1  # Error
