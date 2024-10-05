import os
import certifi
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia

os.environ["SSL_CERT_FILE"] = certifi.where()


def query_gaia_and_create_png():
    # Query Gaia catalog for a specific region
    job = Gaia.launch_job_async(
        "SELECT TOP 5000000 l, b, phot_g_mean_mag "
        "FROM gaiadr3.gaia_source WHERE l BETWEEN 0 AND 360 AND b BETWEEN -90 AND 90 "
        "ORDER BY random_index"
    )
    results = job.get_results()

    # Extract l, b, and Magnitude
    l = results["l"]
    b = results["b"]
    mag = results["phot_g_mean_mag"]

    # Map l values: 0-180 stays the same, 180-360 becomes negative (shifted left)
    l_shifted = l.copy()
    l_shifted[l > 180] -= 360  # Shift l > 180° to negative values for the left side

    # Normalize the magnitude to use as sizes (smaller magnitude -> larger size)
    sizes_random = 10 ** (
        0.4 * (12 - mag)
    )  # Adjust the constant to scale sizes appropriately

    # Plot the data
    plt.figure(figsize=(40, 20))
    plt.scatter(l_shifted, b, s=sizes_random, color="white")
    plt.gca().invert_xaxis()  # Invert x-axis to match sky coordinates

    # Add axis labels
    plt.xlabel("Galactic Longitude (degrees)", fontsize=18)
    plt.ylabel("Galactic Latitude (degrees)", fontsize=18)

    # Set axis limits
    plt.xlim(180, -180)  # x-axis now ranges from -180° to 180°
    plt.ylim(-90, 90)  # b ranges from -90° to 90°

    # Set title and background color
    plt.title("Sky Image from Gaia Data (Galactic Coordinates)", fontsize=24)
    plt.gca().set_facecolor("black")  # Set background to black to represent the sky


if __name__ == "__main__":
    print(query_gaia_and_create_png())
