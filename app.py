from flask import Flask, render_template, Response
from Camera.Stream import CameraStream
from flask_executor import Executor
# from Camera.HKcam import HKCam
from configs.config import *
from utils.utils import *
from create import create_action_detection_model, create_FaceRecognition, get_minio_client, create_app
from create.database import *
import cv2


# === 全局变量 ===

# 使用 HKCam

# camIP ='192.168.1.64'
# DEV_PORT = 8000
# username ='admin'
# password = 'haut2023'
# cap = HKCam(camIP,username,password)
# os.chdir(os.path.dirname(__file__))

# 使用 HKCam

# 使用本机的Cam
cap = cv2.VideoCapture("qiandao.mp4")
# 使用本机的Cam


# === 全局变量 ===

app = create_app()
executor = Executor(app)


yolo = create_action_detection_model()

# minio client
minioClient = get_minio_client()
retinaface = create_FaceRecognition(minioClient)


camera_stream = CameraStream()

        

def read_camera(cap):
    global yolo, retinaface
    # 创建一个循环，用于不断地读取摄像头的图像并调用 camera_stream.update_frame
    try:
        print("摄像头开启")
        i = 0
        while True:
            i += 1
            _, img = cap.read()

            # img = yolo.inference(img)
            if i % 25 == 0:
                img = retinaface.inference(img)
            
            _, bytes_arr = cv2.imencode('.jpg', img)

            camera_stream.update_frame(bytes_arr.tobytes())
    except Exception as e :
        print(e)
    finally:
        print("摄像头关闭")
        cap.release()


# === 全局变量 ===


@app.route("/create_table")
def create():
    create_all_tables()


@app.route("/")
def index():
    return render_template('index.html') 

@app.route('/video_feed')
def video_feed():
    global camera_stream
    frames = camera_stream.subscribe()
    def generate():
        while True:
            nonlocal frames
            frame = frames.get_frame() # queue为空会阻塞线程
            yield (b'--frame\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace;boundary=frame')



with app.test_request_context():
    executor.submit(read_camera, cap)


if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False, threaded=True)
    