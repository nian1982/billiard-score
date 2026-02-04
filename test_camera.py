#!/usr/bin/env python3
"""
Script para detectar y probar cámaras disponibles
"""
import cv2
import sys

print("=" * 60)
print("🔍 Detectando cámaras disponibles...")
print("=" * 60)

for i in range(5):
    print(f"\n📹 Probando /dev/video{i}...")
    try:
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            # Intentar leer un frame
            ret, frame = cap.read()
            
            if ret and frame is not None:
                height, width = frame.shape[:2]
                
                # Obtener propiedades
                fps = cap.get(cv2.CAP_PROP_FPS)
                backend = cap.getBackendName()
                
                print(f"  ✅ FUNCIONA!")
                print(f"  📐 Resolución: {width}x{height}")
                print(f"  🎬 FPS: {fps}")
                print(f"  🔧 Backend: {backend}")
                print(f"  ➡️  Usar: cv2.VideoCapture({i})")
            else:
                print(f"  ⚠️  Se abrió pero no puede capturar frames")
            
            cap.release()
        else:
            print(f"  ❌ No se puede abrir")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("💡 Recomendación:")
print("=" * 60)
print("Usa el índice que mostró '✅ FUNCIONA!' en billar_app.py")
print("=" * 60)
