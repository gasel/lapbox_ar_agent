# Lapbook AR Agent 🏠🤖

Proyecto de formación interactivo que combina un Lapbook físico desplegable en 3D con un asistente de Realidad Aumentada (WebAR) local, controlado por voz (manos libres) y potenciado por Modelos de Lenguaje Multimodales (VLM).

## 🏛️ Arquitectura del Sistema
- **Frontend:** A-Frame + AR.js para el renderizado 3D/RA. `silero-vad` para la detección de actividad de voz en tiempo real.
- **Backend:** FastAPI expuesto mediante WebSockets para streaming de audio de baja latencia.
- **Modelos de IA (On-Device en Termux):** Whisper (STT) + Laya/Qwen2.5-VL (Decisión/VLM) + Kokoro (TTS).

## 🚀 Despliegue Rápido en Termux (Xiaomi)
1. Instalar la APK de Termux (v0.119.0-beta.3 de GitHub).
2. Ejecutar `pkg update && pkg upgrade -y` y `termux-setup-storage`.
3. Instalar dependencias del sistema: `pkg install git python nodejs ndk-sysroot clang make libjpeg-turbo fftw libsndfile -y`.
4. Clonar el repositorio y configurar el entorno:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd lapbook-ar-agent/backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```