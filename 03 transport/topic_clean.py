# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 12:29:42 2024

@author: Jithendra
"""

from google.cloud import pubsub_v1
project_id = "pubsubtask16042024"
topic_name = "MyTopic"
subscriber = pubsub_v1.SubscriberClient()
topic_path = subscriber.topic_path(project_id, topic_name)
subscriptions = subscriber.list_subscriptions(project=f"projects/{project_id}")
for subscription in subscriptions:
    if topic_path in subscription.topic:
        subscription_path = subscription.name
        subscriber.delete_subscription(request={"subscription": subscription_path})
        print(f"All messages in subscription '{subscription_path}' have been deleted.")

print(f"All messages in topic '{topic_path}' have been deleted.")