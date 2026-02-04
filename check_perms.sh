#!/bin/bash

echo "🔍 Verificando permisos de cámara..."
echo ""

# Verificar si está en el grupo video
if groups | grep -q video; then
    echo "✅ Tienes acceso al grupo 'video'"
else
    echo "❌ NO estás en el grupo 'video'"
    echo ""
    echo "Solución rápida:"
    echo "  sudo usermod -a -G video $USER"
    echo "  Luego cierra sesión y vuelve a entrar (o reinicia)"
    echo ""
fi

# Mostrar permisos de los dispositivos
echo "Permisos actuales:"
ls -l /dev/video* 2>/dev/null

echo ""
echo "Tu usuario: $(whoami)"
echo "Tus grupos: $(groups)"
