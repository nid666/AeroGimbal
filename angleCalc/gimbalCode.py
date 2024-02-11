import numpy as np
import json
from astropy import units as u
from astropy.coordinates import EarthLocation, ITRS, GCRS, SkyCoord
from astropy.time import Time

# Function to parse the given JSON
def parse_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
        satellite_position = data["payloadData"]["attributes"]["translationState.position"]["value"]
        print(satellite_position)
        return satellite_position

# Function to compute the angle and the axis using Astropy
def compute_angle_and_axis_astropy(satellite_position, target_lat, target_lon):
    # Current time in UTC
    t = Time.now()  # This gets the current time
    
    # Convert ECEF satellite position to Astropy CartesianRepresentation
    satellite_cartesian = SkyCoord(x=satellite_position[0]*u.m, 
                                   y=satellite_position[1]*u.m, 
                                   z=satellite_position[2]*u.m, 
                                   frame=ITRS(obstime=t), 
                                   representation_type='cartesian')
    
    # Convert satellite position to GCRS to account for Earth rotation
    satellite_gcrs = satellite_cartesian.transform_to(GCRS(obstime=t))
    
    # Create EarthLocation object for the target location
    target_location = EarthLocation(lat=target_lat*u.deg, lon=target_lon*u.deg)
    
    # Get the GCRS position of the target
    target_gcrs = target_location.get_gcrs(obstime=t)
    
    # Compute vector from satellite to target in GCRS frame
    vector_to_target = target_gcrs.cartesian.xyz.value - satellite_gcrs.cartesian.xyz.value
    
    # Nadir direction is just the negative of satellite position (normalized)
    nadir_vector = -satellite_gcrs.cartesian.xyz.value / np.linalg.norm(satellite_gcrs.cartesian.xyz.value)
    
    # Calculate the rotation axis, which is the cross product of the nadir vector and the vector_to_target
    rotation_axis = np.cross(nadir_vector, vector_to_target)
    rotation_axis_normalized = rotation_axis / np.linalg.norm(rotation_axis)

    # Compute the angle between the two vectors
    cos_angle = np.dot(vector_to_target, nadir_vector) / (np.linalg.norm(vector_to_target) * np.linalg.norm(nadir_vector))
    angle_rad = np.arccos(np.clip(cos_angle, -1.0, 1.0))  # Clipped to avoid numerical errors outside the domain of arccos
    
    # Convert to degrees
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg, rotation_axis_normalized

# Example:
json_data = 'data.json'
satellite_position = parse_json(json_data)
target_lat = 0  # Latitude in degrees
target_lon = 0  # Longitude in degrees

angle, axis = compute_angle_and_axis_astropy(satellite_position, target_lat, target_lon)
print(f"Angle (degrees): {angle}")
print(f"Rotation axis (normalized): {axis}")
