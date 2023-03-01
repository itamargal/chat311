#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""chat311

A simple app to generate 311 service requests using OpenAI.

NOTE: Generate an OpenAI API key and export it to the OPENAI_API_KEY environment variable.

You must export the following variables to your environment in order to write to the database:

CHAT311_HOSTNAME
CHAT311_DATABASE
CHAT311_USERNAME
CHAT311_PASSWORD
"""

# Standard Libraries
from datetime import datetime, timezone
import csv
import logging
import os

# 3rd Party Libraries
from pymysql.cursors import DictCursor
import openai
import pandas as pd
import pymysql
import requests
import streamlit as st


def geocode(address, chat311_config=None):
    """Geocode an address using the HERE API."""

    # Load config if not provided
    if not chat311_config:
        chat311_config = get_chat311_config()

    # Get parameters for geocoding service
    here_api_key = chat311_config["HERE_API_KEY"]
    url = "https://geocode.search.hereapi.com/v1/geocode"
    querystring = {"q": address, "apiKey": here_api_key}

    # Submit geocoding request
    response = requests.request("GET", url, headers={}, params=querystring)
    logging.debug("Geocoding address: %s", address)
    logging.debug(response.text)

    # Parse response, get first match, and extract coordinates
    try:
        top_result = response.json()["items"][0]
        lat, lng = top_result["position"]["lat"], top_result["position"]["lng"]
        coordinates = {"lat": lat, "lng": lng}
    except Exception as error:
        logging.warning(error)
        coordinates = None

    return coordinates

    """Generate a service request from a complaint string."""

    # A list of request categories
    request_categories = [
        "pavement markings",
        "potholes",
        "snow & ice",
        "sidewalks",
        "street lights",
        "traffic signals",
        "traffic & parking signs",
        "To report an abandoned vehicle, please call the Syracuse Police Ordinance at 315-448-8650. If this is an emergency, please call 911. Do NOT submit requests to Cityline.",
        "To report an illegally parked vehicle, please call the Syracuse Police Ordinance at 315-448-8650. If this is an emergency, please call 911. Do NOT submit requests to Cityline.",
        "Parking Meter",
        "Parking Tickets",
        "Other Parking & Vehicles Concern",
        "Dog Control",
        "Roadkill",
        "Animal Control",
        "Deer Sighting",
        "Graffiti on Private Land",
        "Electronics & Hazardous Waste",
        "Illegal Setouts",
        "Large or Bulk Items- Setout notification only",
        "Large or Bulk Items- Skipped Pickup",
        "Tires",
        "Public Trash Can",
        "Recycling",
        "Recycling (pick up that has been skipped)",
        "Report Litter on Private Land",
        "Weekly Trash Pickup",
        "Register for Adopt-A-Block",
        "Adopt-A-Block - Request for Trash pick up",
        "Yard Waste",
        "Graffiti on Public Land",
        "Report Litter on Public Land",
        "Home & Building Maintenance",
        "Vacant Buildings",
        "Vacant Land",
        "Report Overgrown Grass on Private Land",
        "Report Trash/Debris Outside a Home/Building",
        "Other Housing & Property Maintenance Concern",
        "Overgrown Grass in Public Spaces",
        "Park Maintenance",
        "Playground Equipment",
        "Tree Care and Removal",
        "Other Parks, Trees & Public Utilities Concern",
        "Request a free street tree planting (City of Syracuse Property Owners Only)",
        "Sewer-related Concerns",
        "Water-related Concerns",
        "Health, Safety & Social Services",
    ]

    # Create prompt to generate request category
    category_prompt_template = """Based on the complaint: "{complaint}", print the best category of request from this list:

    {request_categories}

    Only print a single result.
    """
    category_prompt = category_prompt_template.format(
        complaint=complaint,
        request_categories="\n".join(request_categories)
    )

    # Create prompt to generate request severity
    severity_prompt_template = """Based on the complaint: "{complaint}", print the severity of the issue. Only print a single result."""
    severity_prompt = severity_prompt_template.format(complaint=complaint)

    # Create prompt to generate request description
    description_prompt_template = """Based on the complaint: "{complaint}", print a description of the issue. Only print a single sentence."""
    description_prompt = description_prompt_template.format(complaint=complaint)

    # Create prompt to generate request location description
    location_prompt_template = """Based on the complaint: "{complaint}", describe the location of the issue (in a single sentence)."""
    location_prompt = location_prompt_template.format(complaint=complaint)

    # Create prompt to generate request location coordinates
    coordinates_prompt_template = """Based on the complaint: "{complaint}", print the location of the issue (in latitude/longitude format)."""
    coordinates_prompt = coordinates_prompt_template.format(complaint=complaint)

    # Get the category
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=category_prompt,
            max_tokens=4097 - len(category_prompt),
    )
    category = response.choices[0].text.strip()

    # Get the severity
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=severity_prompt,
            # temperature=0.5,
            max_tokens=4097 - len(severity_prompt),
            # top_p=1,
            # frequency_penalty=0.2,
            # presence_penalty=0,
            # stop=["\"\"\""],
            stream=False,
    )
    severity = response.choices[0].text.strip()

    # Get the request description
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=description_prompt,
            # temperature=0.5,
            max_tokens=4097 - len(description_prompt),
            # top_p=1,
            # frequency_penalty=0.2,
            # presence_penalty=0,
            # stop=["\"\"\""],
            stream=False,
    )
    description = response.choices[0].text.strip()

    # Get the location description
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=location_prompt,
            # temperature=0.5,
            max_tokens=4097 - len(description_prompt),
            # top_p=1,
            # frequency_penalty=0.2,
            # presence_penalty=0,
            # stop=["\"\"\""],
            stream=False,
    )
    location = response.choices[0].text.strip()

    # Get the lat/lon coordinates
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=coordinates_prompt,
            # temperature=0.5,
            max_tokens=4097 - len(coordinates_prompt),
            # top_p=1,
            # frequency_penalty=0.2,
            # presence_penalty=0,
            # stop=["\"\"\""],
            stream=False,
    )
    coordinates = response.choices[0].text.strip()

    # Log the results from OpenAI
    logging.info("category: %s", category)
    logging.info("severity: %s", severity)
    logging.info("description: %s", description)
    logging.info("location: %s", location)
    logging.info("coordinates: %s", coordinates)

    # Extract the latitude and longitude from the location string
    latitude, longitude = [_.strip() for _ in coordinates.split(",")]
    logging.info("latitude: %s", latitude)
    logging.info("longitude: %s", longitude)

    # Create a service request object
    service_request_object = {
        "complaint": complaint,
        "category": category,
        "severity": severity,
        "description": description,
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "created_datetime": datetime.now(timezone.utc).isoformat(),
    }

    logging.info("Generated service request object")
    logging.info(service_request_object)

    return service_request_object


def get_service_request_string(service_request_object):
    """Return a string representation of a service request object."""

    # A string template for the output format.
    service_request_template = """
    Service Request:

    Location: {location}
    Latitude: {latitude}
    Longitude: {longitude}
    Severity: {severity}
    Category: {category}

    Description: {description}

    Note: If this is an emergency, please call 911. For reporting an abandoned vehicle or an illegally parked vehicle, please call the Syracuse Police Ordinance at 315-448-8650. For all non-emergencies and service requests, call (315) 448-CITY (2489). The category chosen for this request is {category}.
    """

    return service_request_template.format(**service_request_object)


def write_to_database(service_request_object, chat311_config):
    """Write a service request object to a database."""

    # Create a database connection
    connection = pymysql.connect(
        host     = chat311_config["CHAT311_HOSTNAME"],
        user     = chat311_config["CHAT311_USERNAME"],
        passwd   = chat311_config["CHAT311_PASSWORD"],
        db       = chat311_config["CHAT311_DATABASE"],
        ssl      = {
            "ca": "/etc/ssl/cert.pem"
        },
        ssl_verify_cert = True,
    )

    # Create a cursor
    cursor = DictCursor(connection)

    # Create a table if it doesn't already exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            complaint TEXT,
            category TEXT,
            severity TEXT,
            description TEXT,
            location TEXT,
            latitude TEXT,
            longitude TEXT,
            created_datetime TEXT
        );
        """
    )

    # Insert the service request object into the database
    cursor.execute(
        """
        INSERT INTO service_requests (complaint, category, severity, description, location, latitude, longitude, created_datetime)
        VALUES (%(complaint)s, %(category)s, %(severity)s, %(description)s, %(location)s, %(latitude)s, %(longitude)s, %(created_datetime)s)
        """,
        service_request_object,
    )

    # Commit the changes
    connection.commit()

    # Close the database connection
    connection.close()


