import cv2
import numpy as np
import time

from numpy.lib.stride_tricks import DummyArray
import PoseModule as pm
from flask import Flask,render_template, Response,request

app = Flask(__name__)



# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1280, 720))

detector = pm.poseDetector()

nombre=""
edad=""
genero=""
video_url=""
total_buenas=0
total_malas=0
porcentaje_buenas=0
porcentaje_malas=0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return render_template('video.html')


def generar():  
    global total_buenas
    global total_malas
    global porcentaje_malas
    global porcentaje_buenas

    cap = cv2.VideoCapture(video_url)

    count = 0
    count1 = 0
    dir = 0
    dir1 = 0
    pTime = 0

    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            img = cv2.resize(img, (1280, 720))
            # img = cv2.imread("AiTrainer/test.jpg")
            img = detector.findPose(img, False)
            lmList = detector.findPosition(img, False)
            #print(lmList)
            if len(lmList) != 0:
                # Right Arm
                angle = detector.findAngle(img, 12, 14, 16)
                # # Left Arm
                # angle = detector.findAngle(img, 11, 13, 15,False)
                per = np.interp(angle, (190, 199), (0, 100))
                bar = np.interp(angle, (190, 199), (650, 100))

                #voleas malas

                per1 = np.interp(angle, (80, 189), (0, 100))
                bar1 = np.interp(angle, (80, 189), (650, 100))




            # print(angle, per)

                # Check for the dumbbell curls
                color = (255, 0, 255)
                if per == 100:
                    color = (0, 255, 0)
                    if dir == 0:

                        count += 0.5
                        dir = 1
                if per == 0:
                    color = (0, 255, 0)
                    if dir == 1:
                        count += 0.5
                        dir = 0
                # print(count)


            #conteo de las voleas malas
                color = (255, 0, 255)
                if per1 == 100:
                    color = (0, 255, 0)
                    if dir1 == 0:
                        count1 += 0.5
                        dir1 = 1
                if per1 == 0:
                    color = (0, 255, 0)
                    if dir1 == 1:
                        count1 += 0.5
                        dir1 = 0
                # print("volea","-", "Vole mala")
                # print(count,"-", count1)


                # Draw Bar
                cv2.rectangle(img, (1100, 100), (1175, 650), color, 3)
                cv2.rectangle(img, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
                cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                            color, 4)

                # Draw Curl Count

                cv2.rectangle(img, (0, 750), (400, 610), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f' Buena', (10,700 ), cv2.FONT_HERSHEY_PLAIN, 3,
                            (0, 0, 0), 3)
                cv2.putText(img, str(int(count)), (45, 670), cv2.FONT_HERSHEY_PLAIN, 5,
                            (255, 0, 0), 5)


                #cv2.putText(img, str(int(count)), (45, 670), cv2.FONT_HERSHEY_PLAIN, 15,
                            #(255, 0, 0), 25)

            # cv2.rectangle(img, (0, 60), (300, 300), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f' Mala', (250, 700), cv2.FONT_HERSHEY_PLAIN, 3,
                            (0, 0, 0), 3)
                cv2.putText(img, str(int(count1)), (300, 670), cv2.FONT_HERSHEY_PLAIN, 5,
                            (255, 0, 0), 5)


            total_buenas=int(count)
            total_malas=int(count1)

            total_voleadas=total_buenas+total_malas

            try:
                porcentaje_buenas=total_buenas/total_voleadas
                porcentaje_malas=total_malas/total_voleadas
            except ZeroDivisionError:
                porcentaje_buenas=0
                porcentaje_malas=0


            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            #cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
                        #(255, 0, 0), 5)

            # cv2.imshow("Image", img)
            # cv2.waitKey(1)
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()



            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    return Response(generar(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/upload', methods = ['GET','POST'])
def upload_file():
   global nombre
   global edad
   global genero
   global video_url


   if request.method == 'POST':
        nombre=request.form['nombre']
        edad=request.form['edad']
        genero=request.form['genero']

        # print(nombre,edad,genero)

        f = request.files['file']
        f.save('videos/'+f.filename)
        # print(f.filename)
        video_url='videos/'+f.filename
        duracion=duracion_video(video_url)
        
        return render_template('video.html',duracion=duracion)
      
@app.route('/resumen')
def resumen():
    return render_template("resumen.html",nombre=nombre,edad=edad,genero=genero,total_buenas=total_buenas,total_malas=total_malas,porcentaje_buenas=round(porcentaje_buenas*100,2),porcentaje_malas=round(porcentaje_malas*100,2))

def duracion_video(video):
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    
    # print('duration (S) = ' + str(duration))

    return(duration)

if __name__ == "__main__":
    app.run(debug=True)