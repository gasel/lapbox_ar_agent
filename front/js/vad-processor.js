// frontend/js/vad-processor.js
class VADProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    // Tasa de muestreo estándar que espera Whisper (16kHz)
    this.targetSampleRate = 16000; 
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (input && input[0]) {
      const channelData = input[0];
      
      // Enviar los frames de audio directamente al hilo principal (app.js)
      this.port.postMessage({
        message: 'AUDIO_FRAME',
        buffer: channelData
      });
    }
    return true;
  }
}

registerProcessor('vad-processor', VADProcessor);
