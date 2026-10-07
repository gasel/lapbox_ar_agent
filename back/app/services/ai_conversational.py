# backend/app/services/ai_conversational.py
import requests
import json

class AIConversationalService:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.api_url = f"{ollama_url}/api/generate"
        self.model_name = "qwen2.5vl:3b"
        print(f"👁️ Servicio Qwen2.5-VL vinculado a Ollama en: {ollama_url}")

    async def analyze_scene(self, image_b64: str, user_text: str) -> dict:
        """Envía el par Imagen + Texto a la API local de Ollama."""
        
        # Limpiar el prefijo de Data URL de HTML5 si existe (data:image/jpeg;base64,...)
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        # Estructuramos el prompt del sistema integrado siguiendo estándares de desarrollo
        system_instructions = (
            "Eres el tutor interactivo del lapbook. Analiza la imagen de la maqueta y la pregunta. "
            "Responde estrictamente en formato JSON con dos campos: 'voz_tutor' (texto corto para leer) "
            "y 'render_ui' (objeto con campos 'hab': 'cocina', 'status': 'ok' o 'peligro', 'sfx': 'success' o 'fire')."
        )

        prompt_final = f"{system_instructions}\n\nAlumno pregunta: {user_text}"

        # Payload compatible con la API multimodal de Ollama
        payload = {
            "model": self.model_name,
            "prompt": prompt_final,
            "images": [image_b64],
            "stream": False,
            "format": "json" # Forzamos a Ollama a estructurar la salida en JSON válido
        }

        try:
            # Petición local de baja latencia
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                # La respuesta de texto viene en formato string JSON debido al constraint 'format'
                ai_response_text = result.get("response", "{}")
                return json.loads(ai_response_text)
            else:
                print(f"❌ Error en Ollama API: Código {response.status_code}")
                return self._get_fallback_response()
                
        except Exception as e:
            print(f"⚠️ Fallo de conexión con el demonio de Ollama: {e}")
            return self._get_fallback_response()

    def _get_fallback_response(self) -> dict:
        """Respuesta de respaldo en caso de desconexión del modelo."""
        return {
            "voz_tutor": "Disculpa, estoy experimentando un retraso al analizar tu maqueta de papel.",
            "render_ui": {"hab": "cocina", "status": "info", "sfx": "none"}
        }