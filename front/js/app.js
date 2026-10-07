const socket = new WebSocket('ws://127.0.0.1:8000/stream');
const uiStatus = document.getElementById('ui-status');
const objetoVirtual = document.getElementById('objeto-virtual');

// Inicialitzar el context d'àudio global del navegador per reproduir binaris cruds
const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });

socket.onopen = () => {
    console.log("🚀 Connectat al backend multimotiu de Termux.");
    inicializarOidoInteligente();
};

socket.onmessage = async (event) => {
    // 1. GESTIÓ DE DADES BINÀRIES (Àudio de Kokoro)
    if (event.data instanceof Blob) {
        console.log("🎙️ Rebent buffer d'àudio de Kokoro...");
        const arrayBuffer = await event.data.arrayBuffer();
        reproducirAudioCrudo(arrayBuffer);
        return;
    }

    // 2. GESTIÓ DE TEXT / JSON (Esdeveniments de la IA)
    const response = JSON.parse(event.data);
    
    if (response.type === "FAST_TRACK_UI") {
        // Resposta instantània en 40ms del model de decisió
        console.log("⚡ Resposta ràpida (Decisió):", response.data);
        if (response.data.hab_detectada === "cocina") {
            // Fem reaccionar la interfície 3D immediatament
            uiStatus.innerText = "📍 Habitació detectada: Cuina. Analitzant detalls...";
        }
    } 
    else if (response.type === "FINAL_UI") {
        // Resposta completa de Qwen2.5-VL amb el feedback pedagògic
        console.log("🤖 Resposta final (VLM):", response.data);
        uiStatus.innerText = response.data.voz_tutor;
        
        if (response.data.render_ui.status === "ok") {
            objetoVirtual.setAttribute('visible', 'true');
            objetoVirtual.setAttribute('material', 'color', 'green');
        } else if (response.data.render_ui.status === "peligro") {
            objetoVirtual.setAttribute('visible', 'true');
            objetoVirtual.setAttribute('material', 'color', 'red');
        }
    }
};

// Funció d'enginyeria de baix nivell per transformar bytes flotants en so real
function reproducirAudioCrudo(arrayBuffer) {
    const float32Array = new Float32Array(arrayBuffer);
    
    // Crear un buffer d'àudio mono a 16000Hz (el que genera el nostre backend)
    const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 16000);
    audioBuffer.getChannelData(0).set(float32Array);
    
    const source = audioCtx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioCtx.destination);
    
    // Reproduir el so de la veu de forma instantània
    source.start(0);
}

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
