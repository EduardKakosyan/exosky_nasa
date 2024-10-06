import os
import certifi
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord, Galactic, CartesianRepresentation
import psycopg2
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from astroquery.simbad import Simbad

os.environ["SSL_CERT_FILE"] = certifi.where()


def cartesian_to_galactic(x, y, z):
    """Convert Cartesian coordinates to Galactic coordinates."""
    cartesian = CartesianRepresentation(x=x * u.pc, y=y * u.pc, z=z * u.pc)
    galactic_coord = Galactic(cartesian)
    l = galactic_coord.l.deg
    b = galactic_coord.b.deg
    distance = galactic_coord.distance.pc

    return l, b, distance


def transform_mag(mag, distance_pc, new_distance_pc):
    """Transform the phot_g_mean_mag to reflect new distance."""
    return mag + 5 * (np.log10(new_distance_pc) - np.log10(distance_pc))


def color_stars(bp_rp, bp_g, g_rp):
    """Map bp_rp to colors and adjust brightness using bp_g and g_rp."""
    cmap = plt.get_cmap("cividis")  # Choose a color map
    norm = Normalize(vmin=min(bp_rp), vmax=max(bp_rp))  # Normalize bp_rp values
    star_colors = cmap(norm(bp_rp))

    brightness_scale = 1.5 / (1 + np.exp(-bp_g + g_rp))  # Adjust the scaling factor
    star_colors[:, :3] *= brightness_scale[:, np.newaxis] * 0.8  # Adjust brightness

    return star_colors


def fetch_galactic_coordinates(planet_name):
    """Fetch galactic coordinates of a planet from SIMBAD."""
    simbad = Simbad()
    result = simbad.query_object(planet_name)

    if result is None:
        raise ValueError(f"No results found for {planet_name}")

    # Extract coordinates
    ra = result['RA'].data[0]
    dec = result['DEC'].data[0]

    # Convert to Galactic coordinates
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg), frame='icrs')
    galactic_coord = coord.galactic
    return galactic_coord.l.deg, galactic_coord.b.deg


def query_postgresql_and_create_png(planet_name, distance_pc):
    """Query PostgreSQL for star data and create a PNG."""
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
    distance_pc_gaia = 1000 / parallax

    # Fetch the galactic coordinates for the specified planet
    galactic_long, galactic_lat = fetch_galactic_coordinates(planet_name)

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

    # Adjust phot_g_mean_mag based on distance to the specified planet
    new_mag = transform_mag(mag, distance_pc_gaia, distance_pc)

    sizes = 5 * 10 ** (0.4 * (12 - new_mag))  # Using adjusted magnitude for sizes

    l_new_shifted = np.where(l_new > 180, l_new - 360, l_new)

    # Get star colors based on bp_rp, bp_g, g_rp
    star_colors = color_stars(bp_rp, bp_g, g_rp)

    fig, ax = plt.subplots(figsize=(160, 40))

    # Use the 'c' argument for color mapping
    scatter = ax.scatter(l_new_shifted, b_new, s=sizes, c=bp_rp, cmap="cividis",
                         alpha=0.7)

    # Fix the aspect ratio and limits
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("black")

    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(f"{planet_name}.png", facecolor="black", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    # Example usage: Fetch coordinates for Kepler-186f and create a PNG
    try:
        query_postgresql_and_create_png("Kepler-186f", distance_pc=500)
    except ValueError as e:
        print(e)
