"""Main Function to run the celestial pipeline

@author: Eduard Kakosyan
"""

# imports

# defaults
import os
import sys
import threading
import queue
import time
import certifi
import logging

# 3rd party ports
import psycopg2
import numpy as np
from astroquery.gaia import Gaia

# local imports


# this is to make the ssl work
os.environ["SSL_CERT_FILE"] = certifi.where()

# GLOBALS
star_queue = queue.Queue()
max_rows = 5000000
max_chunk = 100000
current_processed_rows = 0


def _connect_to_celestial():
    """Establish connection to the celestial database."""
    conn = psycopg2.connect(
        host="localhost",
        database="star_catalog",
        user="user",
        password="password",
        port="5431",
    )
    return conn


def _truncate_star_data(conn):
    """Clears the database on running the celestial pipeline

    :param conn: The connection to the database
    :return: None
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute("TRUNCATE TABLE star_data;")
            conn.commit()
        except Exception as e:
            logging.error(f"Error truncating star_data table: {e}")
            conn.rollback()


def _query_gaia(offset=0, limit=100000):
    """Query the Gaia database for star data

    :param offset: The offset of the query
    :param limit: The limit of the query
    :return: The results of the query
    """
    try:
        job = Gaia.launch_job_async(
            f"SELECT TOP {limit} source_id, l, b, parallax, phot_g_mean_mag, bp_rp, bp_g, g_rp "
            f"FROM gaiadr3.gaia_source WHERE l BETWEEN 0 AND 360 AND b BETWEEN -90 AND 90 "
            f"ORDER BY random_index OFFSET {offset}"
        )
        results = job.get_results()
        return results
    except Exception as e:
        logging.error(f"An error occurred while querying Gaia: {e}")
        return None


def process_star_row(row):
    source_id = int(row["SOURCE_ID"])
    l = float(row["l"])
    b = float(row["b"])
    parallax = row["parallax"] if row["parallax"] is not None else None
    mag = float(row["phot_g_mean_mag"])
    bp_rp = float(row["bp_rp"])
    bp_g = float(row["bp_g"])
    g_rp = float(row["g_rp"])

    # Check for NaN values and skip if any are present
    if any(np.isnan(value) for value in [l, b, parallax, mag, bp_rp, bp_g, g_rp]):
        return None  # Return None to skip this star

    # Convert coordinates to Cartesian
    x, y, z = galactic_to_cartesian(l, b, parallax)

    return [source_id, float(x), float(y), float(z), parallax, mag, bp_rp, bp_g, g_rp]


def reader_thread():
    """Thread for reading data from Gaia API."""
    offset = 0
    limit = 100000

    while offset < max_rows:
        results = _query_gaia(offset, limit)
        if results is None or len(results) == 0:
            break  # Stop if no more data is available
        results_df = results.to_pandas()

        for row in results_df.itertuples(index=False):
            cartesian_star = process_star_row(row._asdict())
            if cartesian_star is not None:
                star_queue.put(cartesian_star)  # Add to the queue

        offset += limit  # Increment offset for the next batch

    # Signal the writer thread to stop
    star_queue.put(None)  # Stop signal


def writer_thread(conn):
    """Thread for writing data to the PostgreSQL database."""
    stars_batch = []

    while True:
        star = star_queue.get()
        if star is None:  # Stop signal received
            if stars_batch:
                writer(stars_batch, "star_data", conn)  # Write remaining stars
            break

        stars_batch.append(star)

        if len(stars_batch) >= 1000:
            try:
                writer(stars_batch, "star_data", conn)
                stars_batch = []  # Reset batch after writing
            except Exception as e:
                logging.error(f"Error processing batch: {e}")


def main():
    # time start
    start = time.time()

    # Connect to the database
    conn = _connect_to_big_data()

    # Truncate existing data
    _truncate_star_data(conn)

    # Start reader and writer threads
    reader = threading.Thread(target=reader_thread)
    writer = threading.Thread(target=writer_thread, args=(conn,))

    reader.start()
    writer.start()

    # Wait for both threads to complete
    reader.join()
    writer.join()

    # Close the connection
    conn.close()

    # time end
    end = time.time()

    print(f"Time taken: {end - start} seconds")


if __name__ == "__main__":
    main()
