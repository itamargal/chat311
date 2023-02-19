#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""chat311

A simple app to generate 311 service requests using OpenAI.

NOTE: Generate an OpenAI API key and export it to the OPENAI_API_KEY environment variable.
"""

import openai
import streamlit as st


def generate_service_request(complaint):
    """Generate a service request from a complaint string."""

    # A string template for the output format.
    service_request_template = """
    Service Request:

    Location: {location}
    Latitude: {latitude}
    Longitude: {longitude}
    Severity: {severity}
    Category: {category}

    Description: {description}

    Note: If this is an emergency, please call 911. For reporting an abandoned vehicle or an illegally parked vehicle, please call the Syracuse Police Ordinance at 315-448-8650. The category chosen for this request is Street Lights as it pertains to a broken street light.
    """

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

    # print(category)
    # print(severity)
    # print(description)
    # print(location)
    # print(coordinates)

    latitude, longitude = [_.strip() for _ in coordinates.split(",")]
    # print(latitude)
    # print(longitude)

    return service_request_template.format(
        category=category,
        severity=severity,
        description=description,
        location=location,
        latitude=latitude,
        longitude=longitude,
    )

def streamlit_app():
    """Launch a Streamlit app to generate service requests from complaints."""
    service_request = None
    complaint = None
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
        service_request = generate_service_request(complaint)

    if service_request:
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

if __name__=="__main__":
    streamlit_app()
