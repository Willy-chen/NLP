// set up basic variables for app
const record = document.querySelector('.record');
const send = document.querySelector('.send');
const chatBox = document.querySelector('.chat-box .chat-records')
const canvas = document.querySelector('.visualizer');
const mainSection = document.querySelector('.main-controls');

// disable stop button while not recording
send.disabled = true;
var recording = false;

// visualiser setup - create web audio api context and canvas
let audioCtx;
const canvasCtx = canvas.getContext("2d");

let recBuffers = [[], []];
let recLength = 0;
let numChannels = 2;
let listening = false;
let timeout = null;
let constraints = {
    audio: true
};
let failedToGetUserMedia = false;

if (navigator.getUserMedia) {
    navigator.getUserMedia(constraints, (stream) => {
        init(stream);
    }, (err) => {
        alert('Unable to access audio.\n\n' + err);
        console.log('The following error occurred: ' + err);
        failedToGetUserMedia = true;
    });
}
else if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
      

      record.onclick = function() {
        beginRecording();
        send.disabled = false;
        record.disabled = true;
      }

      send.onclick = function() {
        endRecording();
        send.disabled = true;
        record.disabled = false;
      }  
      
      init(stream);
    }).catch((err) => {
        alert('Unable to access audio.\n\n' + err);
        console.log('The following error occurred: ' + err);
        failedToGetUserMedia = true;
    });
}
else failedToGetUserMedia = true;

function beginRecording() {
    recBuffers = [[], []];
    recLength = 0;
    listening = true;
    timeout = setTimeout(() => {
        endRecording();
    }, 60000);
}

function endRecording() {
    clearTimeout(timeout);
    timeout = null;
    blob = exportWAV();
    var data = new FormData()
    data.append("audio", blob, 'temp')
    var clipContainer = document.querySelectorAll('.chat-bubble--right');
    clipContainer = clipContainer[clipContainer.length-1];
    const loadingIcon = document.createElement('div');
    loadingIcon.classList.add('lds-ellipsis');
    for (let i=0;i<4;i++) loadingIcon.appendChild(document.createElement('div'));
    if (clipContainer) clipContainer.appendChild(loadingIcon);
    fetch('/predictApp/upload', {
      method: 'POST',
      body: data

    }).then(response => response.json()
    ).then(json => {
        console.log(json)
        loadingIcon.remove();
        const transcript = document.createElement('div');
        if (json.data['text'] == ''){
          transcript.textContent = "Sorry, could't understand audio.";
          clipContainer.appendChild(transcript); 
        } 
        else{
          transcript.textContent = "\t "+json.data['text'];
          clipContainer.appendChild(transcript); 
          const row = document.createElement('div');
          row.classList.add('row'); 
          row.classList.add('no-gutter');
          const col = document.createElement('div');
          col.classList.add('col-md-3');
          const chatBubble = document.createElement('div');
          chatBubble.classList.add('chat-bubble');
          chatBubble.classList.add('chat-bubble--left');
          col.appendChild(chatBubble);
          row.appendChild(col);
          chatBox.appendChild(row);
          const loadingIcon = document.createElement('div');
          loadingIcon.classList.add('lds-ellipsis');
          for (let i=0;i<4;i++) loadingIcon.appendChild(document.createElement('div'));
          chatBubble.appendChild(loadingIcon);
          fetch('/predictApp/predict', {
            method: 'POST',
            body: json.data['text']
      
          }).then(response => response.json()
          ).then(json => {
            console.log(json);
            loadingIcon.remove();
            chatBubble.textContent = json.data['text'];
          });
        }
    });
}
var context;
function init(stream) {
    let audioContext = new AudioContext();
    let source = audioContext.createMediaStreamSource(stream);
    context = source.context;
    let node = (context.createScriptProcessor || context.createJavaScriptNode).call(context, 4096, numChannels, numChannels);
    node.onaudioprocess = (e) => {
        if (!listening) return;

        for (var i = 0; i < numChannels; i++) {
            recBuffers[i].push([...e.inputBuffer.getChannelData(i)]);
        }

        recLength += recBuffers[0][0].length;
    }
    source.connect(node);
    node.connect(context.destination);
}

function mergeBuffers(buffers, len) {
    let result = new Float32Array(len);
    let offset = 0;
    for (var i = 0; i < buffers.length; i++) {
        result.set(buffers[i], offset);
        offset += buffers[i].length;
    }
    return result;
}

function interleave(inputL, inputR) {
    let len = inputL.length + inputR.length;
    let result = new Float32Array(len);

    let index = 0;
    let inputIndex = 0;

    while (index < len) {
        result[index++] = inputL[inputIndex];
        result[index++] = inputR[inputIndex];
        inputIndex++;
    }

    return result;
}

function exportWAV() {
    let buffers = [];
    for (var i = 0; i < numChannels; i++) {
        buffers.push(mergeBuffers(recBuffers[i], recLength));
    }

    let interleaved = numChannels == 2 ? interleave(buffers[0], buffers[1]) : buffers[0];
    let dataView = encodeWAV(interleaved);
    let blob = new Blob([ dataView ], { type: 'audio/wav' });
    // blob.name = Math.floor((new Date()).getTime() / 1000) + '.wav';

    listening = false;

    return blob;
}

