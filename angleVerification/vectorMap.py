import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from streamlit_globe import streamlit_globe
import streamlit as st
import re
from astropy.coordinates import EarthLocation
from astropy import units as u
from scipy.spatial.transform import Rotation as R
import gimbalMathCode as gimbalmath


def main():
    file = st.file_uploader("Upload a json space ephemeris", type=["json"], accept_multiple_files=False)
    if file is not None:
        try:
            # # Parse the JSON data
            data = fix_and_load_json(file)
            satellite_position = data['payloadData']['attributes']['translationState.position']['value']
            #gets the lat and long
            latitude, longitude = ecef_to_latlon(satellite_position)
            
            target_lat = st.text_input("Enter the latitude of the target")
            target_lon = st.text_input("Enter the longitude of the target")
            if target_lat == "" or target_lon == "":
                return
            target_lat = float(target_lat)
            target_lon = float(target_lon)
            angle, axis = gimbalmath.compute_angle_and_axis_astropy(satellite_position, target_lat, target_lon)
            lat2, long2 = hit_location(satellite_position, angle, axis)
            print("CALCULATED ANGLE: \n" + str(angle))
            pointsData=[{'lat': latitude, 'lng': longitude, 'size': 0.3, 'color': 'blue'}, {'lat': lat2, 'lng': long2, 'size': 0.3, 'color': 'red'}, {'lat': target_lat, 'lng': target_lon, 'size': 0.3, 'color': 'green'}]
            labelsData=[{'lat': latitude, 'lng': longitude, 'size': 5, 'color': 'red', 'text': 'Satellite Position'}, {'lat': lat2, 'lng': long2, 'size': 5, 'color': 'red', 'text': 'Calculated Trajectory'}, {'lat': target_lat, 'lng': target_lon, 'size': 5, 'color': 'green', 'text': 'Target Location'}]
            streamlit_globe(pointsData=pointsData, labelsData=labelsData, daytime='day', width=1000, height=600)
        except Exception as e: 
            st.error("Invalid JSON file: \n ERROR: \n" + str(e))


def fix_and_load_json(input_json_file_object):
    content = input_json_file_object.read().decode("utf-8")

    # Replace non-standard quotes with standard quotes
    content = content.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")

    # Replace non-standard whitespace characters
    content = re.sub(r'[^\S\n\t]', ' ', content)

    # Parse the fixed content into a JSON object
    try:
        json_object = json.loads(content)
        return json_object
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def hit_location(ecef, angle_degrees, rotation_axis):
    # Convert angle to radians
    angle_radians = np.radians(angle_degrees)

    # Create a quaternion from the angle and rotation axis
    quaternion = R.from_rotvec(rotation_axis * angle_radians)

    # Apply the quaternion to the satellite's ECEF coordinates
    rotated_ecef = quaternion.apply(ecef)

    # Calculate the intersection of the line with the Earth's surface
    # Assuming the Earth is a perfect sphere for simplicity
    # Normalize the rotated ECEF vector and scale by Earth's radius
    earth_radius = 6371 * 1000  # Earth's radius in meters
    norm_rotated_ecef = rotated_ecef / np.linalg.norm(rotated_ecef)
    intersection_ecef = norm_rotated_ecef * earth_radius

    # Convert ECEF to geodetic coordinates
    location = EarthLocation.from_geocentric(*intersection_ecef, unit=u.m)
    lat = location.lat.degree
    lon = location.lon.degree

    return (lat, lon)


#old parse json function
def parse_json(jsonPath):
    with open(jsonPath) as f:
        data = json.load(f)
        satellite_position = data['payloadData']['attributes']['translationState.position']['value']
        return satellite_position



# Define a function to convert ECEF to latitude and longitude
def ecef_to_latlon(ecef):
    # This is a simplified formula and may not be accurate for all cases
    x, y, z = ecef
    print(x, y, z)
    a = 6378137.0  # Earth's radius in meters
    e2 = 0.00669437999014  # Eccentricity squared

    # Calculate longitude
    lon = np.arctan2(y, x)

    # Calculate latitude
    p = np.sqrt(x**2 + y**2)
    theta = np.arctan2(z * a, p * (1 - e2))
    lat = np.arctan2(z + e2 * a * np.sin(theta)**3, p - e2 * a * np.cos(theta)**3)

    return np.degrees(lat), np.degrees(lon)



def hit_location(ecef, angle_degrees, rotation_axis):
    # Convert angle to radians
    angle_radians = np.radians(angle_degrees)

    # Create a quaternion from the angle and rotation axis
    quaternion = R.from_rotvec(rotation_axis * angle_radians)

    # Apply the quaternion to the satellite's ECEF coordinates
    rotated_ecef = quaternion.apply(ecef)

    # Calculate the intersection of the line with the Earth's surface
    # Assuming the Earth is a perfect sphere for simplicity
    # Normalize the rotated ECEF vector and scale by Earth's radius
    earth_radius = 6371 * 1000  # Earth's radius in meters
    norm_rotated_ecef = rotated_ecef / np.linalg.norm(rotated_ecef)
    intersection_ecef = norm_rotated_ecef * earth_radius

    # Convert ECEF to geodetic coordinates
    location = EarthLocation.from_geocentric(*intersection_ecef, unit=u.m)
    lat = location.lat.degree
    lon = location.lon.degree

    return lat, lon


#Page config info
st.set_page_config(
    page_title="CubeSat Gimbal",
    page_icon="🧊",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>CubeSat Gimbal</h1>", unsafe_allow_html=True) 



main()
