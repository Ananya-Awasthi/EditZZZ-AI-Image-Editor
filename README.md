#EditZZZ – AI-Powered Online Image Editor

EditZZZ is a web-based image editing application built using Flask and OpenCV.
It allows users to upload images, apply various filters (including AI-style effects), resize images, and download the processed results — all through a clean and simple UI.

🚀 Features
🔧 Basic Image Editing

Grayscale conversion

Blur filter

Sharpen filter

Image rotation (90°)

🤖 AI-Style Image Processing

Cartoonify effect (bilateral filtering + adaptive thresholding)

Edge detection using Canny algorithm

📐 Image Resizing

Resize images to custom width and height

Maintains fast processing and quality output

🧹 Automatic File Cleanup

Automatically deletes uploaded and processed images older than 5 minutes

Prevents disk space overflow

Mimics real-world production behavior

🔐 Secure & Safe

File type validation

UUID-based filenames (prevents overwriting)

Sanitized filenames using Werkzeug

🛠️ Tech Stack

Backend: Flask (Python)

Image Processing: OpenCV, NumPy

Frontend: HTML, Bootstrap 5

Utilities: UUID, File lifecycle management