def get_chat311_config():
    """Return a dictionary of configuration parameters."""

    # List of configuration parameters / environment variables
    config_params = [
        "OPENAI_API_KEY",
        "CHAT311_HOSTNAME",
        "CHAT311_DATABASE",
        "CHAT311_USERNAME",
        "CHAT311_PASSWORD",
    ]

    # Load configuration from st.secrets (secrets.toml) or shell environment

    # Load configuration from st.secrets (secrets.toml)
    try:
        chat311_config = {param: st.secrets[param] for param in config_params}
        logging.info("Loaded configuration from st.secrets (secrets.toml)")
    except KeyError as error:
        logging.warning("Variable missing from st.secrets (secrets.toml): %s", error)
        logging.warning("Unable to load configuration from st.secrets (secrets.toml)")
        chat311_config = None

    # Load configuration from shell environment if not already loaded
    if not chat311_config:
        try:
            chat311_config = {param: os.environ[param] for param in config_params}
            logging.info("Loaded configuration from shell environment")
        except KeyError as error:
            logging.warning("Variable missing from shell environment: %s", error)
            logging.warning("Unable to load configuration from shell environment")
            chat311_config = None

    if not chat311_config:
        logging.warning("Unable to load configuration from st.secrets (secrets.toml) or shell environment")

    return chat311_config


