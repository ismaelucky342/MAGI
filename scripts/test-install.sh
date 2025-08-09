#!/bin/bash

# Test script para verificar la instalación de dependencias

echo "🧪 Probando instalación de dependencias..."

# Verificar estructura del proyecto
echo "Verificando estructura del proyecto..."
if [ -f "package.json" ]; then
    echo "✓ package.json encontrado"
else
    echo "✗ package.json NO encontrado"
    exit 1
fi

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "✓ frontend/package.json encontrado"
else
    echo "✗ frontend/package.json NO encontrado"
fi

if [ -d "backend" ] && [ -f "backend/package.json" ]; then
    echo "✓ backend/package.json encontrado"
else
    echo "✗ backend/package.json NO encontrado"
fi

# Probar instalación root
echo ""
echo "Probando instalación de dependencias root..."
if npm install --silent; then
    echo "✓ Dependencias root instaladas correctamente"
else
    echo "✗ Error instalando dependencias root"
    exit 1
fi

echo ""
echo "🎉 Prueba de instalación completada exitosamente!"
