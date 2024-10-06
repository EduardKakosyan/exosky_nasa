import os
import certifi
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
from astropy import units as u
from astropy.coordinates import Galactic, CartesianRepresentation, Distance
from matplotlib.colors import Normalize


os.environ["SSL_CERT_FILE"] = certifi.where()


def galactic_to_cartesian(l, b, distance_pc):
    distance = Distance(distance_pc * u.pc, allow_negative=True)
    galactic_coord = Galactic(l=l * u.deg, b=b * u.deg, distance=distance)
    cartesian_coord = galactic_coord.cartesian
    return cartesian_coord.x.value, cartesian_coord.y.value, cartesian_coord.z.value


def cartesian_to_galactic(x, y, z):
    cartesian_coord = CartesianRepresentation(x=x * u.pc, y=y * u.pc, z=z * u.pc)
    galactic_coord = Galactic(cartesian_coord)
    return galactic_coord.l.deg, galactic_coord.b.deg, galactic_coord.distance.pc


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
    cur.execute(
        "SELECT parallax, phot_g_mean_mag, x, y, z, bp_rp, bp_g, g_rp FROM star_data;"
    )
    rows = cur.fetchall()
    print(f"Retrieved {len(rows)} rows from the database.")  # Debugging line
    cur.close()
    conn.close()

    # Convert rows to numpy arrays
    if len(rows) == 0:
        print("No data retrieved from the database.")
        return None

    parallax = np.array([row[0] for row in rows])
    mag = np.array([row[1] for row in rows])
    x_gaia = np.array([row[2] for row in rows])
    y_gaia = np.array([row[3] for row in rows])
    z_gaia = np.array([row[4] for row in rows])
    bp_rp = np.array([row[5] for row in rows])
    bp_g = np.array([row[6] for row in rows])
    g_rp = np.array([row[7] for row in rows])

    distance_pc_gaia = np.where(parallax > 0, 1000 / parallax, 0)
    return x_gaia, y_gaia, z_gaia, distance_pc_gaia, mag, bp_rp, bp_g, g_rp


def transform_mag(mag, distance_pc_earth, distance_pc_planet):
    """Transform the phot_g_mean_mag to reflect new distance using distance modulus formula."""
    epsilon = 1e-10
    distance_pc_earth = np.clip(distance_pc_earth, epsilon, None)
    distance_pc_planet = np.clip(distance_pc_planet, epsilon, None)

    abs_mag = mag - 5 * (np.log10(distance_pc_earth) - 1)

    new_mag = abs_mag + 5 * (np.log10(distance_pc_planet) - 1)

    return new_mag


def create_star_colors(bp_rp, bp_g, g_rp, new_mag):
    """Map star colors based on bp_rp and adjust brightness."""
    # Normalize bp_rp values for color mapping
    norm = Normalize(vmin=np.min(bp_rp), vmax=np.max(bp_rp))

    cmap = plt.get_cmap("cividis")
    star_colors = cmap(norm(bp_rp))

    brightness_scale = 1.5 / (1 + np.exp(-bp_g + g_rp))
    star_colors[:, :3] *= brightness_scale[:, np.newaxis] * 0.8
    star_colors[:, :3] = np.clip(star_colors[:, :3], 0, 1)

    # Identify the indices of the 20 largest stars based on magnitude
    largest_star_indices = np.argsort(new_mag)[:30]

    # Set the colors of the largest stars to white
    star_colors[largest_star_indices] = [1, 1, 1, 1]

    return star_colors


def create_png_for_exoplanet(planet_name, galactic_long, galactic_lat, distance_pc):
    # Query PostgreSQL to get star data
    result = query_postgres()
    if result is None:
        return  # Exit if there's no data
    x_gaia, y_gaia, z_gaia, distance_pc_gaia, mag, bp_rp, bp_g, g_rp = result

    # Convert the exoplanet's galactic coordinates to Cartesian
    planet_x, planet_y, planet_z = galactic_to_cartesian(galactic_long, galactic_lat, distance_pc)

    # Shift the star positions
    shifted_x = x_gaia - planet_x
    shifted_y = y_gaia - planet_y
    shifted_z = z_gaia - planet_z

    # Convert back to galactic coordinates
    l_new, b_new, _ = cartesian_to_galactic(shifted_x, shifted_y, shifted_z)

    new_mag = transform_mag(mag, distance_pc_gaia, distance_pc)

    # Adjust the scaling factor and threshold for star sizes
    normalized_distances = (distance_pc_gaia - np.min(distance_pc_gaia)) / (
                np.max(distance_pc_gaia) - np.min(distance_pc_gaia))

    sizes = (2 ** ((-0.4) * (new_mag - np.median(new_mag)))) * (1 - normalized_distances)
    sizes = sizes * 0.1  # Reduced scaling factor
    threshold = 1  # Lowered threshold
    sizes[sizes < threshold] = 0

    # Generate star colors
    star_colors = create_star_colors(bp_rp, bp_g, g_rp, new_mag)

    # Identify the indices of the 30 brightest stars
    brightest_star_indices = np.argsort(new_mag)[:30]

    # Plotting
    plt.figure(figsize=(80, 20))  # Adjusted figure size to better resemble the Milky Way proportions
    l_new_shifted = np.where(l_new > 180, l_new - 360, l_new)

    # Plot all stars except the brightest 30
    scatter = plt.scatter(l_new_shifted, b_new, s=sizes, color=star_colors, alpha=0.8)

    # Plot the brightest 30 stars on top with alpha=1
    scatter = plt.scatter(l_new_shifted[brightest_star_indices], b_new[brightest_star_indices],
                          s=sizes[brightest_star_indices], color=star_colors[brightest_star_indices], alpha=1.0)

    plt.title(f"Stars around {planet_name}")
    plt.xlabel("Galactic Longitude (degrees)")
    plt.ylabel("Galactic Latitude (degrees)")
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.gca().set_facecolor("black")  # Black background for space-like effect

    # Save the plot to a file
    plt.savefig(f"{planet_name}.png", facecolor="black")
    plt.close()


if __name__ == "__main__":
    try:
        create_png_for_exoplanet("Kepler-186f", 36, 12, 152)
    except Exception as e:
        print(f"An error occurred: {e}")
