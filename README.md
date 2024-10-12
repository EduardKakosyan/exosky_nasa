# Sky Painters: An Interactive Exoplanetary Sky Experience

## NASA Space Apps Challenge 2024
Visit our website: [Sky Painters](https://skypainter.fly.dev/)
https://github.com/user-attachments/assets/1c1a8f44-ed77-40c1-a940-52181bc06906


## Project Overview
Sky Painters is an interactive web application that allows users to experience the night sky from the perspective of exoplanets across the Milky Way. By utilizing data from the **Gaia Data Release 3 (Gaia DR3)** and the **NASA Exoplanet Archive**, this app enables students to explore and visualize how the sky would appear from different exoplanets. It offers both an immersive 3D model of the galaxy and a hands-on educational tool where users can draw constellations.

## Features
- **Exoplanetary Viewpoints:** Select from a range  of exoplanets and observe the night sky as it would appear from each of them.
- **Interactive 360-Degree Sky Map:** Explore the Milky Way in a fully navigable, 3D, 360-degree environment.
- **Constellation Drawing Tool:** Draw your own constellations on the sky map.
- **Realistic Star Magnitude Adjustments:** Star brightness is adjusted based on recalculated magnitudes from the exoplanet’s perspective, ensuring accurate and immersive visualization.

## Math and Science Concepts

Sky Painter is designed to provide mathematically accurate point of view from each exoplanet.
This is achieved using a custom database crafted for this project. Each image is generated using 
over **13 million** stars from the Gaia DR3 dataset. Each star distance is transformed to 
cartesian coordinates and stored in a PostgreSQL database. During the rendering process, 
this database is then queried to retrieve the stars that are visible from the exoplanet.
The cartesian coordinates are transformed back to galactic coordinates. Additionally, the magnitude of each star is adjusted based on the distance from the exoplanet. This ensures that the stars are displayed with the correct brightness.

## Technologies Used
- **Frontend:** React, Three.js, TypeScript, Tailwind CSS
- **Backend:** Python, PostgreSQL, Docker
- **Deployment:** Fly.io, GitHub

## Team Members
- **[Eduard Kakosyan](kakosyaneduard@dal.ca)**
- **[Huy Huynh](huy.huynh@dal.ca)**
- **[Hao Tang](@dal.ca)**
- **[Phuc Than](@dal.ca)**
- **[Adnan Abdul Rahim](@dal.ca)**
