# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 12:26:43 2024

@author: Jithendra
"""

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

project_id = "pubsubtask16042024"
subscription_id = "MySub"
timeout = 5.0

# Initialize the Pub/Sub Subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Define the callback function to process incoming messages
def callback(message):
    print(f"Received message: {message.data.decode('utf-8')}")
    message.ack()

# Subscribe to the Pub/Sub topic
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...\n")

# Wait for messages
try:
    streaming_pull_future.result(timeout=timeout)
except TimeoutError:
    streaming_pull_future.cancel()
    streaming_pull_future.result()  