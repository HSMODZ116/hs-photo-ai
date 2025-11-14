# app.py
from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HS Modz Ofc - AI Image Transformation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        .aspect-square { aspect-ratio: 1 / 1; }
        .image-container { position: relative; display: inline-block; }
        .download-icon { position: absolute; top: 10px; right: 10px; background-color: rgba(0,0,0,0.6); border-radius: 50%; padding: 8px; cursor: pointer; z-index: 10; color: white; transition: background-color 0.2s ease-in-out; display: none; }
        .download-icon:hover { background-color: rgba(0,0,0,0.8); }
        .image-container.loaded .download-icon { display: block; }
    </style>
</head>
<body class="p-4 sm:p-8 min-h-screen flex items-center justify-center">

<div id="appContainer" class="bg-white p-6 sm:p-10 rounded-xl shadow-2xl w-full max-w-4xl">
    <h1 class="text-3xl sm:text-4xl font-bold text-center mb-6 text-indigo-700">🤖 HS Modz Ofc AI Image Tool</h1>
    <p class="text-center text-gray-500 mb-8">
        Upload your image, and transform it using an AI prompt. (Uses ImgBB for hosting)
    </p>

    <div class="space-y-6 mb-8">
        <div class="flex flex-col">
            <label for="imageFile" class="text-lg font-medium text-gray-700 mb-2">1. Select Your Image File</label>
            <input type="file" id="imageFile" accept="image/*" class="p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
        </div>

        <div class="flex flex-col">
            <label for="promptInput" class="text-lg font-medium text-gray-700 mb-2">2. Transformation Prompt</label>
            <input type="text" id="promptInput" placeholder="Example: make this in cyberpunk style, high detail" class="p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
        </div>

        <button id="processBtn" onclick="processImage()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl shadow-lg transition duration-300 ease-in-out transform hover:scale-[1.01] flex items-center justify-center">
            <svg id="buttonIcon" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.01 12.01 0 002.944 12c0 2.215.717 4.29 2.013 5.965A11.966 11.966 0 0112 21.056c2.813 0 5.448-.96 7.551-2.673A11.967 11.967 0 0021.056 12a12.003 12.003 0 00-1.438-5.016z"></path></svg>
            <span id="buttonText">Upload & Generate Transformation</span>
        </button>

        <p id="message" class="text-sm p-3 rounded-lg text-center hidden"></p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 border-t pt-8 border-gray-200">
        <div class="text-center">
            <h2 class="text-xl font-semibold mb-3 text-gray-800">Your Image (Input)</h2>
            <div class="image-container mx-auto">
                <img id="inputPreview" src="https://placehold.co/400x400/3B82F6/FFFFFF?text=Select+Image+File" alt="Input Image Preview" class="w-full h-auto object-contain rounded-lg shadow-md border-2 border-indigo-300 aspect-square">
            </div>
        </div>

        <div class="text-center">
            <h2 class="text-xl font-semibold mb-3 text-gray-800">AI Transformed Image (Output)</h2>
            <div id="outputImageContainer" class="image-container mx-auto">
                <img id="outputImage" 
                     src="https://placehold.co/400x400/9CA3AF/FFFFFF?text=Result+Will+Appear+Here" 
                     alt="Generated Image" 
                     class="w-full h-auto object-contain rounded-lg shadow-md border-2 border-green-500 aspect-square"
                     onerror="this.src='https://placehold.co/400x400/DC2626/FFFFFF?text=Image+Load+Failed'; showMessage('Error: Generated data was not a valid image.', 'bg-red-100 text-red-800'); this.parentElement.classList.remove('loaded');">
                <button class="download-icon" onclick="downloadTransformedImage()">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                </button>
            </div>
            <button id="downloadBtn" onclick="downloadTransformedImage()" class="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-[1.02] hidden">
                Download Transformed Image
            </button>
        </div>
    </div>

    <div class="mt-10 pt-4 border-t border-gray-200 text-center text-sm text-gray-600">
        <p class="font-bold text-indigo-700 mb-1">Powered by: HS Modz Ofc</p>
        <p>Developed by: <span class="font-semibold text-gray-800">Haseeb Sahil</span></p>
        <p class="mt-2">Join our Telegram: <a href="https://t.me/hsmodzofc2" target="_blank" class="text-blue-600 hover:text-blue-800 font-medium">@hsmodzofc2</a></p>
    </div>
</div>

<script>
const imageFile = document.getElementById('imageFile');
const inputPreview = document.getElementById('inputPreview');
const outputImage = document.getElementById('outputImage');
const outputImageContainer = document.getElementById('outputImageContainer');
const downloadBtn = document.getElementById('downloadBtn');
let transformedImageBlob = null;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

