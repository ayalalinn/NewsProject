import os
import json
import ssl
from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv

# טוען משתנים מקובץ .env
load_dotenv()

async def send_to_kafka(topic: str, message: dict, key: str = None):
    """שולח הודעת JSON ל־Kafka ב־Aiven"""
    
    # בונה SSLContext נכון
    ssl_context = ssl.create_default_context(cafile=os.getenv("KAFKA_SSL_CAFILE"))
    ssl_context.load_cert_chain(
        certfile=os.getenv("KAFKA_SSL_CERTFILE"),
        keyfile=os.getenv("KAFKA_SSL_KEYFILE")
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL"),
        ssl_context=ssl_context,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8") if v else None,
    )

    await producer.start()
    try:
        await producer.send_and_wait(topic, key=key, value=message)
        print(f"✅ נשלחה הודעה ל־Kafka: {message.get('title', '(ללא כותרת)')}")
    finally:
        await producer.stop()
