#טעינה
import os
from dotenv import load_dotenv

load_dotenv()

FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "articles")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
