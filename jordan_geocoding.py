import requests

# Set up geocoding service URL
url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

# Pre-inserted address
address = "1600 Amphitheatre Parkway, Mountain View, CA"  # Replace with your desired address

# Create the request payload
params = {
    "SingleLine": address,
    "f": "json",
    "outSR": "4326"
}

# Send the request and retrieve the response
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Check if there are any candidates found
    if "candidates" in data:
        # Get the first candidate
        candidate = data["candidates"][0]

        # Extract the latitude and longitude
        location = candidate["location"]
        latitude = location["y"]
        longitude = location["x"]

        print("Latitude: {}, Longitude: {}".format(latitude, longitude))
    else:
        print("No candidates found.")
else:
    print("Request failed.")

print("Done geocoding")
