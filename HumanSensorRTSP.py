#Built with Python3.10 and OpenCV4.6.0
import cv2 as cv
from paho.mqtt import client as mqtt_client
import time
import yaml
import os

curPath = os.path.dirname(os.path.realpath(__file__))
yamlPath = os.path.join(curPath, "config.yaml")

with open(yamlPath, 'r', encoding='utf-8') as f:
    preferences = yaml.load(f.read(), Loader=yaml.FullLoader)

url = preferences['url']
broker = preferences['broker']
port =  preferences['port']
topic = preferences['topic']
#client_id = f'python-mqtt-{random.randint(0, 1000)}'

print('CV2 Version is ' + cv.__version__ )
print('Starting...')

'''以图片保存含有人体的帧
def imgSave(img):
    now = datetime.now()  # 获得当前时间
    timestr = now.strftime("/Users/YourUserName/Desktop/test/%Y_%m_%d_%H_%M_%S.jpeg")
    cv2.imwrite(timestr, img )
    print('Saved successfully')
'''

last_capture_time_stamp = time.time()

def discern(img):
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    cap = cv.CascadeClassifier(preferences['module'])
    faceRects = cap.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=3, minSize=(50, 50))
    if len(faceRects):
        for faceRect in faceRects:
            x, y, w, h = faceRect
            cv.rectangle(img, (x, y), (x + h, y + w), (0, 255, 0), 2)
        #imgSave(img)
        global human_state
        human_state = True
        global show_capture_time
        show_capture_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    else:
        human_state = False
    
    cv.imshow("Image", img)

def connect_mqtt():#连接mqtt
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()#client_id
    client.username_pw_set(preferences['account'], preferences['password'])
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):#发布mqtt
    if human_state == True:
        #msg = f"human {msg_count}"
        msg = f'Human exist at '+ show_capture_time
        result = client.publish(topic, msg)
        #result: [0,1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

def run():
    client = connect_mqtt()
    #client.loop_start()
    publish(client)
    #client.on_disconnect
    
cap = cv.VideoCapture(preferences['from_url_or_cam'])

while True:
    ret, img = cap.read()#逐帧显示
    discern(img)
    time_interval = time.time() - last_capture_time_stamp
    if time_interval >= 1:
        run()
        last_capture_time_stamp = time.time()
        #cv2.imshow("Image", img)#保存含有人体的帧

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()  # 释放摄像头
cv.destroyAllWindows()  # 释放窗口资源