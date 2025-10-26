# nlp/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Kafka (Aiven)
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_TOPIC_NEWS = os.getenv("KAFKA_TOPIC_NEWS", "news-events")

# Supabase (database)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Cloudinary (media)
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# MCP (AI Agents / Coordination)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

# General
PROJECT_NAME = "Realtime News Agents"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
