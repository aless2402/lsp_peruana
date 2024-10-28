import cv2 as cv
import mediapipe as mp
import numpy as np
import threading
import speech_recognition as sr
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Configuración de MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Variable global para el texto de los subtítulos
subtitle_text = ""

# Función para el reconocimiento de voz
def recognize_voice():
    global subtitle_text
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        while True:
            audio = recognizer.listen(source)

            try:
                result = recognizer.recognize_google(audio, language='es-PE')
                subtitle_text = result
            except sr.UnknownValueError:
                subtitle_text = "No se entendió"
            except sr.RequestError:
                subtitle_text = "Error de solicitud"

# Inicia el hilo para reconocimiento de voz
voice_thread = threading.Thread(target=recognize_voice)
voice_thread.daemon = True
voice_thread.start()

def generate_frames():
    camera = cv.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break

        # Procesar la imagen
        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Dibujar las manos detectadas
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Codificar la imagen y generar el frame
        _, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/subtitles')
def subtitles():
    return jsonify({'subtitle': subtitle_text})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
