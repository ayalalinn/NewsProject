import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env
load_dotenv()

# Get the service account path
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred_path or not os.path.exists(cred_path):
    raise SystemExit(f"❌ Service account file not found: {cred_path!r}. Check .env and secrets folder.")

# Initialize Firebase app (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Create Firestore client
db = firestore.client()

# Write a test document
doc_ref = db.collection(os.getenv("FIRESTORE_COLLECTION", "news_items")).document()
doc_ref.set({
    "title": "Connection Test",
    "summary": "Smoke test - Firestore connection successful."
})

print("✅ Document written successfully with ID:", doc_ref.id)

# Read back to verify
doc = doc_ref.get()
print("🔎 Read back:", doc.to_dict())

