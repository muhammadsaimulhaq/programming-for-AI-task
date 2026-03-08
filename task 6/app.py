import os
import cv2
import numpy as np
from flask import Flask, render_template_string, request, jsonify, url_for
from werkzeug.utils import secure_filename
import uuid
import time
import logging

# Flask app initialize karein
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['SECRET_KEY'] = 'animal-detection-secret-key-2025'

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}

# Folders create karein
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('haarcascades', exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== MULTIPLE CASCADE CLASSIFIERS ====================
cascades = {}

# 1. Face cascades
face_cascades = [
    ('catface', cv2.data.haarcascades + 'haarcascade_frontalcatface.xml'),
    ('catface_extended', cv2.data.haarcascades + 'haarcascade_frontalcatface_extended.xml'),
    ('frontalface', cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'),
    ('frontalface_alt', cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'),
    ('frontalface_alt2', cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'),
    ('profileface', cv2.data.haarcascades + 'haarcascade_profileface.xml'),
]

# 2. Body cascades
body_cascades = [
    ('fullbody', cv2.data.haarcascades + 'haarcascade_fullbody.xml'),
    ('upperbody', cv2.data.haarcascades + 'haarcascade_upperbody.xml'),
    ('lowerbody', cv2.data.haarcascades + 'haarcascade_lowerbody.xml'),
]

# Sab cascades load karein
all_cascades = face_cascades + body_cascades

for name, path in all_cascades:
    try:
        cascade = cv2.CascadeClassifier(path)
        if not cascade.empty():
            cascades[name] = cascade
            logger.info(f"✅ Loaded cascade: {name}")
        else:
            logger.warning(f"⚠️ Empty cascade: {name}")
    except Exception as e:
        logger.error(f"❌ Failed to load {name}: {str(e)}")

logger.info(f"Total cascades loaded: {len(cascades)}")

# ==================== NEW MODERN HTML TEMPLATE ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WildSight AI | Animal Detection System</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <!-- Google Fonts - Modern Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    
    <style>
        /* CSS Reset & Global Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: #0a0f1e;
            color: #fff;
            overflow-x: hidden;
        }

        /* Animated Background */
        .background-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: linear-gradient(125deg, #0a0f1e 0%, #1a1f33 50%, #0f172a 100%);
        }

        .background-animation::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            top: -50%;
            left: -50%;
            background: radial-gradient(circle, rgba(255,215,0,0.03) 0%, transparent 50%);
            animation: rotate 30s linear infinite;
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* Floating Particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            width: 2px;
            height: 2px;
            background: rgba(255, 215, 0, 0.3);
            border-radius: 50%;
            animation: float 8s infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
            50% { transform: translateY(-100px) translateX(20px); opacity: 0.5; }
        }

        /* Main Container */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }

        /* Modern Header */
        .modern-header {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
        }

        .logo-container {
            display: inline-block;
            position: relative;
            margin-bottom: 20px;
        }

        .logo-icon {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            border-radius: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            transform: rotate(10deg);
            box-shadow: 0 20px 40px rgba(255, 215, 0, 0.3);
            animation: float-logo 3s ease-in-out infinite;
        }

        @keyframes float-logo {
            0%, 100% { transform: rotate(10deg) translateY(0); }
            50% { transform: rotate(10deg) translateY(-10px); }
        }

        .logo-icon i {
            font-size: 50px;
            color: #0a0f1e;
            transform: rotate(-10deg);
        }

        .main-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 4.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FFD700, #FFA500, #FF8C00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            letter-spacing: 5px;
            margin-bottom: 15px;
            text-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
            animation: glow 3s ease-in-out infinite;
        }

        @keyframes glow {
            0%, 100% { filter: drop-shadow(0 0 20px rgba(255,215,0,0.3)); }
            50% { filter: drop-shadow(0 0 40px rgba(255,215,0,0.6)); }
        }

        .subtitle {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.7);
            letter-spacing: 2px;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* Feature Badges */
        .feature-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
            flex-wrap: wrap;
        }

        .feature-badge-modern {
            padding: 12px 25px;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,215,0,0.2);
            border-radius: 50px;
            color: #FFD700;
            font-weight: 500;
            transition: all 0.3s;
            cursor: default;
        }

        .feature-badge-modern:hover {
            background: rgba(255,215,0,0.1);
            transform: translateY(-3px);
            border-color: #FFD700;
        }

        .feature-badge-modern i {
            margin-right: 8px;
        }

        /* Upload Card - Glassmorphism */
        .glass-card {
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,215,0,0.1);
            border-radius: 40px;
            padding: 50px;
            margin-bottom: 40px;
            transition: all 0.3s;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }

        .glass-card:hover {
            border-color: rgba(255,215,0,0.3);
            box-shadow: 0 25px 50px -12px rgba(255,215,0,0.2);
        }

        .upload-area-modern {
            border: 3px dashed rgba(255,215,0,0.3);
            border-radius: 30px;
            padding: 60px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: rgba(0,0,0,0.2);
        }

        .upload-area-modern:hover {
            border-color: #FFD700;
            background: rgba(255,215,0,0.05);
            transform: scale(1.02);
        }

        .upload-icon {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,165,0,0.1));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
        }

        .upload-icon i {
            font-size: 50px;
            color: #FFD700;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .upload-title {
            font-size: 2rem;
            font-weight: 700;
            color: #FFD700;
            margin-bottom: 15px;
        }

        .upload-text {
            color: rgba(255,255,255,0.6);
            font-size: 1.1rem;
            margin-bottom: 30px;
        }

        .btn-modern {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #0a0f1e;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s;
            box-shadow: 0 10px 20px rgba(255,215,0,0.3);
        }

        .btn-modern:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 40px rgba(255,215,0,0.4);
            color: #0a0f1e;
        }

        .btn-outline-modern {
            background: transparent;
            border: 2px solid #FFD700;
            color: #FFD700;
            padding: 13px 38px;
        }

        .btn-outline-modern:hover {
            background: #FFD700;
            color: #0a0f1e;
        }

        /* File Info */
        .file-info-modern {
            background: rgba(255,215,0,0.1);
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 20px;
            padding: 15px 25px;
            margin-top: 20px;
            color: #FFD700;
            display: none;
        }

        /* Loading Animation */
        .loading-modern {
            text-align: center;
            padding: 50px;
            display: none;
        }

        .loader {
            width: 80px;
            height: 80px;
            border: 5px solid rgba(255,215,0,0.1);
            border-top: 5px solid #FFD700;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 30px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: #FFD700;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
        }

        /* Result Card */
        .result-card-modern {
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,215,0,0.1);
            border-radius: 40px;
            padding: 40px;
            margin-top: 40px;
            display: none;
        }

        .result-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            color: #FFD700;
            margin-bottom: 30px;
        }

        .result-image-container {
            border-radius: 30px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }

        .result-image {
            width: 100%;
            max-height: 400px;
            object-fit: contain;
            background: rgba(0,0,0,0.3);
        }

        .stats-card-modern {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            border-radius: 30px;
            padding: 30px;
            color: #0a0f1e;
            margin-top: 20px;
        }

        .stat-number {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.8;
        }

        .location-badge {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 15px;
        }

        .map-container-modern {
            border-radius: 30px;
            overflow: hidden;
            height: 400px;
            margin-top: 20px;
            border: 2px solid rgba(255,215,0,0.2);
        }

        /* Detection Details */
        .details-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,215,0,0.1);
            border-radius: 30px;
            padding: 30px;
            margin-top: 30px;
        }

        .details-title {
            color: #FFD700;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }

        .detail-item {
            padding: 15px;
            border-bottom: 1px solid rgba(255,215,0,0.1);
            color: rgba(255,255,255,0.8);
        }

        .detail-item:last-child {
            border-bottom: none;
        }

        /* Footer */
        .modern-footer {
            text-align: center;
            padding: 50px 0 20px;
            color: rgba(255,255,255,0.5);
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .footer-links a {
            color: rgba(255,255,255,0.6);
            text-decoration: none;
            transition: all 0.3s;
        }

        .footer-links a:hover {
            color: #FFD700;
        }

        .copyright {
            font-size: 0.9rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2.5rem;
            }
            
            .glass-card {
                padding: 30px;
            }
            
            .upload-area-modern {
                padding: 30px;
            }
            
            .feature-badges {
                gap: 10px;
            }
            
            .feature-badge-modern {
                padding: 8px 15px;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="background-animation"></div>
    
    <!-- Particles -->
    <div class="particles" id="particles"></div>

    <div class="main-container">
        <!-- Modern Header -->
        <div class="modern-header" data-aos="fade-down" data-aos-duration="1000">
            <div class="logo-container">
                <div class="logo-icon">
                    <i class="fas fa-paw"></i>
                </div>
            </div>
            <h1 class="main-title">WildSight AI</h1>
            <p class="subtitle">Advanced Animal Detection & Monitoring System</p>
            
            <div class="feature-badges">
                <span class="feature-badge-modern"><i class="fas fa-bolt"></i> Real-time</span>
                <span class="feature-badge-modern"><i class="fas fa-map-pin"></i> Karachi</span>
                <span class="feature-badge-modern"><i class="fas fa-video"></i> Video Support</span>
                <span class="feature-badge-modern"><i class="fas fa-chart-line"></i> Analytics</span>
            </div>
        </div>

        <!-- Upload Section -->
        <div class="glass-card" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="200">
            <div class="upload-area-modern" id="uploadArea">
                <div class="upload-icon">
                    <i class="fas fa-cloud-upload-alt"></i>
                </div>
                <h2 class="upload-title">Upload Media</h2>
                <p class="upload-text">Drag & drop or click to browse</p>
                <p style="color: rgba(255,255,255,0.4); margin-bottom: 25px;">Supports: JPG, PNG, MP4, AVI, MOV (Max 50MB)</p>
                
                <input type="file" id="fileInput" accept=".jpg,.jpeg,.png,.mp4,.avi,.mov" style="display: none;">
                
                <button class="btn-modern" onclick="document.getElementById('fileInput').click();">
                    <i class="fas fa-folder-open me-2"></i> Choose File
                </button>
            </div>

            <div class="file-info-modern" id="fileInfo">
                <div class="d-flex align-items-center justify-content-between">
                    <span><i class="fas fa-file me-2"></i> <span id="fileName"></span></span>
                    <button class="btn btn-sm btn-danger" onclick="clearFile()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>

            <div class="loading-modern" id="loading">
                <div class="loader"></div>
                <div class="loading-text">Processing your file...</div>
                <p style="color: rgba(255,255,255,0.5);">This may take a few moments</p>
                <div class="progress mt-4" style="height: 5px; background: rgba(255,215,0,0.1);">
                    <div class="progress-bar" style="width: 100%; background: linear-gradient(90deg, #FFD700, #FFA500);"></div>
                </div>
            </div>
        </div>

        <!-- Result Section -->
        <div class="result-card-modern" id="result">
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-success" style="background: rgba(255,215,0,0.1); border: 1px solid #FFD700; color: #FFD700; border-radius: 20px;">
                        <i class="fas fa-check-circle me-2"></i>
                        <span id="messageText">Detection Complete!</span>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-lg-6">
                    <h3 class="result-title"><i class="fas fa-eye me-2"></i>Detection Result</h3>
                    <div class="result-image-container">
                        <img id="resultImage" class="result-image" src="" alt="Detection Result">
                    </div>
                    
                    <div class="stats-card-modern">
                        <div class="row align-items-center">
                            <div class="col-6 text-center">
                                <i class="fas fa-paw fa-3x mb-3"></i>
                                <div class="stat-number" id="animalCount">0</div>
                                <div class="stat-label">Animals Found</div>
                            </div>
                            <div class="col-6 text-center">
                                <i class="fas fa-map-marker-alt fa-3x mb-3"></i>
                                <div class="location-badge">
                                    <strong id="locationName">Karachi, Pakistan</strong>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="text-center mt-3">
                        <span class="badge" id="fileTypeBadge" style="background: rgba(255,215,0,0.1); color: #FFD700; padding: 10px 20px;">Image</span>
                    </div>
                </div>

                <div class="col-lg-6">
                    <h3 class="result-title"><i class="fas fa-map-marked-alt me-2"></i>Location Map</h3>
                    <div id="mapContainer" class="map-container-modern"></div>
                    
                    <div class="text-center mt-4">
                        <button class="btn-modern me-2" onclick="window.location.reload()">
                            <i class="fas fa-redo me-2"></i>New Analysis
                        </button>
                        <button class="btn-outline-modern" onclick="shareResults()">
                            <i class="fas fa-share-alt me-2"></i>Share
                        </button>
                    </div>
                </div>
            </div>

            <div class="details-card" id="detectionDetails">
                <h4 class="details-title"><i class="fas fa-info-circle me-2"></i>Detection Details</h4>
                <p class="text-muted">Processing complete. View results above.</p>
            </div>
        </div>

        <!-- Footer -->
        <div class="modern-footer">
            <div class="footer-links">
                <a href="#"><i class="fas fa-home"></i> Home</a>
                <a href="#"><i class="fas fa-info-circle"></i> About</a>
                <a href="#"><i class="fas fa-envelope"></i> Contact</a>
                <a href="#"><i class="fas fa-shield-alt"></i> Privacy</a>
            </div>
            <div class="copyright">
                <i class="fas fa-copyright me-1"></i> 2025 WildSight AI - Advanced Animal Detection System
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    
    <script>
        // Initialize AOS
        AOS.init();

        // Create Particles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 5 + 's';
                particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
                particlesContainer.appendChild(particle);
            }
        }
        createParticles();

        // DOM Elements
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const resultImage = document.getElementById('resultImage');
        const animalCount = document.getElementById('animalCount');
        const messageText = document.getElementById('messageText');
        const mapContainer = document.getElementById('mapContainer');
        const locationName = document.getElementById('locationName');
        const fileTypeBadge = document.getElementById('fileTypeBadge');
        const detectionDetails = document.getElementById('detectionDetails');

        // Event Listeners
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#FFD700';
            uploadArea.style.background = 'rgba(255,215,0,0.1)';
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'rgba(255,215,0,0.3)';
            uploadArea.style.background = 'rgba(0,0,0,0.2)';
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'rgba(255,215,0,0.3)';
            uploadArea.style.background = 'rgba(0,0,0,0.2)';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        function handleFileSelect(file) {
            if (file.size > 50 * 1024 * 1024) {
                alert('File size exceeds 50MB limit. Please choose a smaller file.');
                return;
            }

            const allowedTypes = ['image/jpeg', 'image/png', 'video/mp4', 'video/avi', 'video/quicktime'];
            if (!allowedTypes.includes(file.type) && 
                !file.name.match(/\\.(jpg|jpeg|png|mp4|avi|mov)$/i)) {
                alert('Invalid file type. Please upload JPG, PNG, MP4, AVI, or MOV files.');
                return;
            }

            fileName.textContent = file.name;
            fileInfo.style.display = 'block';
            
            uploadFile(file);
        }

        function clearFile() {
            fileInput.value = '';
            fileInfo.style.display = 'none';
        }

        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            uploadArea.style.display = 'none';
            fileInfo.style.display = 'none';
            loading.style.display = 'block';
            result.style.display = 'none';

            if (file.type.includes('image')) {
                fileTypeBadge.innerHTML = '<i class="fas fa-image me-2"></i>Image';
            } else if (file.type.includes('video')) {
                fileTypeBadge.innerHTML = '<i class="fas fa-video me-2"></i>Video';
            }

            // Get the current base URL
            const baseUrl = window.location.origin;
            
            fetch(baseUrl + '/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                loading.style.display = 'none';

                if (data.success) {
                    result.style.display = 'block';
                    
                    if (data.image_url) {
                        // Make sure image URL is absolute
                        if (data.image_url.startsWith('/')) {
                            resultImage.src = baseUrl + data.image_url;
                        } else {
                            resultImage.src = data.image_url;
                        }
                    } else {
                        resultImage.src = 'https://via.placeholder.com/600x400?text=Preview+Unavailable';
                    }
                    
                    animalCount.textContent = data.animal_count || 0;
                    messageText.textContent = data.message || 'Detection complete!';
                    locationName.textContent = data.location || 'Karachi, Pakistan';
                    
                    if (data.map_html) {
                        mapContainer.innerHTML = data.map_html;
                    }
                    
                    let detailsHtml = '<h4 class="details-title"><i class="fas fa-info-circle me-2"></i>Detection Details</h4>';
                    if (data.file_type === 'image') {
                        detailsHtml += `
                            <div class="detail-item"><i class="fas fa-file-image me-2"></i> File Type: Image</div>
                            <div class="detail-item"><i class="fas fa-paw me-2"></i> Animals Detected: ${data.animal_count}</div>
                            <div class="detail-item"><i class="fas fa-clock me-2"></i> Time: ${new Date().toLocaleString()}</div>
                        `;
                        
                        if (data.details && data.details.length > 0) {
                            detailsHtml += '<div class="mt-3"><strong>Detections:</strong></div>';
                            data.details.forEach((d, i) => {
                                detailsHtml += `<div class="detail-item">• Detection ${i+1}: ${d.cascade} at (${d.position[0]}, ${d.position[1]})</div>`;
                            });
                        }
                    } else if (data.file_type === 'video') {
                        detailsHtml += `
                            <div class="detail-item"><i class="fas fa-video me-2"></i> File Type: Video</div>
                            <div class="detail-item"><i class="fas fa-paw me-2"></i> Animals Detected: ${data.animal_count}</div>
                            <div class="detail-item"><i class="fas fa-clock me-2"></i> Time: ${new Date().toLocaleString()}</div>
                        `;
                    }
                    
                    detectionDetails.innerHTML = detailsHtml;
                    
                    result.scrollIntoView({ behavior: 'smooth' });
                    
                } else {
                    alert('Error: ' + (data.error || 'Unknown error occurred'));
                    uploadArea.style.display = 'block';
                    loading.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loading.style.display = 'none';
                uploadArea.style.display = 'block';
                alert('Error uploading file: ' + error.message + '\\nPlease check if the server is running.');
            });
        }

        function shareResults() {
            const text = `🐾 WildSight AI Alert! Found ${animalCount.textContent} animals in Karachi!`;
            if (navigator.share) {
                navigator.share({
                    title: 'WildSight AI Detection',
                    text: text,
                    url: window.location.href
                });
            } else {
                navigator.clipboard.writeText(text).then(() => {
                    alert('Results copied to clipboard!');
                }).catch(() => {
                    alert('Text: ' + text);
                });
            }
        }

        window.addEventListener('load', () => {
            locationName.textContent = 'Karachi, Pakistan';
            
            // Test server connection
            fetch(window.location.origin + '/health')
                .then(response => response.json())
                .then(data => {
                    console.log('Server connected:', data);
                })
                .catch(error => {
                    console.error('Server connection failed:', error);
                });
        });
    </script>
