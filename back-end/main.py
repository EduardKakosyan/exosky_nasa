import logging
import psycopg2
import numpy as np
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import os
import certifi
import threading
import queue
import time
import matplotlib.pyplot as plt  # Don't forget to import matplotlib

logging.basicConfig(level=logging.INFO)
os.environ["SSL_CERT_FILE"] = certifi.where()

# Global queue for passing data between threads
star_queue = queue.Queue()


def _connect_to_celestial():
    """Establish connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host="localhost",
        database="star_catalog",
        user="user",
        password="password",
        port="5431",
    )
    return conn


def get_kepler_coordinates():
    """Get the galactic coordinates of Kepler-186f from SIMBAD."""
    simbad = Simbad()
    result = simbad.query_object("Kepler-186f")

    if result is None or 'RA' not in result.columns or 'DEC' not in result.columns:
        raise ValueError("Failed to retrieve Kepler coordinates from SIMBAD.")

    ra = result['RA'].data[0]
    dec = result['DEC'].data[0]

    # Parse RA and DEC into degrees
    coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
    l, b = coord.galactic.l.deg, coord.galactic.b.deg  # Convert to galactic coordinates
    return l, b


def query_star_data(kepler_x, kepler_y, kepler_z, limit=1000000):  # Set limit to 1 million
    """Query star_data table for stars around Kepler-186f."""
    with _connect_to_celestial() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT source_id, x, y, z 
                FROM star_data 
                ORDER BY 
                    sqrt(power(x - {kepler_x}, 2) + power(y - {kepler_y}, 2) + power(z - {kepler_z}, 2))
                LIMIT {limit};  -- Limit the results to 1 million
                """
            )
            return cursor.fetchall()


def convert_to_cartesian(l, b, parallax=None):
    """Convert galactic coordinates to Cartesian."""
    coord = SkyCoord(l=l * u.degree, b=b * u.degree, distance=(1 / parallax) * u.arcsecond if parallax else None,
                     frame='galactic')
    return coord.cartesian.x.value, coord.cartesian.y.value, coord.cartesian.z.value


def process_and_store_data(stars):
    """Store the stars data relative to Kepler-186f in a new table."""
    with _connect_to_celestial() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS stars_relative_to_kepler (source_id BIGINT, x FLOAT, y FLOAT, z FLOAT);")

            for source_id, x, y, z in stars:
                # Convert NumPy types to native Python float types
                cursor.execute(
                    "INSERT INTO stars_relative_to_kepler (source_id, x, y, z) VALUES (%s, %s, %s, %s)",
                    (source_id, float(x), float(y), float(z))  # Ensure float conversion
                )
            conn.commit()


def plot_milky_way(stars):
    """Plot the Milky Way using the given stars data."""
    # Extracting x, y, z coordinates for plotting
    x_stars = np.array([star[1] for star in stars])
    y_stars = np.array([star[2] for star in stars])
    z_stars = np.array([star[3] for star in stars])

    sizes = np.clip(1000 * np.log10(10 / np.abs(z_stars)), 1, 1000)  # Size based on distance

    plt.figure(figsize=(40, 20))
    plt.scatter(x_stars, y_stars, s=sizes, color='white')
    plt.gca().set_facecolor('black')
    plt.title("Sky Image from Kepler-186f Perspective", fontsize=24)
    plt.savefig("kepler186f_sky_image.png", facecolor='black')


def main():
    # Start the process
    start = time.time()

    # Get Kepler's coordinates
    kepler_l, kepler_b = get_kepler_coordinates()
    print(f"Kepler-186f coordinates: l={kepler_l}, b={kepler_b}")
    kepler_x, kepler_y, kepler_z = convert_to_cartesian(kepler_l, kepler_b)
    print(f"Kepler-186f Cartesian coordinates: x={kepler_x}, y={kepler_y}, z={kepler_z}")

    # Query the star_data table, limiting to 1 million rows
    stars = query_star_data(kepler_x, kepler_y, kepler_z, limit=1000000)
    print("Got the stars")

    # Center stars around Kepler-186f
    stars_relative = [(source_id, x - kepler_x, y - kepler_y, z - kepler_z) for (source_id, x, y, z) in stars]

    # Store relative stars in a new table
    process_and_store_data(stars_relative)
    print("Stored the stars")

    # Plot the Milky Way from Kepler-186f's perspective
    plot_milky_way(stars_relative)
    print("Plotted the stars")

    # Time taken for the process
    end = time.time()
    print(f"Time taken: {end - start} seconds")


if __name__ == "__main__":
    main()
