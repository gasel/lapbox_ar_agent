const socket = new WebSocket('ws://127.0.0.1:8000/stream');
const uiStatus = document.getElementById('ui-status');
const objetoVirtual = document.getElementById('objeto-virtual');

socket.onopen = () => {
    console.log("🚀 Conectado al backend de Termux.");
    inicializarOidoInteligente();
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("🤖 Respuesta de la IA:", data);
    
    // Actualizar UI y escena 3D según la decisión del VLM
    uiStatus.innerText = data.voz_tutor;
    
    if (data.render_ui.status === "ok") {
        objetoVirtual.setAttribute('visible', 'true');
        objetoVirtual.setAttribute('material', 'color', 'green');
    }
};

/*async function inicializarOidoInteligente() {
    try {
        const myVad = await vad.create({
            onSpeechStart: () => {
                uiStatus.innerText = "🎙️ Procesando tu voz en tiempo real...";
                uiStatus.style.background = "rgba(231, 76, 60, 0.8)";
            },
            onFrame: (audioFrame) => {
                // Enviar fragmentos binarios PCM al WebSocket si el canal está abierto
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(audioFrame.buffer);
                }
            },
            onSpeechEnd: () => {
                uiStatus.innerText = "⏳ Analizando maqueta...";
                uiStatus.style.background = "rgba(46, 204, 113, 0.8)";
                
                // Capturar el canvas de la cámara de AR.js
                const scene = document.querySelector('a-scene');
                const canvas = scene.components.screenshot ? scene.components.screenshot.getCanvas('perspective') : null;
                const imageBase64 = canvas ? canvas.toDataURL('image/jpeg') : "";

                // Enviar trigger final con la imagen al backend
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({
                        event: "PROCESS_SCENE",
                        image: imageBase64
                    }));
                }
            }
        });
        
        myVad.start();
        console.log("👂 Detector de actividad de voz (VAD) activo y manos libres.");
    } catch (err) {
        console.error("Error al acceder al micrófono o inicializar VAD:", err);
        uiStatus.innerText = "⚠️ Error de permisos de micrófono";
    }
}*/

async function inicializarOidoInteligente() {
    try {
        // Inicializar el VAD usando el bundle de la ventana global
        const myVad = await vad.MicVAD.new({
            onSpeechStart: () => {
                uiStatus.innerText = "🎙️ Procesando tu voz en tiempo real...";
                uiStatus.style.background = "rgba(231, 76, 60, 0.8)";
            },
            onFrame: (audioFrame) => {
                // audioFrame ya viene normalizado a Float32 de 16kHz gracias a Silero
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(audioFrame.buffer);
                }
            },
            onSpeechEnd: () => {
                uiStatus.innerText = "⏳ Analizando maqueta...";
                uiStatus.style.background = "rgba(46, 204, 113, 0.8)";
                
                const scene = document.querySelector('a-scene');
                const canvas = scene.components.screenshot ? scene.components.screenshot.getCanvas('perspective') : null;
                const imageBase64 = canvas ? canvas.toDataURL('image/jpeg') : "";

                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({
                        event: "PROCESS_SCENE",
                        image: imageBase64
                    }));
                }
            }
        });
        
        myVad.start();
        console.log("👂 Detector de actividad de voz (VAD) inicializado correctamente.");
    } catch (err) {
        console.error("Error al inicializar VAD:", err);
        uiStatus.innerText = "⚠️ Error de micrófono o inicialización WASM";
    }
}
