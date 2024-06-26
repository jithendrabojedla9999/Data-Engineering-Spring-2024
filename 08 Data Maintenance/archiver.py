import os
from google.cloud import pubsub_v1
from google.cloud import storage
from datetime import datetime

# Project ID and Subscription details
project_id = "scientific-pad-420219"
subscription_name = "archeivetest-sub"
bucket_name = "dataengactivity"

# Initialize a Subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

# Initialize a Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def callback(message):
    print(f"Received message: {message.data}")
    # Create a unique filename for each message based on the current timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"breadcrumb_{timestamp}.txt"
    blob = bucket.blob(filename)
    blob.upload_from_string(message.data.decode('utf-8'))
    print(f"Stored message to {filename} in bucket {bucket_name}")
    message.ack()  # Acknowledge the message

# Create the subscription if it doesn't exist
def create_subscription():
    topic_path = subscriber.topic_path(project_id, "archeivetest")
    try:
        subscriber.create_subscription(name=subscription_path, topic=topic_path)
        print(f"Subscription {subscription_name} created.")
    except Exception as e:
        print(f"Subscription {subscription_name} already exists or failed to create: {e}")

create_subscription()

# Subscribe to the topic
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...")

# Block the main thread while waiting for messages
try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()

