import React, { useState } from 'react';
import axios from 'axios';
import { ReactMediaRecorder } from "react-media-recorder";

function App() {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (textPrompt) => {
    setLoading(true);
    const formData = new FormData();
    formData.append("prompt", textPrompt);

    const response = await axios.post("http://localhost:8000/generate", formData, {
      responseType: 'blob'
    });

    setImage(URL.createObjectURL(response.data));
    setLoading(false);
  };

  const handleAudioUpload = async (blob) => {
    const formData = new FormData();
    formData.append("file", blob, "audio.wav");

    const res = await axios.post("http://localhost:8000/transcribe", formData);
    const { prompt } = res.data;
    setPrompt(prompt);
    await handleGenerate(prompt);
  };

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h1>🎨 AI Wallpaper Generator</h1>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your wallpaper..."
        style={{ width: "300px", marginRight: "1rem" }}
      />
      <button onClick={() => handleGenerate(prompt)}>Generate</button>
      <br /><br />
      <ReactMediaRecorder
        audio
        render={({ startRecording, stopRecording }) => (
          <button onMouseDown={startRecording} onMouseUp={stopRecording}>
            🎙️ Hold to Speak
          </button>
        )}
        onStop={handleAudioUpload}
      />
      {loading && <p>Generating...</p>}
      {image && <img src={image} alt="Generated Wallpaper" style={{ marginTop: "2rem", maxWidth: "90%" }} />}
    </div>
  );
}

export default App;
