"""
Sistema de Streaming de Billar - Arquitectura HLS (DVR Real)
Optimizado para baja latencia (Stable)
"""

import os
import signal
import subprocess
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para HLS.js

# Configuración
HLS_DIR = os.path.join(os.getcwd(), 'hls')
os.makedirs(HLS_DIR, exist_ok=True)

# Estado Global
class GlobalState:
    def __init__(self):
        self.recording = False
        self.start_time = 0
        # Scores dinámicos (se inicializan desde frontend)
        self.scores = {}
        self.history = []
        self.ffmpeg_process = None

state = GlobalState()

class FFmpegController:
    @staticmethod
    def start_recording():
        if state.recording:
            return False

        # Limpiar
        for f in os.listdir(HLS_DIR):
            if f.endswith('.ts') or f.endswith('.m3u8'):
                try:
                    os.remove(os.path.join(HLS_DIR, f))
                except Exception as e:
                    print(f"Error limpiando archivo {f}: {e}")

        state.start_time = time.time()
        state.history = [{
            'timestamp': state.start_time,
            'scores': state.scores.copy()
        }]

        # CONFIGURACIÓN BALANCEADA: Latencia ~4s + DVR Ilimitado
        # -hls_time 2: Segmentos de 2s (equilibrio latencia/estabilidad)
        # -g 30: GOP de 1s
        # -hls_list_size 0: DVR ILIMITADO (puedes retroceder todo)
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'v4l2',
            '-framerate', '30',
            '-video_size', '1280x720',
            '-i', '/dev/video0',
            '-c:v', 'libx264',
            '-preset', 'veryfast',      # Balance velocidad/calidad
            '-tune', 'zerolatency',
            '-pix_fmt', 'yuv420p',      # Compatibilidad web
            '-g', '30',                 # GOP 1s
            '-sc_threshold', '0',
            '-f', 'hls',
            '-hls_time', '2',           # 2 segundos por segmento
            '-hls_list_size', '0',      # 0 = ILIMITADO (DVR completo)
            '-hls_flags', 'delete_segments+append_list',
            '-hls_segment_filename', os.path.join(HLS_DIR, 'segment_%03d.ts'),
            os.path.join(HLS_DIR, 'stream.m3u8')
        ]
        
        try:
            print(f"🚀 Iniciando FFmpeg Stable: {' '.join(cmd)}")
            # Redirigir log a archivo para debug si falla
            log_file = open(os.path.join(os.getcwd(), 'ffmpeg.log'), 'w')
            state.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
            state.recording = True
            return True
        except Exception as e:
            print(f"❌ Error iniciando FFmpeg: {e}")
            return False

    @staticmethod
    def stop_recording():
        if not state.recording:
            return False
            
        if state.ffmpeg_process:
            print("🛑 Deteniendo FFmpeg...")
            state.ffmpeg_process.terminate()
            try:
                state.ffmpeg_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                state.ffmpeg_process.kill()
            state.ffmpeg_process = None
            
        state.recording = False
        return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test_hls():
    return render_template('test_hls.html')

@app.route('/hls/<path:filename>')
def serve_hls(filename):
    response = make_response(send_from_directory(HLS_DIR, filename))
    
    # Headers explícitos
    if filename.endswith('.m3u8'):
        response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    elif filename.endswith('.ts'):
        response.headers['Content-Type'] = 'video/mp2t'
        response.headers['Cache-Control'] = 'max-age=60'
        
    return response

@app.route('/api/status')
def get_status():
    return jsonify({
        'recording': state.recording,
        'start_time': state.start_time,
        'current_scores': state.scores
    })

@app.route('/api/history')
def get_history():
    return jsonify({
        'start_time': state.start_time,
        'events': state.history
    })

@app.route('/start_recording', methods=['POST'])
def start_recording_route():
    success = FFmpegController.start_recording()
    if success:
        return jsonify({'status': 'started', 'start_time': state.start_time})
    return jsonify({'status': 'error', 'message': 'Could not start recording'}), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording_route():
    FFmpegController.stop_recording()
    return jsonify({'status': 'stopped'})

@app.route('/update_score', methods=['POST'])
def update_score():
    data = request.json
    player = data.get('player')
    action = data.get('action')
    
    # Auto-inicializar jugador si no existe
    if player not in state.scores:
        state.scores[player] = 0
    
    original_score = state.scores[player]
    if action == 'add':
        state.scores[player] += 1
    elif action == 'subtract' and state.scores[player] > 0:
        state.scores[player] -= 1
        
    if state.scores[player] != original_score:
        current_time = time.time()
        state.history.append({
            'timestamp': current_time,
            'scores': state.scores.copy()
        })
        
    return jsonify({'scores': state.scores})

@app.route('/reset_scores', methods=['POST'])
def reset_scores():
    for p in state.scores:
        state.scores[p] = 0
    state.history.append({
        'timestamp': time.time(),
        'scores': state.scores.copy()
    })
    return jsonify({'scores': state.scores})

if __name__ == '__main__':
    def signal_handler(sig, frame):
        FFmpegController.stop_recording()
        exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Servidor iniciado en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
