import os
import certifi
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
from astropy import units as u
from astropy.coordinates import Galactic, CartesianRepresentation
from matplotlib.colors import Normalize

os.environ["SSL_CERT_FILE"] = certifi.where()

def galactic_to_cartesian(l, b, distance_pc):
    galactic_coord = Galactic(l=l * u.deg, b=b * u.deg, distance=distance_pc * u.pc)

    # Convert to Cartesian representation
    cartesian_coord = galactic_coord.cartesian

    # Extract x, y, z in parsecs
    x = cartesian_coord.x.value
    y = cartesian_coord.y.value
    z = cartesian_coord.z.value

    return x, y, z


def cartesian_to_galactic(x, y, z):
    cartesian_coord = CartesianRepresentation(x=x * u.pc, y=y * u.pc, z=z * u.pc)

    # Convert to Galactic coordinates
    galactic_coord = Galactic(cartesian_coord)

    # Extract Galactic longitude, latitude, and distance
    l = galactic_coord.l.deg
    b = galactic_coord.b.deg
    distance = galactic_coord.distance.pc

    return l, b, distance


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

    # Query for the relevant data
    cur.execute(
        "SELECT x, y, z, parallax, phot_g_mean_mag, bp_rp, bp_g, g_rp FROM star_data LIMIT 5000000;"
    )
    rows = cur.fetchall()

    # Close the database connection
    cur.close()
    conn.close()

    # Convert rows to numpy arrays
    x_gaia = np.array([row[0] for row in rows])  # x in parsecs
    y_gaia = np.array([row[1] for row in rows])  # y in parsecs
    z_gaia = np.array([row[2] for row in rows])  # z in parsecs
    parallax = np.array([row[3] for row in rows])  # parallax in milliarcseconds
    mag = np.array([row[4] for row in rows])  # phot_g_mean_mag
    bp_rp = np.array([row[5] for row in rows])
    bp_g = np.array([row[6] for row in rows])
    g_rp = np.array([row[7] for row in rows])

    # Convert parallax to distance in parsecs
    distance_pc_gaia = 1000 / parallax

    return x_gaia, y_gaia, z_gaia, distance_pc_gaia, mag, bp_rp, bp_g, g_rp

def create_star_colors(bp_rp, bp_g, g_rp, new_mag):
    """Map star colors based on bp_rp and adjust brightness."""
    # Normalize bp_rp values for color mapping
    norm = Normalize(vmin=np.min(bp_rp), vmax=np.max(bp_rp))

    cmap = plt.get_cmap("cividis")
    star_colors = cmap(norm(bp_rp))

    brightness_scale = 1.5 / (1 + np.exp(-bp_g + g_rp))
    star_colors[:, :3] *= brightness_scale[:, np.newaxis]
    star_colors[:, :3] = np.clip(star_colors[:, :3], 0, 1)

    # Identify the indices of the 20 largest stars based on magnitude
    largest_star_indices = np.argsort(new_mag)[:20]

    star_colors[largest_star_indices] = [1, 1, 1, 1]

    return star_colors


def create_png_for_exoplanet(planet_name, galactic_long, galactic_lat, distance_pc):
    # Query PostgreSQL to get star data
    result = query_postgres()
    if result is None:
        return
    x_gaia, y_gaia, z_gaia, distance_pc_gaia, mag, bp_rp, bp_g, g_rp = result

    # Convert to Cartesian coordinates (using Earth as origin)
    # Calculate distance based on the returned parallax dat

    # Convert the exoplanet's galactic coordinates to Cartesian
    planet_x, planet_y, planet_z = galactic_to_cartesian(galactic_long, galactic_lat, distance_pc)

    # Shift the star positions to make the exoplanet the new origin
    shifted_x = x_gaia - planet_x
    shifted_y = y_gaia - planet_y
    shifted_z = z_gaia - planet_z

    # Convert back to galactic coordinates
    l_new, b_new, _ = cartesian_to_galactic(shifted_x, shifted_y, shifted_z)

    # Normalize the new magnitude to use as sizes (smaller magnitude -> larger size)
    sizes_random = 10 ** (0.4 * (12 - mag))  # Adjust constant to scale sizes appropriately

    # Plot the data
    plt.figure(figsize=(160, 40))

    l_new_shifted = np.where(l_new > 180, l_new - 360, l_new)

    star_colors = create_star_colors(bp_rp, bp_g, g_rp, mag)

    plt.scatter(l_new_shifted, b_new, s=sizes_random, c=star_colors)

    # Add axis labels
    plt.xlabel("Galactic Longitude (degrees)", fontsize=18)
    plt.ylabel("Galactic Latitude (degrees)", fontsize=18)

    # Set title and background color
    plt.title(f"Sky Image from Gaia Data (Galactic Coordinates) - {planet_name}", fontsize=24)
    plt.gca().set_facecolor("black")  # Set background to black to represent the sky

    # Save the plot to a file
    plt.savefig(f'{planet_name}.png', facecolor="black")
    plt.close()  # Close the plot to free up memory


if __name__ == "__main__":
    # Example for creating PNG for Kepler-186f
    create_png_for_exoplanet("Kepler-186f", 36, 12, 1000)
    create_png_for_exoplanet("Earth", 0, 0, 0)
