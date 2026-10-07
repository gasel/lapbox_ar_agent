# backend/app/services/stt_whisper.py
import numpy as np

class WhisperSTTService:
    def __init__(self):
        self.audio_buffer = []
        print("🎙️ Servicio Whisper STT (Estructura) inicializado.")

    def clear_buffer(self):
        """Limpia el buffer acumulado tras terminar una frase."""
        self.audio_buffer = []

    def append_chunk(self, byte_data: bytes):
        """Acumula los fragmentos binarios PCM Float32 recibidos por el WebSocket."""
        # Convertir los bytes crudos a un array de floats de numpy (PCM de 16kHz)
        chunk = np.frombuffer(byte_data, dtype=np.float32)
        self.audio_buffer.append(chunk)

    async def transcribe(self) -> str:
        """
        Concatena el buffer y realiza la inferencia.
        En producción real, aquí pasamos el array a onnxruntime con los pesos de Whisper.
        """
        if not self.audio_buffer:
            return ""

        # Concatena todos los fragmentos musicales en un único flujo de audio
        full_audio = np.concatenate(self.audio_buffer)
        
        # --- SIMULACIÓN DE SEGURIDAD (Esqueleto funcional) ---
        print(f"📊 Procesando {len(full_audio)} muestras de audio en Whisper...")
        
        # Simulamos una transcripción genérica para el esqueleto inicial
        # En el siguiente paso acoplaremos los pesos .onnx
        self.clear_buffer()
        return "¿Está bien puesto el extintor aquí en la cocina?"