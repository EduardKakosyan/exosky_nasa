import os
import certifi
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia
from astropy import units as u
import numpy as np
from astropy.coordinates import Galactic, CartesianRepresentation
from exoplanet_data import exoplanets

os.environ["SSL_CERT_FILE"] = certifi.where()

def galactic_to_cartesian(l, b, distance_pc):
    galactic_coord = Galactic(l=l*u.deg, b=b*u.deg, distance=distance_pc*u.pc)
    
    # Convert to Cartesian representation
    cartesian_coord = galactic_coord.cartesian

    # Extract x, y, z in parsecs
    x = cartesian_coord.x.value
    y = cartesian_coord.y.value
    z = cartesian_coord.z.value
    
    return x, y, z

def cartesian_to_galactic(x, y, z):
    cartesian_coord = CartesianRepresentation(x=x*u.pc, y=y*u.pc, z=z*u.pc)
    
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

def query_gaia():
    """Query Gaia catalog once and return results."""
    job = Gaia.launch_job_async(
        "SELECT TOP 500000 l, b, phot_g_mean_mag, parallax "
        "FROM gaiadr3.gaia_source "
        "WHERE l IS NOT NULL AND b IS NOT NULL AND phot_g_mean_mag IS NOT NULL AND parallax IS NOT NULL "
        "AND parallax > 0 AND l BETWEEN 0 AND 360 AND b BETWEEN -90 AND 90 "
        "ORDER BY random_index"
    )
    return job.get_results()

def create_png_for_exoplanet(planet_name, galactic_long, galactic_lat, distance_pc, gaia_results):
    # Extract l, b, and Magnitude from Gaia results
    l = gaia_results["l"].data
    b = gaia_results["b"].data
    mag = gaia_results["phot_g_mean_mag"].data
    parallax = gaia_results["parallax"].data  # In case we want to use it later

    # Convert parallax to distance in parsecs
    distance_pc_gaia = 1000 / parallax
    
    # Convert to Cartesian coordinates (using Earth as origin)
    x_gaia, y_gaia, z_gaia = galactic_to_cartesian(l, b, distance_pc_gaia)

    # Convert the exoplanet's galactic coordinates to Cartesian
    planet_x, planet_y, planet_z = galactic_to_cartesian(galactic_long, galactic_lat, distance_pc)

    # Shift the star positions to make the exoplanet the new origin
    shifted_x = x_gaia - planet_x
    shifted_y = y_gaia - planet_y
    shifted_z = z_gaia - planet_z
    
    # Convert back to galactic coordinates
    l_new, b_new, d_new = cartesian_to_galactic(shifted_x, shifted_y, shifted_z)

    # Normalize the new magnitude to use as sizes (smaller magnitude -> larger size)
    sizes_random = 10 ** (0.4 * (12 - mag))  # Adjust constant to scale sizes appropriately

    # Plot the data
    plt.figure(figsize=(80, 20))
    
    l_new_shifted = np.where(l_new > 180, l_new - 360, l_new)
    
    plt.scatter(l_new_shifted, b_new, s=sizes_random, color="white")

    # Add axis labels
    plt.xlabel("Galactic Longitude (degrees)", fontsize=18)
    plt.ylabel("Galactic Latitude (degrees)", fontsize=18)

    # Set title and background color
    plt.title(f"Sky Image from Gaia Data (Galactic Coordinates) - {planet_name}", fontsize=24)
    plt.gca().set_facecolor("black")  # Set background to black to represent the sky
    
    # Save the plot to a file
    plt.savefig(f'{planet_name}.jpg', facecolor="black")
    plt.close()  # Close the plot to free up memory

if __name__ == "__main__":
    # Query the Gaia catalog once
    gaia_results = query_gaia()

    create_png_for_exoplanet("Earth", 0, 0, 0, gaia_results)
    create_png_for_exoplanet("Planet Right", 90, 0, 1000, gaia_results)
    create_png_for_exoplanet("Planet Back", 180, 0, 1000, gaia_results)
    create_png_for_exoplanet("Planet Back", 270, 0, 1000, gaia_results)
    # for exoplanet in exoplanets:
    #     name = exoplanet["name"]
    #     galactic_long = exoplanet["galactic_longitude"]
    #     galactic_lat = exoplanet["galactic_latitude"]
    #     distance_pc = exoplanet["distance_pc"]

    #     # Call the function for each exoplanet
    #     create_png_for_exoplanet(name, galactic_long, galactic_lat, distance_pc, gaia_results)