function floatTo16BitPCM(output, offset, input){
    for (var i = 0; i < input.length; i++, offset+=2){
        var s = Math.max(-1, Math.min(1, input[i]));
        output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
}

function writeString(view, offset, string){
    for (var i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

function encodeWAV(samples){
    var buffer = new ArrayBuffer(44 + samples.length * 2);
    var view = new DataView(buffer);

    /* RIFF identifier */
    writeString(view, 0, 'RIFF');
    /* file length */
    view.setUint32(4, 36 + samples.length * 2, true);
    /* RIFF type */
    writeString(view, 8, 'WAVE');
    /* format chunk identifier */
    writeString(view, 12, 'fmt ');
    /* format chunk length */
    view.setUint32(16, 16, true);
    /* sample format (raw) */
    view.setUint16(20, 1, true);
    /* channel count */
    view.setUint16(22, numChannels, true);
    /* sample rate */
    view.setUint32(24, context.sampleRate, true);
    /* byte rate (sample rate * block align) */
    view.setUint32(28, context.sampleRate * 4, true);
    /* block align (channel count * bytes per sample) */
    view.setUint16(32, numChannels * 2, true);
    /* bits per sample */
    view.setUint16(34, 16, true);
    /* data chunk identifier */
    writeString(view, 36, 'data');
    /* data chunk length */
    view.setUint32(40, samples.length * 2, true);

    floatTo16BitPCM(view, 44, samples);

    return view;
}


// //main block for doing the audio recording
if (navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.');

  const constraints = { audio: true };
  let chunks = [];

  let onSuccess = function(stream) {
    const mediaRecorder = new MediaRecorder(stream);

    visualize(stream);

    record.onclick = function() {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("recorder started");
      record.style.background = "#50a878";
      record.textContent = "Recording...";

      beginRecording();

      send.disabled = false;
      record.disabled = true;
    }

    send.onclick = function() {
      
      const clipContainer = document.createElement('section');
      // const clipLabel = document.createElement('p');
      const audio = document.createElement('audio');
      //const deleteButton = document.createElement('button');

      const row = document.createElement('div');
      row.classList.add('row'); 
      row.classList.add('no-gutter');
      const col = document.createElement('div');
      col.classList.add('col-md-3');
      col.classList.add('offset-md-9');
      const chatBubble = document.createElement('div');
      chatBubble.classList.add('chat-bubble');
      chatBubble.classList.add('chat-bubble--right');
      const soundClips = document.createElement('div');
      soundClips.classList.add('sound-clips');


      clipContainer.classList.add('clip');
      audio.setAttribute('controls', '');
      audio.classList.add('player');
      // deleteButton.textContent = 'Delete';
      // deleteButton.className = 'delete';

      clipContainer.appendChild(audio);
      // clipContainer.appendChild(clipLabel);
      // clipContainer.appendChild(deleteButton);
      soundClips.appendChild(clipContainer);
      chatBubble.appendChild(soundClips);
      col.appendChild(chatBubble);
      row.appendChild(col);
      chatBox.appendChild(row);

      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("recorder stopped");
      record.style.background = "";
      record.style.color = "";
      record.textContent = "Record";
      // mediaRecorder.requestData();
      endRecording();

      send.disabled = true;
      record.disabled = false;
    }

    mediaRecorder.onstop = function(e) {
      console.log("data available after MediaRecorder.stop() called.");

      const clipName = "Temp";//prompt('Enter a name for your sound clip?','Unnamed');

      var audio = document.querySelectorAll('.player');  
      audio = audio[audio.length-1];
      // audio.controls = true;
      const blob = new Blob(chunks, { 'type' : 'audio/webm; codec=opus' });
      // chunks = [];
      // console.log(blob);
      const audioURL = window.URL.createObjectURL(blob);
      audio.src = audioURL;
      // console.log("recorder stopped");

      // deleteButton.onclick = function(e) {
      //   let evtTgt = e.target;
      //   evtTgt.parentNode.parentNode.removeChild(evtTgt.parentNode);
      // }

    }

    mediaRecorder.ondataavailable = function(e) {
      chunks.push(e.data);
    }
  }

  let onError = function(err) {
    console.log('The following error occured: ' + err);
  }

  navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);

} else {
   console.log('getUserMedia is not supported on your browser!');
}

function visualize(stream) {
  if(!audioCtx) {
    audioCtx = new AudioContext();
  }

  const source = audioCtx.createMediaStreamSource(stream);

  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  source.connect(analyser);
  //analyser.connect(audioCtx.destination);

  draw()

  function draw() {
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;

    requestAnimationFrame(draw);

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = 'rgb(80, 206, 135)';
    canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

    canvasCtx.beginPath();

    let sliceWidth = WIDTH * 1.0 / bufferLength;
    let x = 0;


    for(let i = 0; i < bufferLength; i++) {

      let v = dataArray[i] / 128.0;
      let y = v * HEIGHT/2;

      if(i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height/2);
    canvasCtx.stroke();

  }
}

window.onresize = function() {
  canvas.width = mainSection.clientWidth;
}

window.onload = ()=>{canvas.width = mainSection.clientWidth;};

window.onresize();

