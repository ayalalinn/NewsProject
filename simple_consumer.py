import asyncio
import json
import ssl
from aiokafka import AIOKafkaConsumer
import os

async def consume():
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-247f753c-hadarn26-c7d5.i.aivencloud.com:10544")

    # הגדרת SSL
    ssl_context = ssl.create_default_context(cafile=r"./secrets/aiven/ca.pem")
    ssl_context.load_cert_chain(
        certfile=r"./secrets/aiven/service.cert",
        keyfile=r"./secrets/aiven/service.key"
    )

    consumer = AIOKafkaConsumer(
        "news.raw",
        bootstrap_servers=kafka_bootstrap,
        group_id="test-group",
        security_protocol="SSL",
        ssl_context=ssl_context
    )

    await consumer.start()
    print("📡 מאזין ל־Kafka topic: news.raw ...")
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            print("📰 הודעה התקבלה:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())
