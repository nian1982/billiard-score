# Tecnologias
* Python 3.11.x
* paru -S python311
* python3.11 -m venv .venv

# 🎱 Sistema de Control de Billar - Streaming Optimizado

Sistema de streaming en vivo para control de mesas de billar con reproducción de video y gestión de puntos.

## ✨ Características

### Video
- ✅ Streaming en vivo desde cámara del laptop
- ✅ **Buffer circular en memoria** (solo últimos 5 minutos en RAM)
- ✅ Retroceder a cualquier punto sin perder la grabación
- ✅ Botón "Volver a EN VIVO"
- ✅ Barra de progreso interactiva
- ✅ Retroceder 10 segundos

### Puntos
- ✅ **8 mesas de billar** con contadores individuales
- ✅ Botones **+ y -** separados para cada mesa
- ✅ **Marcadores visibles** en la parte superior
- ✅ Los puntos se guardan junto con cada frame del video
- ✅ Al retroceder, los puntos vuelven al estado de ese momento
- ✅ Botón para resetear todos los puntos

## 🚀 Instalación

### 1. Instalar Python
```bash
# En Windows: Descargar de python.org (Python 3.8 o superior)
# En Linux/Mac:
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar aplicación
```bash
python billar_app.py
```

### 4. Abrir navegador
```
http://localhost:5000
```

## 📊 Ventajas sobre JavaScript/WebRTC

| Aspecto | Python + OpenCV | JavaScript |
|---------|-----------------|------------|
| **Memoria** | 🟢 Muy eficiente (buffer circular) | 🟡 Consume más |
| **CPU** | 🟢 Bajo consumo | 🟡 Medio |
| **Control** | 🟢 Precisión total | 🟡 Limitado por API |
| **Compatibilidad** | 🟢 Funciona en cualquier navegador | 🟡 Depende del navegador |
| **Calidad** | 🟢 Configurable | 🟡 Limitada |

## 💾 Optimización de Memoria

### Buffer Circular
- Solo guarda los **últimos 5 minutos** en RAM
- Los frames antiguos se eliminan automáticamente
- Memoria **predecible y controlada**

### Compresión
- Frames comprimidos en JPEG (85% calidad)
- Resolución ajustable (por defecto 1280x720)
- FPS configurable (por defecto 30)

### Cálculo de Memoria Aproximada
```
Memoria = Duración × FPS × Tamaño_Frame
Ejemplo (5 min):
- 5 min × 60 seg = 300 segundos
- 300 seg × 30 FPS = 9,000 frames
- 9,000 frames × ~50 KB/frame = ~450 MB
```

## ⚙️ Configuración (billar_app.py)

```python
# Línea 15-17
BUFFER_SECONDS = 300  # 5 minutos (ajustable)
FPS = 30              # Frames por segundo
MAX_FRAMES = BUFFER_SECONDS * FPS
```

### Ajustar para equipos con menos RAM:
```python
BUFFER_SECONDS = 180  # 3 minutos → ~270 MB
FPS = 20              # 20 FPS → reduce memoria 33%
```

### Para equipos con más RAM:
```python
BUFFER_SECONDS = 600  # 10 minutos → ~900 MB
FPS = 30
```

## 🎮 Uso

### Iniciar Grabación
1. Click en "▶ Iniciar Grabación"
2. El sistema comienza a grabar y muestra "EN VIVO"

### Controlar Puntos
- Click **-** para disminuir puntos de una mesa
- Click **+** para aumentar puntos de una mesa
- Los cambios se ven inmediatamente en el marcador superior

### Reproducción
1. **⏪ -10s**: Retrocede 10 segundos
2. **Barra de progreso**: Click para saltar a cualquier momento
3. **🔴 Ir a EN VIVO**: Volver a la transmisión en vivo
4. Los puntos cambian automáticamente al momento del video

### Validaciones
- Retrocede a cualquier momento de la partida
- Verifica jugadas
- Los puntos muestran el estado exacto de ese momento
- La grabación continúa en segundo plano

## 📁 Estructura de Archivos

```
billar-streaming/
├── billar_app.py          # Aplicación principal (Flask + OpenCV)
├── templates/
│   └── index.html         # Interfaz web
├── requirements.txt       # Dependencias
└── README.md             # Este archivo
```

## 🔧 Solución de Problemas

### La cámara no se detecta
```python
# En billar_app.py, línea 41, cambiar:
self.video = cv2.VideoCapture(0)  # Probar con 1, 2, etc.
```

### Consume mucha memoria
```python
# Reducir buffer y FPS:
BUFFER_SECONDS = 120  # 2 minutos
FPS = 15
```

### Video lento o con lag
```python
# Reducir resolución (línea 43-44):
self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
```

## 🎯 Comparación con Alternativas

### Python + OpenCV (Esta solución) ✅
- **Pros**: Memoria eficiente, control total, rápido
- **Contras**: Requiere instalar Python

### JavaScript + MediaRecorder
- **Pros**: No requiere instalación
- **Contras**: Consume más memoria, menos control

### Servidor de Streaming (RTMP/HLS)
- **Pros**: Escalable, múltiples usuarios
- **Contras**: Complejo, requiere servidor, costoso

## 📝 Notas Técnicas

### Sincronización Puntos-Video
Cada frame guarda:
```python
{
    'frame': bytes,           # Frame comprimido
    'timestamp': float,       # Momento exacto
    'scores': dict           # Estado de puntos
}
```

Al retroceder, se restaura el estado completo de ese momento.

## 🆘 Soporte

Para problemas o mejoras, verifica:
1. Python 3.8+ instalado
2. Permisos de cámara otorgados
3. Puerto 5000 disponible

## 📄 Licencia

Libre para uso personal y comercial.

---

creado para optimizar el control de mesas de billar con mínimo consumo de recursos.

# Con FFmpeg
ffmpeg -f v4l2 -framerate 10 -video_size 1280x720 -i /dev/video0 \
-c:v libx264 \
-preset veryfast \
-tune zerolatency \
-pix_fmt yuv420p \
-g 10 -keyint_min 10 -sc_threshold 0 \
-f hls \
-hls_time 1 \
-hls_list_size 240 \
-hls_flags delete_segments+append_list \
hls/stream.m3u8


Desde ~/Downloads/files:

python -m http.server 8080


Abre:

http://localhost:8080/index.html
