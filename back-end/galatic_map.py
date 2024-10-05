import os
import certifi
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia

os.environ["SSL_CERT_FILE"] = certifi.where()

def galactic_to_cartesian(l, b, distance_pc):
    """Convert galactic coordinates to 3D Cartesian coordinates."""
    l_rad = np.radians(l)
    b_rad = np.radians(b)
    
    # Convert to Cartesian coordinates
    x = distance_pc * np.cos(b_rad) * np.cos(l_rad)
    y = distance_pc * np.cos(b_rad) * np.sin(l_rad)
    z = distance_pc * np.sin(b_rad)
    
    return np.array([x, y, z]).T

def cartesian_to_galactic(x, y, z):
    """Convert 3D Cartesian coordinates to galactic coordinates."""
    r = np.sqrt(x**2 + y**2 + z**2)
    l = np.degrees(np.arctan2(y, x))
    b = np.degrees(np.arcsin(z / r))
    
    # Ensure l is in [0, 360]
    l = (l + 360) % 360
    return l, b

def transform_mag(mag, distance_pc, new_distance_pc):
    """Transform the phot_g_mean_mag to new values based on distance."""
    return mag + 5 * (np.log10(new_distance_pc) - np.log10(distance_pc))

def query_gaia_and_create_png(planet_name, galactic_long, galactic_lat, distance_pc):
    # Query Gaia catalog for a specific region
    job = Gaia.launch_job_async(
        "SELECT TOP 5000000 l, b, phot_g_mean_mag, parallax "
        "FROM gaiadr3.gaia_source WHERE l BETWEEN 0 AND 360 AND b BETWEEN -90 AND 90 "
        "ORDER BY random_index"
    )
    results = job.get_results()

    # Extract l, b, and Magnitude
    l = results["l"]
    b = results["b"]
    mag = results["phot_g_mean_mag"]
    parallax = results["parallax"]  # In case we want to use it later

    # Convert to Cartesian coordinates (using Earth as origin)
    distance_pc_gaia = 1 / (parallax / 1000)  # Convert parallax to distance in parsecs
    xyz_gaia = galactic_to_cartesian(l, b, distance_pc_gaia)

    # Calculate new origin based on the exoplanet
    planet_xyz = galactic_to_cartesian(galactic_long, galactic_lat, distance_pc)
    
    # Change coordinates to the inputted exoplanet as the new origin
    shifted_xyz = xyz_gaia - planet_xyz

    # Convert back to galactic coordinates
    l_new, b_new = cartesian_to_galactic(shifted_xyz[:, 0], shifted_xyz[:, 1], shifted_xyz[:, 2])

    # Transform the magnitude values
    new_mag = transform_mag(mag, distance_pc_gaia, distance_pc)

    # Normalize the new magnitude to use as sizes (smaller magnitude -> larger size)
    sizes_random = 10 ** (0.4 * (12 - new_mag))  # Adjust constant to scale sizes appropriately

    # Plot the data
    plt.figure(figsize=(160, 40))
    plt.scatter(l_new, b_new, s=sizes_random, color="white")
    plt.gca().invert_xaxis()  # Invert x-axis to match sky coordinates

    # Add axis labels
    plt.xlabel("Galactic Longitude (degrees)", fontsize=18)
    plt.ylabel("Galactic Latitude (degrees)", fontsize=18)

    # Set axis limits
    plt.xlim(180, -180)  # x-axis now ranges from -180° to 180°
    plt.ylim(-90, 90)  # b ranges from -90° to 90°

    # Set title and background color
    plt.title(f"Sky Image from Gaia Data (Galactic Coordinates) - {planet_name}", fontsize=24)
    plt.gca().set_facecolor("black")  # Set background to black to represent the sky
    
    # Save the plot to a file
    plt.savefig(f'{planet_name}.jpg', facecolor="black")
    plt.close()  # Close the plot to free up memory

if __name__ == "__main__":
    print(query_gaia_and_create_png())