</body>
</html>
"""

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_image_for_detection(img):
    """Image ko enhance karein better detection ke liye"""
    try:
        # 1. Denoise
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # 2. Increase contrast
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge([l,a,b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return img
    except Exception as e:
        logger.error(f"Enhancement error: {str(e)}")
        return img

def detect_with_all_cascades(gray_img, color_img):
    """Sab cascades se detection karein"""
    all_detections = []
    detection_details = []
    
    # Image pyramids for multi-scale detection
    scales = [1.0, 0.8, 0.6]
    
    for scale in scales:
        if scale != 1.0:
            width = int(gray_img.shape[1] * scale)
            height = int(gray_img.shape[0] * scale)
            scaled_gray = cv2.resize(gray_img, (width, height))
            scale_factor = 1.0 / scale
        else:
            scaled_gray = gray_img
            scale_factor = 1.0
        
        for name, cascade in cascades.items():
            try:
                if 'face' in name:
                    params = {
                        'scaleFactor': 1.05,
                        'minNeighbors': 3,
                        'minSize': (30, 30),
                        'maxSize': (300, 300)
                    }
                elif 'body' in name:
                    params = {
                        'scaleFactor': 1.1,
                        'minNeighbors': 2,
                        'minSize': (50, 50),
                        'maxSize': (500, 500)
                    }
                else:
                    params = {
                        'scaleFactor': 1.1,
                        'minNeighbors': 3,
                        'minSize': (30, 30),
                        'maxSize': (400, 400)
                    }
                
                detections = cascade.detectMultiScale(
                    scaled_gray,
                    scaleFactor=params['scaleFactor'],
                    minNeighbors=params['minNeighbors'],
                    minSize=params['minSize'],
                    maxSize=params['maxSize'],
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                for (x, y, w, h) in detections:
                    orig_x = int(x * scale_factor)
                    orig_y = int(y * scale_factor)
                    orig_w = int(w * scale_factor)
                    orig_h = int(h * scale_factor)
                    
                    # Avoid duplicates
                    is_duplicate = False
                    for existing in all_detections:
                        ex_x, ex_y, ex_w, ex_h, _ = existing
                        overlap_x = max(0, min(orig_x + orig_w, ex_x + ex_w) - max(orig_x, ex_x))
                        overlap_y = max(0, min(orig_y + orig_h, ex_y + ex_h) - max(orig_y, ex_y))
                        overlap_area = overlap_x * overlap_y
                        area1 = orig_w * orig_h
                        area2 = ex_w * ex_h
                        
                        if overlap_area > 0.3 * min(area1, area2):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        all_detections.append((orig_x, orig_y, orig_w, orig_h, name))
                        
                        if 'cat' in name:
                            color = (0, 255, 0)
                            label = f"Cat"
                        elif 'face' in name:
                            color = (255, 0, 0)
                            label = f"Face"
                        elif 'body' in name:
                            color = (0, 0, 255)
                            label = f"Body"
                        else:
                            color = (255, 255, 0)
                            label = f"Animal"
                        
                        cv2.rectangle(color_img, (orig_x, orig_y), 
                                    (orig_x + orig_w, orig_y + orig_h), color, 2)
                        
                        cv2.putText(color_img, label, (orig_x, orig_y - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        
                        detection_details.append({
                            'cascade': name,
                            'position': [orig_x, orig_y, orig_w, orig_h],
                            'confidence': 'High' if params['minNeighbors'] <= 3 else 'Medium'
                        })
                        
            except Exception as e:
                logger.error(f"Error in cascade {name}: {str(e)}")
                continue
    
    # Filter small detections
    filtered_detections = []
    for det in all_detections:
        x, y, w, h, name = det
        if w * h > 500:
            filtered_detections.append(det)
    
    return color_img, len(filtered_detections), detection_details

def detect_animals_in_image(image_path):
    """Main detection function"""
    try:
        logger.info(f"Processing image: {image_path}")
        
        img = cv2.imread(image_path)
        if img is None:
            logger.error("Failed to read image")
            return None, 0, []
        
        original_img = img.copy()
        enhanced_img = enhance_image_for_detection(img)
        
        gray = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
        
        result_img1, count1, details1 = detect_with_all_cascades(gray, enhanced_img.copy())
        
        gray_original = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        result_img2, count2, details2 = detect_with_all_cascades(gray_original, original_img.copy())
        
        if count1 >= count2:
            final_img = result_img1
            final_count = count1
            final_details = details1
            logger.info(f"Using enhanced image result: {count1} detections")
        else:
            final_img = result_img2
            final_count = count2
            final_details = details2
            logger.info(f"Using original image result: {count2} detections")
        
        if final_count == 0:
            logger.info("No detections with standard params, trying sensitive mode...")
            
            for name, cascade in cascades.items():
                sensitive_detections = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.03,
                    minNeighbors=1,
                    minSize=(20, 20),
                    maxSize=(400, 400)
                )
                
                for (x, y, w, h) in sensitive_detections:
                    cv2.rectangle(final_img, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    cv2.putText(final_img, f"Sensitive", (x, y-5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                    final_count += 1
                    final_details.append({
                        'cascade': f'{name}_sensitive',
                        'position': [x, y, w, h],
                        'confidence': 'Low'
                    })
        
        if final_count > 0:
            summary = f"Total Animals: {final_count}"
            if final_count == 1:
                summary += " (Single Animal)"
            elif final_count <= 3:
                summary += " (Small Herd)"
            elif final_count <= 6:
                summary += " (Medium Herd)"
            else:
                summary += " (Large Herd!)"
            
            cv2.putText(final_img, summary, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        output_filename = f"detected_{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        cv2.imwrite(output_path, final_img)
        
        logger.info(f"Detection complete: {final_count} animals found")
        return output_path, final_count, final_details
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return None, 0, []

def create_static_map(latitude, longitude, animal_count, location_name="Unknown"):
    """Create a simple static map"""
    try:
        map_html = f"""
        <div style="position: relative; height: 100%; width: 100%; background: #1a1f33; border-radius: 30px; overflow: hidden;">
            <img src="https://staticmap.openstreetmap.de/staticmap.php?center={latitude},{longitude}&zoom=14&size=600x400&maptype=mapnik&markers={latitude},{longitude},gold" 
                 style="width: 100%; height: 100%; object-fit: cover;" 
                 alt="Location Map"
                 onerror="this.onerror=null; this.src='https://via.placeholder.com/600x400?text=Map+Unavailable'">
            
            <div style="position: absolute; bottom: 20px; left: 20px; background: rgba(10,15,30,0.9); backdrop-filter: blur(10px); padding: 15px 25px; border-radius: 20px; border: 1px solid rgba(255,215,0,0.3);">
                <h4 style="margin: 0; color: #FFD700; font-weight: 700;">🐾 Alert</h4>
                <p style="margin: 5px 0 0 0; color: rgba(255,255,255,0.8);">
                    <strong>Location:</strong> {location_name}<br>
                    <strong>Animals:</strong> {animal_count}
                </p>
            </div>
            
            <div style="position: absolute; bottom: 20px; right: 20px; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); padding: 8px 15px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(255,215,0,0.2);">
                <i class="fas fa-map-pin" style="color: #FFD700;"></i> {latitude:.4f}, {longitude:.4f}
            </div>
        </div>
        """
        return map_html
        
    except Exception as e:
        logger.error(f"Map creation error: {str(e)}")
        return f"""
        <div style="padding: 30px; background: #1a1f33; border-radius: 30px; text-align: center; height: 100%;">
            <i class="fas fa-map-marked-alt fa-3x mb-3" style="color: #FFD700;"></i>
            <h4 style="color: #FFD700;">Location Information</h4>
            <p style="color: white;"><strong>{location_name}</strong></p>
            <p style="color: rgba(255,255,255,0.6);">Coordinates: {latitude}, {longitude}</p>
            <p style="color: rgba(255,255,255,0.6);">Animals Detected: {animal_count}</p>
        </div>
        """

def get_default_location():
    """Default location return karein (Karachi)"""
    return 24.8607, 67.0011, "Karachi, Pakistan"

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, MP4, AVI, or MOV'}), 400
        
        # Generate unique filename to avoid conflicts
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File saved: {filepath}")
        
        file_size = os.path.getsize(filepath)
        if file_size > 50 * 1024 * 1024:
            os.remove(filepath)
            return jsonify({'error': 'File too large (max 50MB)'}), 400
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext in ['jpg', 'jpeg', 'png']:
            output_path, animal_count, details = detect_animals_in_image(filepath)
            
            if output_path is None:
                return jsonify({'error': 'Error processing image'}), 500
            
            output_filename = os.path.basename(output_path)
            image_url = url_for('static', filename=f'uploads/{output_filename}')
            
            lat, lon, location_name = get_default_location()
            map_html = create_static_map(lat, lon, animal_count, location_name)
            
            response = {
                'success': True,
                'message': f'✅ Detected {animal_count} animals in the image!',
                'animal_count': animal_count,
                'image_url': image_url,
                'map_html': map_html,
                'location': location_name,
                'file_type': 'image',
                'details': details[:5]
            }
            
        elif file_ext in ['mp4', 'avi', 'mov']:
            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                frame_path = os.path.join(app.config['UPLOAD_FOLDER'], f"frame_{uuid.uuid4().hex}.jpg")
                cv2.imwrite(frame_path, frame)
                
                output_path, animal_count, details = detect_animals_in_image(frame_path)
                
                if output_path:
                    image_url = url_for('static', filename=f'uploads/{os.path.basename(output_path)}')
                else:
                    image_url = None
                
                try:
                    os.remove(frame_path)
                except:
                    pass
            else:
                image_url = None
                animal_count = 0
                details = []
            
            lat, lon, location_name = get_default_location()
            map_html = create_static_map(lat, lon, animal_count, location_name)
            
            response = {
                'success': True,
                'message': f'✅ Video processed! Detected {animal_count} animals in first frame.',
                'animal_count': animal_count,
                'image_url': image_url,
                'map_html': map_html,
                'location': location_name,
                'file_type': 'video',
                'details': details[:5]
            }
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        # Clean up uploaded file (keep the detected image)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'cascades_loaded': len(cascades),
        'upload_folder': app.config['UPLOAD_FOLDER']
    })

@app.route('/debug')
def debug():
    """Debug information"""
    return jsonify({
        'cascades': list(cascades.keys()),
        'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
        'cascade_status': {name: not c.empty() for name, c in cascades.items()}
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐾 WILDSIGHT AI - STARTING")
    print("="*60)
    
    print(f"\n📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📊 Cascades loaded: {len(cascades)}")
    
    if len(cascades) > 0:
        print("\n✅ Active cascades:")
        for name in cascades.keys():
            print(f"   - {name}")
    else:
        print("\n❌ WARNING: No cascades loaded!")
        print("   Using fallback detection...")
    
    print(f"\n🌐 Server: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)