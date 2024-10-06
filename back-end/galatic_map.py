import os
import certifi
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
from astropy import units as u
from astropy.coordinates import Galactic, CartesianRepresentation, Distance

os.environ["SSL_CERT_FILE"] = certifi.where()


def galactic_to_cartesian(l, b, distance_pc):
    # Use Distance object to allow for proper distance handling
    distance = Distance(distance_pc * u.pc, allow_negative=True)
    galactic_coord = Galactic(l=l * u.deg, b=b * u.deg, distance=distance)

    # Convert to Cartesian representation
    cartesian_coord = galactic_coord.cartesian
    return cartesian_coord.x.value, cartesian_coord.y.value, cartesian_coord.z.value


def cartesian_to_galactic(x, y, z):
    cartesian_coord = CartesianRepresentation(x=x * u.pc, y=y * u.pc, z=z * u.pc)
    galactic_coord = Galactic(cartesian_coord)
    return galactic_coord.l.deg, galactic_coord.b.deg, galactic_coord.distance.pc


def transform_mag(mag, distance_pc, new_distance_pc):
    """Transform the phot_g_mean_mag to new values based on distance."""
    return mag + 5 * (np.log10(new_distance_pc) - np.log10(distance_pc))


def query_postgres():
    """Query PostgreSQL database and return star data."""
    conn = psycopg2.connect(
        dbname="star_catalog",
        user="user",
        password="password",
        host="localhost",
        port=5431,
    )
    cur = conn.cursor()
    cur.execute("SELECT parallax, phot_g_mean_mag, x, y, z FROM star_data;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert rows to numpy arrays
    parallax = np.array([row[0] for row in rows])  # parallax in milliarcseconds
    mag = np.array([row[1] for row in rows])  # phot_g_mean_mag
    x_gaia = np.array([row[2] for row in rows])  # x in parsecs
    y_gaia = np.array([row[3] for row in rows])  # y in parsecs
    z_gaia = np.array([row[4] for row in rows])  # z in parsecs

    # Convert parallax to distance in parsecs
    distance_pc_gaia = np.where(
        parallax > 0, 1000 / parallax, 0
    )  # Avoid division by zero

    return x_gaia, y_gaia, z_gaia, distance_pc_gaia, mag


def create_png_for_exoplanet(planet_name, galactic_long, galactic_lat, distance_pc):
    # Query PostgreSQL to get star data
    x_gaia, y_gaia, z_gaia, distance_pc_gaia, mag = query_postgres()

    # Convert the exoplanet's galactic coordinates to Cartesian
    planet_x, planet_y, planet_z = galactic_to_cartesian(
        galactic_long, galactic_lat, distance_pc
    )

    # Shift the star positions to make the exoplanet the new origin
    shifted_x = x_gaia - planet_x
    shifted_y = y_gaia - planet_y
    shifted_z = z_gaia - planet_z

    # Convert back to galactic coordinates
    l_new, b_new, _ = cartesian_to_galactic(shifted_x, shifted_y, shifted_z)

    # Normalize the new magnitude to use as sizes (smaller magnitude -> larger size)
    sizes_random = 11 ** (
        0.4 * (12 - mag)
    )  # You might want to adjust the scaling constant

    # Plot the data
    plt.figure(figsize=(160, 40))  # Adjust figure size as needed
    l_new_shifted = np.where(
        l_new > 180, l_new - 360, l_new
    )  # Shift l_new to the range [-180, 180]

    plt.scatter(
        l_new_shifted, b_new, s=sizes_random, color="white", alpha=0.5
    )  # Added alpha for visibility
    plt.title(f"Stars around {planet_name}")
    plt.xlabel("Galactic Longitude (degrees)")
    plt.ylabel("Galactic Latitude (degrees)")
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.gca().set_facecolor("black")  # Set background to black to represent the sky

    # Save the plot to a file
    plt.savefig(f"{planet_name}.png", facecolor="black")
    plt.close()  # Close the plot to free up memory


if __name__ == "__main__":
    # Example for creating PNG for Kepler-186f
    create_png_for_exoplanet("Kepler-186f", 36, 12, 152)
