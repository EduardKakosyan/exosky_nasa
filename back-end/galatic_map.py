import os
import certifi
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
import psycopg2
from matplotlib.colors import Normalize
import matplotlib.cm as cm

os.environ["SSL_CERT_FILE"] = certifi.where()


def cartesian_to_galactic(x, y, z):
    """Convert Cartesian coordinates to Galactic coordinates."""
    coord = SkyCoord(
        x=x * u.pc, y=y * u.pc, z=z * u.pc, representation_type="cartesian"
    )
    l = coord.galactic.l.deg
    b = coord.galactic.b.deg  # Galactic latitude in degrees
    distance = coord.galactic.distance.pc  # Distance in parsecs
    return l, b, distance


def transform_mag(mag, distance_pc, new_distance_pc):
    """Transform the phot_g_mean_mag to reflect new distance."""
    return mag + 5 * (np.log10(new_distance_pc) - np.log10(distance_pc))


def color_stars(bp_rp, bp_g, g_rp):
    """Map bp_rp to colors and adjust brightness using bp_g and g_rp."""
    # Use a different colormap (e.g., 'cividis' or 'viridis')
    cmap = plt.get_cmap("cividis")  # Choose a color map
    norm = Normalize(vmin=min(bp_rp), vmax=max(bp_rp))  # Normalize bp_rp values
    star_colors = cmap(norm(bp_rp))

    # Modify brightness scaling for a better visual effect
    brightness_scale = 1.5 / (1 + np.exp(-bp_g + g_rp))  # Adjust the scaling factor

    # Apply brightness scaling to the colors (affect only RGB channels)
    star_colors[:, :3] *= brightness_scale[:, np.newaxis] * 0.8  # Adjust the factor to control brightness

    return star_colors


def query_postgresql_and_create_png(
    planet_name, galactic_long, galactic_lat, distance_pc
):
    # Connect to PostgreSQL database
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
        "SELECT x, y, z, parallax, phot_g_mean_mag, bp_rp, bp_g, g_rp FROM star_data;"
    )
    rows = cur.fetchall()

    # Close the database connection
    cur.close()
    conn.close()

    x_gaia = np.array([row[0] for row in rows])  # x in parsecs
    y_gaia = np.array([row[1] for row in rows])  # y in parsecs
    z_gaia = np.array([row[2] for row in rows])  # z in parsecs
    parallax = np.array([row[3] for row in rows])  # parallax in milliarcseconds
    mag = np.array([row[4] for row in rows])  # phot_g_mean_mag
    bp_rp = np.array([row[5] for row in rows])  # bp_rp color index
    bp_g = np.array([row[6] for row in rows])  # bp_g color data
    g_rp = np.array([row[7] for row in rows])  # g_rp color data

    # Convert parallax (in milliarcseconds) to distance in parsecs
    distance_pc_gaia = 1 / parallax

    # Convert planet's galactic coordinates to Cartesian
    planet_coord = SkyCoord(
        l=galactic_long * u.deg,
        b=galactic_lat * u.deg,
        distance=distance_pc * u.pc,
        frame="galactic",
    )
    planet_x, planet_y, planet_z = (
        planet_coord.cartesian.x.value,
        planet_coord.cartesian.y.value,
        planet_coord.cartesian.z.value,
    )

    # Shift star positions to make the exoplanet the new origin
    shifted_x = x_gaia - planet_x
    shifted_y = y_gaia - planet_y
    shifted_z = z_gaia - planet_z

    # Convert the shifted Cartesian coordinates to galactic coordinates
    l_new, b_new, d_new = cartesian_to_galactic(shifted_x, shifted_y, shifted_z)

    # Transform magnitudes based on new distances
    new_mag = transform_mag(mag, distance_pc_gaia, d_new)

    sizes = 10 ** (0.4 * (12 - new_mag))  # Adjust constant for size scaling

    # Get star colors based on bp_rp, bp_g, g_rp
    star_colors = color_stars(bp_rp, bp_g, g_rp)

    fig, ax = plt.subplots(figsize=(160, 40))

    # Use the 'c' argument for color mapping
    scatter = ax.scatter(l_new, b_new, s=sizes, c=bp_rp, cmap="cividis",
                         alpha=0.7)  # Updated to use 'c' instead of 'color'

    # Fix the aspect ratio and limits
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(0, 360)
    ax.set_ylim(-90, 90)
    ax.set_facecolor("black")  # Ensure background is black

    # Optional: add a color bar for reference
    plt.colorbar(scatter, label='BP-RP Color Index')  # Add color bar to provide reference

    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(f"{planet_name}.png", facecolor="black", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    # Example: Plot the sky from the perspective of a planet with galactic coordinates (225, 0) and 10 pc away
    query_postgresql_and_create_png("Planet A", 225, 0, 10)
