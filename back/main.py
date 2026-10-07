import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Importamos los servicios del subproyecto
from app.services.stt_whisper import WhisperSTTService
from app.services.ai_conversational import AIConversationalService

app = FastAPI(title="Lapbook AR Agent Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciamos los servicios globales del backend
whisper_service = WhisperSTTService()
qwen_service = AIConversationalService(ollama_url="http://localhost:11434")

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📡 Conexión WebAR establecida vía WebSocket.")
    
    # Asegurar que el buffer de voz empiece limpio para este alumno
    whisper_service.clear_buffer()
    
    try:
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                # El VAD está detectando habla: acumulamos los trozos de audio Float32
                whisper_service.append_chunk(data["bytes"])
                
            elif "text" in data:
                payload = json.loads(data["text"])
                
                if payload.get("event") == "PROCESS_SCENE":
                    print("🤫 Fin de frase detectado. Iniciando pipeline de inferencia...")
                    image_base64 = payload.get("image")
                    
                    # 1. Ejecutar el modelo STT para extraer el texto del audio acumulado
                    user_text = await whisper_service.transcribe()
                    print(f"🗣️ Transcripción Whisper: '{user_text}'")
                    
                    if not user_text:
                        user_text = "Analiza esta habitación." # Fallback si fue un ruido aleatorio
                    
                    # 2. TODO: Aquí intercalaremos el Modelo de Decisión rápido (ai_decision)
                    
                    # 3. Enviar la imagen de AR.js y el texto de Whisper a Qwen2.5-VL local
                    ai_response = await qwen_service.analyze_scene(image_base64, user_text)
                    print(f"🤖 Respuesta estructurada del VLM: {ai_response}")
                    
                    # 4. TODO: Pasar el campo ai_response['voz_tutor'] por Kokoro TTS
                    
                    # Enviamos el JSON de vuelta al navegador para actualizar A-Frame de inmediato
                    await websocket.send_text(json.dumps(ai_response))
                    
    except WebSocketDisconnect:
        print("🔌 Cliente WebAR desconectado de la sesión.")