import os

from apscheduler.schedulers.blocking import BlockingScheduler
from confluent_kafka import Producer
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

from db.config import postgres_async_config
from db.models.video import Video


engine = create_engine(postgres_async_config.SYNC_POSTGRES_URL)
SessionFactory = sessionmaker(bind=engine)

def select_failed_videos():
    with SessionFactory() as session:
        query = select(Video).where(Video.state == "FAILED")
        result = session.execute(query)
        failed_videos = result.scalars().all()
        return failed_videos


def produce_video(file_name):
    kafka_brokers=os.getenv("KAFKA_BROKERS", "localhost:9092")
    kafka_producer = Producer({
        'bootstrap.servers': kafka_brokers,
        'broker.address.family': 'v4'  # Update with your Kafka broker address
    })
    kafka_producer.produce('video', value=file_name)
    kafka_producer.flush()
def check_failed_records_and_send_to_kafka():
    print("check_failed_records_and_send_to_kafka")
    deleted_videos = select_failed_videos()
    for video in deleted_videos:
        produce_video(video.path)


scheduler = BlockingScheduler()
scheduler.add_job(check_failed_records_and_send_to_kafka, 'interval',seconds=5)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass