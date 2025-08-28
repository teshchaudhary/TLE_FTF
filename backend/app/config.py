import os
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
DISASTER_INDEX = os.getenv("DISASTER_INDEX")
