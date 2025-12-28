from flask import Flask, render_template_string, request, send_file, jsonify
from PIL import Image, ImageOps
import os
import io
import zipfile
from pillow_heif import register_heif_opener

# Register HEIC/HEIF support
register_heif_opener()

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Canvas Image Resizer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .settings {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .setting-group {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #555;
            font-size: 14px;
        }
        input[type="number"] {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border 0.3s;
        }
        input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .drop-zone {
            border: 3px dashed #ccc;
            border-radius: 15px;
            padding: 60px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #fafafa;
        }
        .drop-zone:hover, .drop-zone.dragover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        .drop-zone p {
            color: #666;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .drop-zone small {
            color: #999;
            font-size: 14px;
        }
        #fileInput {
            display: none;
        }
        .file-list {
            margin-top: 20px;
        }
        .file-item {
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            margin-top: 20px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-primary:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .progress {
            display: none;
            margin-top: 20px;
            text-align: center;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖼️ Canvas Image Resizer</h1>
        
        <div class="settings">
            <div class="setting-group">
                <label for="canvasWidth">Canvas Width (px)</label>
                <input type="number" id="canvasWidth" value="1080" min="1">
            </div>
            <div class="setting-group">
                <label for="canvasHeight">Canvas Height (px)</label>
                <input type="number" id="canvasHeight" value="1350" min="1">
            </div>
            <div class="setting-group">
                <label for="verticalPadding">Vertical Padding (px)</label>
                <input type="number" id="verticalPadding" value="32" min="0">
            </div>
            <div class="setting-group">
                <label for="horizontalPadding">Horizontal Padding (px)</label>
                <input type="number" id="horizontalPadding" value="114" min="0">
            </div>
        </div>

        <div class="drop-zone" id="dropZone">
            <p>📁 Drag & drop images here</p>
            <small>or click to browse</small>
            <input type="file" id="fileInput" multiple accept="image/*,.heic,.heif">
        </div>

        <div class="file-list" id="fileList"></div>

        <button class="btn btn-primary" id="processBtn" disabled>Process Images</button>

        <div class="progress" id="progress">
            <div class="spinner"></div>
            <p>Processing images...</p>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const processBtn = document.getElementById('processBtn');
        const progress = document.getElementById('progress');
        let selectedFiles = [];

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        function handleFiles(files) {
            selectedFiles = Array.from(files);
            displayFiles();
            processBtn.disabled = selectedFiles.length === 0;
        }

        function displayFiles() {
            fileList.innerHTML = '';
            selectedFiles.forEach((file, index) => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.innerHTML = `
                    <span>${file.name}</span>
                    <span style="color: #999;">${(file.size / 1024 / 1024).toFixed(2)} MB</span>
                `;
                fileList.appendChild(div);
            });
        }

        processBtn.addEventListener('click', async () => {
            if (selectedFiles.length === 0) return;

            const formData = new FormData();
            selectedFiles.forEach(file => formData.append('files', file));
            formData.append('canvasWidth', document.getElementById('canvasWidth').value);
            formData.append('canvasHeight', document.getElementById('canvasHeight').value);
            formData.append('verticalPadding', document.getElementById('verticalPadding').value);
            formData.append('horizontalPadding', document.getElementById('horizontalPadding').value);

            processBtn.disabled = true;
            progress.style.display = 'block';

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'resized_images.zip';
                    a.click();
                    window.URL.revokeObjectURL(url);
                } else {
                    alert('Error processing images');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                progress.style.display = 'none';
                processBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

def resize_and_center_image(img, canvas_width, canvas_height, vertical_padding, horizontal_padding):
    """Resize image to fit canvas with padding and center it."""
    # Fix orientation based on EXIF data
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # Calculate maximum dimensions with padding
    max_width = canvas_width - (2 * horizontal_padding)
    max_height = canvas_height - (2 * vertical_padding)
    
    # Calculate scaling factor to fit within bounds
    width_ratio = max_width / img.width
    height_ratio = max_height / img.height
    scale_factor = min(width_ratio, height_ratio)
    
    # Calculate new dimensions
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    
    # Resize image
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Create white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # Calculate position to center the image
    x = (canvas_width - new_width) // 2
    y = (canvas_height - new_height) // 2
    
    # Paste resized image onto canvas
    canvas.paste(img_resized, (x, y))
    
    return canvas

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_images():
    files = request.files.getlist('files')
    canvas_width = int(request.form.get('canvasWidth', 1080))
    canvas_height = int(request.form.get('canvasHeight', 1350))
    vertical_padding = int(request.form.get('verticalPadding', 32))
    horizontal_padding = int(request.form.get('horizontalPadding', 114))
    
    # Create zip file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            try:
                # Open image
                img = Image.open(file.stream)
                
                # Process image
                processed_img = resize_and_center_image(
                    img, canvas_width, canvas_height, 
                    vertical_padding, horizontal_padding
                )
                
                # Save to buffer
                img_buffer = io.BytesIO()
                processed_img.save(img_buffer, 'JPEG', quality=95)
                img_buffer.seek(0)
                
                # Add to zip
                original_name = os.path.splitext(file.filename)[0]
                zip_file.writestr(f"{original_name}.jpg", img_buffer.getvalue())
                
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='resized_images.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)