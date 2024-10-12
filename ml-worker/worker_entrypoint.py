import logging
import os
import sys
import tempfile

import cv2
import requests
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker

from db.config import postgres_async_config
from db.models.video import Video
from utils.minio_client import minio_client

from confluent_kafka import Consumer, KafkaError, KafkaException
from websocket import create_connection

engine = create_engine(postgres_async_config.SYNC_POSTGRES_URL, echo=True)
SessionFactory = sessionmaker(bind=engine)


def update_state(video_path, state):
    with SessionFactory() as session:
        stmt = (update(Video).
                where(Video.path == video_path).
                values(state=state)
                )

        session.execute(stmt)

        session.commit()


backend_host = os.environ.get('BACKEND_HOST', 'localhost')
backend_port = os.environ.get('BACKEND_PORT', 8000)
backend_domain = f"{backend_host}{':' + str(backend_port) if backend_port else ''}"

kafka_brokers = os.getenv("KAFKA_BROKERS", "localhost:9092")

conf = {
    'bootstrap.servers': kafka_brokers,
    'group.id': 'my_consumer_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['video'])


def generate_frames(video_file) -> bytes:
    frame_count = 0
    try:
        with open('temp.mp4', 'wb') as f:
            f.write(video_file)

        video = cv2.VideoCapture('temp.mp4')

        while True:
            ret, frame = video.read()
            if not ret:
                break

            (ret, jpeg) = cv2.imencode(".jpg", frame)
            frame_count += 1
            try:
                pass
            except Exception as e:
                print(f"Ошибка: {e}")
            if ret:
                yield frame_count, [jpeg.tobytes()]
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        os.remove('temp.mp4')


def process_video(video_file):
    #TODO yield frame in video_file это пример того, как оно работает
    i = 0
    while i < 100:
        yield i, i
        i += 1
        print(i)
    if i == 100:
        return


# ПОТОМ НОРМ ДОБАВЛЮ
#
# db = psycopg2.connect(
#     host="localhost",
#     database="mydatabase",
#     user="myuser",
#     password="mypassword"
# )

def process_stream(video_name):
    # temp_input_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    # temp_output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")

    path = minio_client.download_file('localbucket', video_name)
    path = path[1]

    try:

        with open(path, 'rb') as f:
            minio_client.upload_file('localbucket', 'processed/' + video_name, f)

        os.remove(path)
    except Exception as e:
        print(f"Ошибка: {e}")
        return
    return


class VideoProcessingActor:

    def __init__(self):
        self.progress = 0
        self.logger = logging.getLogger(__name__)

    #эндпоинта пока нет
    def send_progress(self):
        ws = create_connection(f"ws://{backend_domain}/video_api/ws/progress/")
        ws.send(self.progress)

    @staticmethod
    def send_result(result):
        """
        Для обработки в реальном времени

        """
        ws = create_connection(f"ws://{backend_domain}/video_api/ws/message/")
        ws.send(result)

    @staticmethod
    def send_result_post_request(result):
        req = requests.post(f"http://{backend_domain}/video_api/post_video_from_ml/", data=result)

    def process_message(self, message):

        update_state(message, "PROCESSING")
        try:
            process_stream(message)
        except Exception as e:
            print(f"Ошибка: {e}")
            update_state(message, "FAILED")

        consumer.commit()
        update_state(message, "SUCCESSFUL")


running = True


def shutdown():
    running = False


def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)
        print("Start consuming")

        while running:
            msg = consumer.poll(timeout=1.0)
            print('msg: ', msg)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    continue
                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))

                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                actor = VideoProcessingActor()
                actor.process_message(msg.value().decode('utf-8'))
    finally:
        consumer.close()


if __name__ == '__main__':
    basic_consume_loop(consumer, ['video'])