def streamlit_app(csv_output_filename=False):
    """Launch a Streamlit app to generate service requests from complaints."""

    # Load configuration
    try:
        chat311_config
    except NameError:
        chat311_config = get_chat311_config()

    # Initialize state variables
    service_request = None
    complaint = None

    # Get input from user
    complaint = st.text_input(
        "Service Request Description",
        value="",
        max_chars=None,
        key=None,
        type="default",
        help=None,
        autocomplete=None,
        on_change=None,
        args=None,
        kwargs=None,
        placeholder=None,
        disabled=False,
        label_visibility="visible",
    )

    if complaint:
        service_request_object = generate_service_request_object(complaint)
        service_request = get_service_request_string(service_request_object)

    if service_request:

        # Display service request
        st.text_area(
            label="Service Request",
            value=service_request,
            height=None,
            max_chars=None,
            key=None,
            help=None,
            on_change=None,
            args=None,
            kwargs=None,
            placeholder=None,
            disabled=False,
            label_visibility="visible",
        )

        # Display location on map or display warning if location is not available
        try:
            latitute = float(service_request_object["latitude"])
            longitude = float(service_request_object["longitude"])
            df = pd.DataFrame([[latitute, longitude]], columns=['lat', 'lon'])
            st.map(df)
        except ValueError:
            logging.warning("Unable to display location on map")
            st.warning("Unable to display location on map")

        # Log results to csv file
        if csv_output_filename:
            fieldnames = (
                "complaint",
                "description",
                "category",
                "severity",
                "location",
                "latitude",
                "longitude",
                "created_datetime",
            )
            record = { key: value for key, value in service_request_object.items() if key in fieldnames }
            with open(csv_output_filename, "a", encoding="utf-8") as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writerow(record)

        # Write results to database
        write_to_database(service_request_object, chat311_config)


if __name__=="__main__":
    streamlit_app()