imageFile.addEventListener('change', function() {
    const file = this.files[0];
    if(file){
        const reader = new FileReader();
        reader.onload = e => { inputPreview.src = e.target.result; inputPreview.alt = "Selected image"; };
        reader.readAsDataURL(file);
    } else {
        inputPreview.src = "https://placehold.co/400x400/3B82F6/FFFFFF?text=Select+Image+File";
    }
});

function showMessage(text, classes){
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = `text-sm p-3 rounded-lg text-center mt-4 transition-all duration-300 ${classes}`;
    messageElement.classList.remove('hidden');
}

async function uploadImageToImgBB(file){
    showMessage("1/2: Uploading image to ImgBB...", 'bg-blue-100 text-blue-800');
    const formData = new FormData();
    formData.append("image", file);
    const IMGBB_API_KEY = "5f1df84c72e6ed2483b54305f83c7440";
    const IMGBB_UPLOAD_URL = `https://api.imgbb.com/1/upload?key=${IMGBB_API_KEY}`;
    const resp = await fetch(IMGBB_UPLOAD_URL, { method: 'POST', body: formData });
    const data = await resp.json();
    if(data.success) return data.data.url;
    else throw new Error("ImgBB Upload failed.");
}

async function fetchWithRetry(url, useProxy=true){
    const PROXY_URL = "https://api.allorigins.win/raw?url=";
    const finalUrl = useProxy ? `${PROXY_URL}${encodeURIComponent(url)}` : url;
    const MAX_RETRIES = 3;
    for(let i=0;i<MAX_RETRIES;i++){
        try{
            const response = await fetch(finalUrl);
            if(!response.ok) throw new Error(`API status ${response.status}`);
            return response;
        } catch(e){ if(i<MAX_RETRIES-1){ await delay(Math.pow(2,i)*1000); } else { throw e; } }
    }
}

function downloadTransformedImage(){
    if(transformedImageBlob){
        const url = URL.createObjectURL(transformedImageBlob);
        const a = document.createElement('a'); a.href=url; a.download='ai_transformed_image_HS_Modz.png';
        document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
    } else { showMessage("No image available to download.", 'bg-red-100 text-red-800'); }
}

async function processImage(){
    const prompt = document.getElementById('promptInput').value.trim();
    const file = imageFile.files[0];
    const processBtn = document.getElementById('processBtn');
    const buttonText = document.getElementById('buttonText');
    const buttonIcon = document.getElementById('buttonIcon');

    downloadBtn.classList.add('hidden');
    outputImageContainer.classList.remove('loaded');
    transformedImageBlob = null;

    if(!file){ showMessage("Please select an image file first.", 'bg-yellow-100 text-yellow-800'); return; }
    if(!prompt){ showMessage("Please enter a transformation prompt.", 'bg-yellow-100 text-yellow-800'); return; }

    processBtn.disabled=true; buttonText.textContent="Processing..."; buttonIcon.classList.add('animate-spin');
    outputImage.src="https://placehold.co/400x400/E5E7EB/6B7280?text=Processing...";

    try{
        const publicUrl = await uploadImageToImgBB(file);
        showMessage("1/2: Upload successful. 2/2: Starting AI transformation...", 'bg-indigo-100 text-indigo-800');
        const resp = await fetchWithRetry(`/api/transform`, false, {method:'POST', body:JSON.stringify({prompt:prompt,image_url:publicUrl}), headers: {'Content-Type':'application/json'}});
        const blob = await resp.blob();
        if(blob.size===0) throw new Error("Empty response from transformation API.");
        transformedImageBlob=blob;
        const objectURL=URL.createObjectURL(blob);
        outputImage.src=objectURL; outputImage.alt="AI transformed image";
        outputImage.onload=function(){ showMessage("Image transformation completed successfully!", 'bg-green-100 text-green-800'); downloadBtn.classList.remove('hidden'); outputImageContainer.classList.add('loaded'); URL.revokeObjectURL(objectURL); };
    } catch(e){ console.error(e); showMessage(`Transformation failed: ${e.message}`, 'bg-red-100 text-red-800'); }
    finally{ processBtn.disabled=false; buttonText.textContent="Upload & Generate Transformation"; buttonIcon.classList.remove('animate-spin'); }
}

window.onload=function(){ showMessage("Select your image and enter a prompt to start the 2-step process: Upload then Transform.", 'bg-gray-100 text-gray-700'); }
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/transform", methods=["POST"])
def transform_api():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt", "").strip()
        image_url = data.get("image_url", "").strip()

        if not prompt or not image_url:
            return jsonify({"error":"Both prompt and image URL are required."}),400

        TRANSFORM_API_ENDPOINT = "https://cryyy.itz-ashlynn.workers.dev/img2img"
        resp = requests.get(TRANSFORM_API_ENDPOINT, params={"prompt":prompt,"imageUrl":image_url}, timeout=20)
        resp.raise_for_status()
        return jsonify({"success": True, "result_url": resp.text})
    except Exception as e:
        return jsonify({"error": str(e)}),500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)