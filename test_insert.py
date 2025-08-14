from api_handler import get_channel_details
from db_inserter import insert_channel

channel_id = "UCMiJRAwDNSNzuYeN2uWa0pA"  # Replace with any working channel ID
data = get_channel_details(channel_id)
insert_channel(data)
print("Inserted successfully")