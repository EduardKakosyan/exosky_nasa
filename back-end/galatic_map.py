import os
import certifi
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia
from astropy import units as u
import numpy as np
from astropy.coordinates import SkyCoord

os.environ["SSL_CERT_FILE"] = certifi.where()

def galactic_to_cartesian(l, b, distance_pc):
    coord = SkyCoord(l=l * u.degree, b=b * u.degree, distance=distance_pc, frame='galactic')
    return coord.cartesian.x.value, coord.cartesian.y.value, coord.cartesian.z.value

def cartesian_to_galactic(x, y, z):
    coord = SkyCoord(x=x * u.pc, y=y * u.pc, z=z * u.pc, representation_type='cartesian')
    
    # Convert to galactic coordinates
    l = coord.galactic.l.deg
    b = coord.galactic.b.deg
    distance = coord.galactic.distance.pc
    
    return l, b, distance

def transform_mag(mag, distance_pc, new_distance_pc):
    """Transform the phot_g_mean_mag to new values based on distance."""
    return mag + 5 * (np.log10(new_distance_pc) - np.log10(distance_pc))

def query_gaia_and_create_png(planet_name, galactic_long, galactic_lat, distance_pc):
    # Query Gaia catalog for a specific region
    job = Gaia.launch_job_async(
        "SELECT TOP 500000 l, b, phot_g_mean_mag, parallax "
        "FROM gaiadr3.gaia_source "
        "WHERE l IS NOT NULL AND b IS NOT NULL AND phot_g_mean_mag IS NOT NULL AND parallax IS NOT NULL "
        "AND parallax > 0 AND l BETWEEN 0 AND 360 AND b BETWEEN -90 AND 90 "
        "ORDER BY random_index"
    )
    results = job.get_results()

    # Extract l, b, and Magnitude
    l = results["l"].data
    b = results["b"].data
    mag = results["phot_g_mean_mag"].data
    parallax = results["parallax"].data # In case we want to use it later

    # Convert to Cartesian coordinates (using Earth as origin)
    distance_pc_gaia = 1 / (parallax)  # Convert parallax to distance in parsecs
    
    

    # Use astropy to convert galactic coordinates to Cartesian
    xyz_gaia = galactic_to_cartesian(l, b, distance_pc_gaia)

    # Calculate new origin based on the exoplanet
    planet_xyz = galactic_to_cartesian(galactic_long, galactic_lat, distance_pc)
    
    # Change coordinates to the inputted exoplanet as the new origin
    shifted_xyz = np.array(xyz_gaia) - np.array([planet_xyz]).reshape(3, 1)

    # Convert back to galactic coordinates
    l_new, b_new, d_new = cartesian_to_galactic(shifted_xyz[0], shifted_xyz[1], shifted_xyz[2])

    # Transform the magnitude values
    new_mag = mag
    # Normalize the new magnitude to use as sizes (smaller magnitude -> larger size)
    sizes_random = 10 ** (0.4 * (12 - new_mag))  # Adjust constant to scale sizes appropriately

    # Plot the data
    plt.figure(figsize=(80, 20))
    
    l_new_shifted = np.where(l_new > 180, l_new - 360, l_new)
    
    plt.scatter(l_new_shifted, b_new, s=sizes_random, color="white")
    plt.gca().invert_xaxis()  # Invert x-axis to match sky coordinates

    # Add axis labels
    plt.xlabel("Galactic Longitude (degrees)", fontsize=18)
    plt.ylabel("Galactic Latitude (degrees)", fontsize=18)

    # Set axis limits
    plt.xlim(-180, 180)  # x-axis now ranges from -180° to 180°
    plt.ylim(-90, 90)  # b ranges from -90° to 90°

    # Set title and background color
    plt.title(f"Sky Image from Gaia Data (Galactic Coordinates) - {planet_name}", fontsize=24)
    plt.gca().set_facecolor("black")  # Set background to black to represent the sky
    
    # Save the plot to a file
    plt.savefig(f'{planet_name}.jpg', facecolor="black")
    plt.close()  # Close the plot to free up memory
    
if __name__ == "__main__":
    query_gaia_and_create_png("Planet A", 225, 0, 10)



    # for exoplanet in exoplanets:
    #     name = exoplanet["name"]
    #     galactic_long = exoplanet["galactic_longitude"]
    #     galactic_lat = exoplanet["galactic_latitude"]
    #     distance_pc = exoplanet["distance_pc"]

    #     # Call the function for each exoplanet
    #     query_gaia_and_create_png(name, galactic_long, galactic_lat, distance_pc)