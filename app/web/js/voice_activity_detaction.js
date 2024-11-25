let myvad = null
let isListening = false;

async function createVad(onAudio) {
  if (myvad) {
    return
  }
  myvad = await vad.MicVAD.new({
    onSpeechEnd: (audio) => {
      onAudio(audio)
    }
  })
}

function isVadCreated() {
  return myvad != null
}

function startVad() {
  if (myvad && !isListening) {
    myvad.start()
    isListening = true
  }
}

function listeningVad() {
 return isListening
}

function pauseVad() {
  if (myvad && isListening) {
    myvad.pause()
    isListening = false
  }
}

function destroyVad() {
  if (myvad) {
    myvad.destroy()
    myvad = null
    isListening = false
  }
}
