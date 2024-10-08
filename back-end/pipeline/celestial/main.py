"""Main script for the celestial pipeline

This pipeline is responsible for fetching data from the Gaia catalog and storing it in a Postgres database.

The pipeline consists of two threads:
1. Reader thread: Fetches data from the Gaia catalog and processes it.
2. Writer thread: Computes the cartesian coordinates and writes the processed data to the Postgres database.

The reader thread fetches data from the Gaia catalog in batches of 100,000 rows. The writer thread processes each row
and computes the cartesian coordinates. The processed data is then written to the Postgres database in batches of 10,000
rows.

The pipeline is designed to handle large volumes of data efficiently by using multiple threads and batch processing.

It has processed 50,000,000 rows in 5 hours, on a local machine with 16GB RAM and 4 cores.
This can be further optimized by using a more powerful machine or a cloud-based solution.


Functions:
    _connect_to_celestial: Establish connection to big data.
    _truncate_star_data: Truncate the star_data table to remove existing data.
    _query_gaia: Query Gaia data from the Gaia catalog.
    process_star_row: Process a single row of star data.
    reader_thread: Thread for reading data from Gaia API.
    writer_thread: Thread for writing data to the PostgreSQL database.
    main: Main function to run the pipeline.


:author: Eduard Kakosyan
:date: 2024-10-05
"""

# Standard library imports
import logging
import os
import certifi
import threading
import queue
import time

# Third-party imports
import numpy as np
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u
import psycopg2

# local imports
from writer import writer

logging.basicConfig(level=logging.INFO)

# This is to just prevent a SSL error
os.environ["SSL_CERT_FILE"] = certifi.where()

# Global queue for passing data between threads
star_queue = queue.Queue()
max_rows = 50000000
max_chunk = 100000
current_processed_rows = 0


def _connect_to_celestial():
    """Establish connection to the database.

    :return: the database connection
    """
    conn = psycopg2.connect(
        host="localhost",
        database="star_catalog",
        user="user",
        password="password",
        port="5431",
    )
    return conn


def _truncate_star_data(conn):
    """Truncates the star_data table to remove existing data.

    :param conn: the database connection

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
    """Query Gaia data from the Gaia catalog.

    This function queries the Gaia catalog for star data using the astroquery Gaia module.
    The query selects the source_id, galactic coordinates (l, b), parallax, magnitude, and color indices (bp_rp, bp_g, g_rp)
    for stars within the specified range of galactic coordinates. The query is ordered by a random index to ensure that
    the results are random and not biased by any specific ordering.

    :param offset: the offset for the query
    :param limit: the limit for the query

    :return: the results of the query
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
    """Process a single row of star data.

    This function processes a single row of star data from the Gaia catalog.
    It extracts the source_id, galactic coordinates (l, b), parallax, magnitude, and color indices (bp_rp, bp_g, g_rp)
    from the row and computes the cartesian coordinates (x, y, z) using the astropy SkyCoord class.
    If any of the values are NaN, the star is skipped and None is returned.

    :param row: a dictionary containing the star data

    :return: a list containing the processed star data or None if the star should be skipped
    """

    source_id = row["SOURCE_ID"]
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

    coord = SkyCoord(
        l=l * u.degree,
        b=b * u.degree,
        distance=(1000 / parallax) * u.arcsecond,
        frame="galactic",
    )
    x = coord.cartesian.x.value
    y = coord.cartesian.y.value
    z = coord.cartesian.z.value

    return [
        source_id,
        float(x),
        float(y),
        float(z),
        parallax,
        mag,
        bp_rp,
        bp_g,
        g_rp,
    ]


def reader_thread():
    """Thread for reading data from Gaia API.

    This function reads data from the Gaia catalog in batches of 100,000 rows.
    It processes each row using the process_star_row function and adds the processed data to the star_queue.

    The reader thread stops when no more data is available from the Gaia catalog.

    :return: None
    """
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
    """Thread for writing data to the PostgreSQL database.

    This function reads data from the star_queue and writes it to the PostgreSQL database in batches of 10,000 rows.
    It uses the writer function to write the data to the database.

    The writer thread stops when it receives the stop signal from the reader thread.

    :param conn: the database connection

    :return: None
    """
    stars_batch = []

    while True:
        star = star_queue.get()
        if star is None:  # Stop signal received
            if stars_batch:
                writer(stars_batch, "star_data", conn)  # Write remaining stars
            break

        stars_batch.append(star)

        if len(stars_batch) >= 10000:
            try:
                writer(stars_batch, "star_data", conn)
                stars_batch = []  # Reset batch after writing
            except Exception as e:
                logging.error(f"Error processing batch: {e}")


def main():
    # time start
    start = time.time()

    # Connect to the database
    conn = _connect_to_celestial()

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
