import os
import certifi
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia

os.environ['SSL_CERT_FILE'] = certifi.where()

def query_gaia_and_create_png():
    print("Hello world")

if __name__ == "__main__":
    print(query_gaia_and_create_png())