# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 12:35:36 2024

@author: Jithendra
"""

import requests
import json
from google.cloud import pubsub_v1

# Set your Google Cloud project ID and Pub/Sub topic ID
project_id = "pubsubtask16042024"
topic_id = "MyTopic"

# Initialize the Pub/Sub Publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Function to fetch data from the API and publish to Pub/Sub
def fetch_and_publish_data(vehicle_id):
    url = f"https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id={vehicle_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open(f"bcsample_{vehicle_id}.json", "w") as file:
            json.dump(data, file)
        for record in data:
            data_str = json.dumps(record)
            data_bytes = data_str.encode("utf-8")
            future = publisher.publish(topic_path, data=data_bytes)
            print(f"Published message: {future.result()}")
    else:
        print(f"Failed to fetch data for vehicle ID {vehicle_id}")

vehicle_ids = ["3010", "3951"]

for vehicle_id in vehicle_ids:
    fetch_and_publish_data(vehicle_id)

print(f"Published messages to {topic_path}.")