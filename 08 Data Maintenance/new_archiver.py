import os
import zlib
from google.cloud import pubsub_v1
from google.cloud import storage
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Project ID and Subscription details
project_id = "scientific-pad-420219"
subscription_name = "archeivetest-sub"
bucket_name = "data-eng-activity"

# Initialize a Subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

# Initialize a Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# RSA key generation and saving the private key
key = RSA.generate(2048)
private_key = key.export_key()
with open("private.pem", "wb") as f:
    f.write(private_key)

# Public key for encryption
public_key = key.publickey().export_key()
public_key = RSA.import_key(public_key)
cipher_rsa = PKCS1_OAEP.new(public_key)

def callback(message):
    print(f"Received message: {message.data}")
    # Create a unique filename for each message based on the current timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"breadcrumb_{timestamp}.txt"
    
    # Compress the message data using zlib
    compressed_data = zlib.compress(message.data)
    
    # Encrypt the compressed data using RSA
    encrypted_data = cipher_rsa.encrypt(compressed_data)
    encrypted_filename = f"{filename}.zlib.enc"
    
    # Upload the encrypted data to the bucket
    blob = bucket.blob(encrypted_filename)
    blob.upload_from_string(encrypted_data)
    
    print(f"Stored encrypted and compressed message to {encrypted_filename} in bucket {bucket_name}")
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

