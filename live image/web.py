from flask import Flask, Response, render_template, request, redirect
import cv2
import time
import numpy as np

app = Flask(__name__)


# 應用程式路由定義
app.config['LINK'] = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    try:
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except:
        return "無影像"

@app.route('/io',methods=["GET","POST"])
def io():
    if request.method == "POST":
        tolink = request.form["content"]
        app.config['LINK'] = tolink
        return redirect('/')
    else:
        return redirect('/')

# 影像串流生成器
def generate_frames():
    while True:
        link = app.config['LINK']
        if link is None:
            time.sleep(1)
            continue
        
        cap = cv2.VideoCapture(link)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("沒有讀取到影像，重新啟動 VideoCapture...")
                cap.release()
                time.sleep(0.1)
                cap = cv2.VideoCapture(link)
                break
            
            # 將影像編碼成 JPEG 格式，並且以 multipart/x-mixed-replace 格式傳輸
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # 控制播放速度
            key = cv2.waitKey(60) & 0xFF
            if key == ord('q'):
                break

    # 釋放 VideoCapture 物件，關閉視窗
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run('0.0.0.0', port=7010, debug=True)
