import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Lapbook AR Agent Backend")

# Permitir conexiones desde el navegador del móvil (WebAR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "device": "Xiaomi Local Server"}

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📡 Cliente WebAR conectado mediante WebSocket.")
    
    try:
        while True:
            # Recibir datos del frontend (pueden ser binarios [audio] o texto [JSON/Imágenes])
            data = await websocket.receive()
            
            if "bytes" in data:
                # Aquí se reciben los fragmentos de audio en streaming del micrófono
                audio_chunk = data["bytes"]
                # TODO: Alimentar el buffer de Whisper STT
                pass
                
            elif "text" in data:
                # Aquí se recibe la señal de fin de frase con la captura de la maqueta
                payload = json.loads(data["text"])
                
                if payload.get("event") == "PROCESS_SCENE":
                    print("🤫 Silencio detectado. Procesando escena con IA...")
                    image_base64 = payload.get("image")
                    
                    # --- SIMULACIÓN DEL PIPELINE DE IA (Esqueleto) ---
                    # 1. Transcribir audio final acumulado con Whisper -> texto_usuario
                    # 2. Pasar imagen a Laya/Clef para decisión rápida de coordenadas
                    # 3. Pasar imagen + texto_usuario a Qwen2.5-VL para respuesta pedagógica
                    # 4. Sintetizar respuesta con Kokoro TTS -> audio_output
                    
                    # Respuesta simulada en formato estándar JSON
                    response_payload = {
                        "voz_tutor": "He detectado la cocina de tu maqueta. Recuerda que el extintor debe estar visible.",
                        "render_ui": {
                            "hab": "cocina",
                            "status": "ok",
                            "sfx": "success"
                        }
                    }
                    
                    await websocket.send_text(json.dumps(response_payload))
                    
    except WebSocketDisconnect:
        print("🔌 Cliente WebAR desconectado.")