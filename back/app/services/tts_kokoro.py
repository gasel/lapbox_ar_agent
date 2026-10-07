import os
import json
import numpy as np
import onnxruntime as ort

class KokoroTTSService:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        # Rutas de los assets oficiales de Kokoro que guardaremos en el móvil
        self.model_path = os.path.join(models_dir, "kokoro-v0.1.onnx")
        self.voices_path = os.path.join(models_dir, "voices.json")
        self.session = None
        self.voices_data = {}
        
        print("🎙️ Servicio Kokoro TTS (ONNX) inicializado en estructura.")

    def load_model(self):
        """Carga los pesos de Kokoro en memoria si existen en el dispositivo."""
        if os.path.exists(self.model_path) and os.path.exists(self.voices_path):
            try:
                # Inicializar sesión ONNX optimizada para arquitecturas ARM64
                self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
                with open(self.voices_path, 'r', encoding='utf-8') as f:
                    self.voices_data = json.load(f)
                print("✅ Modelo Kokoro y biblioteca de voces cargados en RAM correctamente.")
            except Exception as e:
                print(f"❌ Error al instanciar el runtime de Kokoro ONNX: {e}")
        else:
            print("⚠️ Advertencia: No se encontraron los archivos de Kokoro en backend/models/. Se ejecutará en modo simulación.")

    async def generate_speech(self, text: str, voice_name: str = "es_male") -> bytes:
        """
        Sintetiza texto en audio PCM crudo (Raw Audio Float32 a 24kHz o 16kHz).
        Devuelve los bytes listos para enviarse por el WebSocket.
        """
        if not self.session:
            # --- MODO SIMULACIÓN (Si aún no has descargado los pesos en el PC) ---
            print(f"🤫 [Simulación TTS] Generando audio para: '{text}'")
            # Devolvemos un buffer de audio vacío simulado de 1 segundo (ceros)
            sample_rate = 16000
            silence = np.zeros(sample_rate, dtype=np.float32)
            return silence.tobytes()

        try:
            # En un entorno ONNX real, aquí se tokeniza el texto, se extrae el vector 
            # de la voz desde 'voices.json' y se ejecuta self.session.run()
            # Retorna el array lineal de audio que pasamos a bytes crudos
            pass
        except Exception as e:
            print(f"❌ Fallo en la inferencia de Kokoro: {e}")
            return b""