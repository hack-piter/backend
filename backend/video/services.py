import base64
import datetime
import logging
import os
import hashlib

import cv2
import numpy as np
from fastapi import UploadFile
from sqlalchemy import select
from websocket import WebSocket

from backend.video import schemas
from db.models import video
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.minio_client import minio_client
from confluent_kafka import Producer


logger = logging.getLogger(__name__)

def create_video_name(video_name):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hash_name = hashlib.md5(video_name.encode())

    return f"{year}/{month}/{day}/{hash(hash_name)}{hash_name.hexdigest()}"



async def save_video(video_file: UploadFile, db: AsyncSession):
    db_video = video.Video(
        path=create_video_name(video_file.filename, ),
        content_type=video_file.content_type,
        content_length=video_file.size
    )
    db.add(db_video)
    await db.flush()
    await db.commit()
    logger.debug(db_video.path)
    file_contents = await video_file.read()
    minio_client.upload_file('localbucket', db_video.path, file_contents)

    return db_video
    #
async def produce_video(file_name):
    kafka_brokers=os.getenv("KAFKA_BROKERS")
    kafka_producer = Producer({
        'bootstrap.servers': kafka_brokers,
        'broker.address.family': 'v4'  # Update with your Kafka broker address
    })
    kafka_producer.produce('video', value=file_name)
    kafka_producer.flush()


def process(url=0):
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.moveWindow('frame', 100, 100)
    timer = 100
    # Capture the video stream
    cap = cv2.VideoCapture(url)

    # Parameters for the squares
    square_size = 50
    square_color = (0, 255, 0)  # green color
    square_num = 5
    def move_square(square_coords):

        square_coords += np.random.rand(square_num, 4) * 0.01
        return square_coords

    def move_square2(square_coords):
        square_coords -= np.random.rand(square_num, 4) * 0.01
        return square_coords

    move = move_square

    square_coords = np.random.rand(square_num, 4)
    k = 0

    while True:
        # Capture a frame
        ret, frame = cap.read()
        k+=1
        if not ret:
            break

        # Draw random squares on the frame
        for coords in square_coords:
            # print(square_coords)

            x = int(coords[0] * frame.shape[1])
            y = int(coords[1] * frame.shape[0])
            w = int(coords[2] * square_size)
            h = int(coords[3] * square_size)

            cv2.rectangle(frame, (x, y), (x + w, y + h), square_color, 2)




        # Update the square coordinates
        if k == timer:
            move = move_square2
            k = 0
        # if square_coords[0][0] == 0 or square_coords[0][0] == 1:
        if square_coords.argmin() == 0:
            square_coords = np.random.rand(square_num, 4)
            move = move_square
            k = 0


        square_coords = move(square_coords)  # random offset from 0 to 0.01
        square_coords = np.clip(square_coords, 0, 1)

        # Encode the frame as a base64 string
        _, buffer = cv2.imencode('.jpg', frame)
        img_b64 = base64.b64encode(buffer)
        yield img_b64

        # Print the base64 string



        # Display the frame
        # cv2.imshow('frame', frame)
        #
        # # Pause for a short period of time
        # cv2.waitKey(1)
        #
        # # Measure the time it takes to process each frame
        # t = cv2.getTickCount()
        print(f'Frame processing time: {t / cv2.getTickFrequency():.2f} ms')

    # Close all OpenCV windows
    cv2.destroyAllWindows()








# async def generate_frames(rtsp_url: str, camera_id: str) -> bytes:
#     frame_count = 0
#     try:
#
#         video = cv2.VideoCapture(rtsp_url, apiPreference=cv2.CAP_FFMPEG)
#         while True:
#             ret, frame = video.read()
#             if not ret:
#                 break
#
#             (ret, jpeg) = cv2.imencode(".jpg", frame)
#             frame_count += 1
#             try:
#                 pass
#             except Exception as e:
#                 print(f"Ошибка: {e}")
#             if ret:
#                 yield jpeg.tobytes()
#     except Exception as e:
#         print(f"Ошибка: {e}")


async def get_rtsp_url(camera_id: str, db: AsyncSession):
    result = await db.execute(select(video.Camera.threadURL).where(video.Camera.id == camera_id))
    rtsp_url = result.scalar()
    return rtsp_url


async def add_camera(camera: schemas.CameraCreate, db: AsyncSession):
    db_camera = video.Camera(
        threadURL=camera.threadURL
    )
    await db_camera.save(db)

    return db_camera

async def add_video(video_file: UploadFile, db: AsyncSession):
    kafka_brokers = os.getenv("KAFKA_BROKERS", "kafka:9092")




    print()
    kafka_producer = Producer({
        'bootstrap.servers': kafka_brokers,
        'broker.address.family': 'v4'# Update with your Kafka broker address
    })
    file_contents = await video_file.read()
    file_name = video_file.filename
    file_type = video_file.content_type
    file_size = len(file_contents)

    path = minio_client.upload_file('localbucket', file_name, file_contents )
    db_video = video.Video(
        path=path[1],
        state="NonHandled",
        content_type=file_type,
        content_length=file_size
    )
    kafka_producer.produce('video', value=path[1].encode('utf-8'))
    kafka_producer.flush()
    return db_video

async def add_video_from_ml(video_name: str, db: AsyncSession):
    db_video = await db.get(video.Video, video_name)
    if db_video is None:
        raise ValueError(f"Видео '{video_name}' не найдено в базе данных")
    db_video.state = "SUCCESSFUL"
    await db_video.save(db)
    return db_video


async def update_video_state(camera: schemas.CameraCreate, db: AsyncSession):
    db_camera = await db.get(video.Camera, camera.id)
    db_camera.threadURL = camera.threadURL
    await db_camera.save(db)

    return db_camera

async def get_video(video_id: str, db: AsyncSession):
    query = select(video.Video).where(video.Video.id == video_id)
    result = await db.execute(query)
    result = result.mappings().first()
    print(result)

    return result



async def get_cameras(db: AsyncSession):
    cameras = await db.execute(
        select(video.Camera)
    )
    cameras = cameras.scalars().all()

    return cameras