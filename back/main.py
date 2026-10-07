import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Importació de tots els serveis de la nostra arquitectura agèntica
from app.services.stt_whisper import WhisperSTTService
from app.services.ai_decision import AIDecisionService
from app.services.ai_conversational import AIConversationalService
from app.services.tts_kokoro import KokoroTTSService

app = FastAPI(title="Lapbook AR Agent Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciació dels serveis a la memòria RAM del Xiaomi
whisper_service = WhisperSTTService()
decision_service = AIDecisionService()
qwen_service = AIConversationalService(ollama_url="http://localhost:11434")
kokoro_service = KokoroTTSService()

# Carregar els models ONNX locals en arrancar el servidor
decision_service.load_model()
kokoro_service.load_model()

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📡 Connexió WebAR en directe establerta.")
    whisper_service.clear_buffer()
    
    try:
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                # El VAD del mòbil detecta veu: acumulem l'àudio
                whisper_service.append_chunk(data["bytes"])
                
            elif "text" in data:
                payload = json.loads(data["text"])
                
                if payload.get("event") == "PROCESS_SCENE":
                    print("🤫 Silenci detectat. Executant pipeline multicapa...")
                    image_base64 = payload.get("image")
                    
                    # ─── CAPA 1: MODEL DE DECISIÓ ULTRA-RÀPID (ONNX) ───
                    # S'executa en ~40ms per donar resposta visual immediata
                    fast_decision = await decision_service.classify_frame(image_base64)
                    
                    # Enviem immediatament les coordenades 3D a A-Frame abans de generar el text
                    await websocket.send_text(json.dumps({
                        "type": "FAST_TRACK_UI",
                        "data": fast_decision
                    }))
                    
                    # ─── CAPA 2: RECONEIXEMENT DE VEU (Whisper STT) ───
                    user_text = await whisper_service.transcribe()
                    print(f"🗣️ Transcripció: '{user_text}'")
                    if not user_text:
                        user_text = "Analitza aquesta habitació."
                    
                    # ─── CAPA 3: RAONAMENT MULTIMODAL (Qwen2.5-VL) ───
                    ai_response = await qwen_service.analyze_scene(image_base64, user_text)
                    print(f"🤖 Resposta del VLM: {ai_response}")
                    
                    # ─── CAPA 4: SÍNTESI DE VEU EN STREAMING (Kokoro TTS) ───
                    texto_a_leer = ai_response.get("voz_tutor", "")
                    audio_raw_bytes = await kokoro_service.generate_speech(texto_a_leer)
                    
                    # ─── CAPA 5: ENVIAMENT DE RESPOSTES COMBINADES ───
                    # Primer enviem les dades estructurades finals de la UI
                    await websocket.send_text(json.dumps({
                        "type": "FINAL_UI",
                        "data": ai_response
                    }))
                    
                    # Seguidament enviem els bytes de l'àudio generat per Kokoro
                    if audio_raw_bytes:
                        await websocket.send_bytes(audio_raw_bytes)
                    
    except WebSocketDisconnect:
        print("🔌 Client WebAR desconnectat de la sessió.")