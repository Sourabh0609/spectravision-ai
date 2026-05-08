// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filterSection = document.getElementById('filterSection');
const processBtn = document.getElementById('processBtn');
const processing = document.getElementById('processing');
const emptyState = document.getElementById('emptyState');
const previewState = document.getElementById('previewState');
const resultState = document.getElementById('resultState');
const previewImage = document.getElementById('previewImage');
const previewVideo = document.getElementById('previewVideo');
const beforeImage = document.getElementById('beforeImage');
const beforeVideo = document.getElementById('beforeVideo');
const afterImage = document.getElementById('afterImage');
const afterVideo = document.getElementById('afterVideo');
const downloadBtn = document.getElementById('downloadBtn');
const newImageBtn = document.getElementById('newImageBtn');
const styleOptions = document.getElementById('styleOptions');
const styleSelect = document.getElementById('styleSelect');
const imageBtn = document.getElementById('imageBtn');
const videoBtn = document.getElementById('videoBtn');
const uploadText = document.getElementById('uploadText');
const uploadHint = document.getElementById('uploadHint');
const processingText = document.getElementById('processingText');

let selectedFile = null;
let resultData = null;
let currentMediaType = 'image';

// Media Type Selection
imageBtn.addEventListener('click', () => {
    currentMediaType = 'image';
    imageBtn.classList.add('active');
    videoBtn.classList.remove('active');
    fileInput.accept = 'image/*';
    uploadText.textContent = 'Click to upload or drag & drop';
    uploadHint.innerHTML = 'Images: PNG, JPG, JPEG, BMP, WEBP (max 16MB)';
    
    // Show/hide filter options
    document.querySelectorAll('.filter-option-image').forEach(el => {
        el.style.display = 'block';
    });
});

videoBtn.addEventListener('click', () => {
    currentMediaType = 'video';
    videoBtn.classList.add('active');
    imageBtn.classList.remove('active');
    fileInput.accept = 'video/*';
    uploadText.textContent = 'Click to upload video';
    uploadHint.innerHTML = 'Videos: MP4, AVI, MOV, MKV (max 100MB)';
    
    // Hide image-only filters
    document.querySelectorAll('.filter-option-image').forEach(el => {
        el.style.display = 'none';
    });
    
    // Select B&W to Color by default for videos
    document.querySelector('input[value="bw_to_color"]').checked = true;
});

// Upload Area Click
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File Input Change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Handle File Selection
function handleFileSelect(file) {
    const isVideo = file.type.startsWith('video/');
    const isImage = file.type.startsWith('image/');
    
    // Validate file type based on current mode
    if (currentMediaType === 'image' && !isImage) {
        alert('Please upload an image file');
        return;
    }
    
    if (currentMediaType === 'video' && !isVideo) {
        alert('Please upload a video file');
        return;
    }
    
    // Validate file size
    const maxSize = currentMediaType === 'video' ? 100 * 1024 * 1024 : 16 * 1024 * 1024;
    if (file.size > maxSize) {
        alert(`File size exceeds ${currentMediaType === 'video' ? '100MB' : '16MB'}. Please upload a smaller file.`);
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        if (isImage) {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';
            previewVideo.style.display = 'none';
        } else if (isVideo) {
            previewVideo.src = e.target.result;
            previewVideo.style.display = 'block';
            previewImage.style.display = 'none';
        }
        
        emptyState.style.display = 'none';
        previewState.style.display = 'block';
        resultState.style.display = 'none';
        filterSection.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// Filter Radio Change
const filterRadios = document.querySelectorAll('input[name="filter"]');
filterRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.value === 'style_transfer') {
            styleOptions.style.display = 'block';
        } else {
            styleOptions.style.display = 'none';
        }
    });
});

// Process Button Click
processBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please upload a file first.');
        return;
    }
    
    const selectedFilter = document.querySelector('input[name="filter"]:checked').value;
    const selectedStyle = styleSelect.value;
    const isVideo = selectedFile.type.startsWith('video/');
    
    // Show processing state
    filterSection.style.display = 'none';
    previewState.style.display = 'none';
    processing.style.display = 'block';
    
    if (isVideo) {
        processingText.textContent = 'Processing video... This may take several minutes depending on video length.';
    } else {
        processingText.textContent = 'Processing your image with SpectraVision AI...';
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('filter', selectedFilter);
    formData.append('style', selectedStyle);
    formData.append('media_type', currentMediaType);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            resultData = data;
            
            // Show result
            if (data.media_type === 'video') {
                beforeVideo.src = data.input_url;
                afterVideo.src = data.output_url;
                beforeVideo.style.display = 'block';
                afterVideo.style.display = 'block';
                beforeImage.style.display = 'none';
                afterImage.style.display = 'none';
            } else {
                beforeImage.src = data.input_url;
                afterImage.src = data.output_url;
                beforeImage.style.display = 'block';
                afterImage.style.display = 'block';
                beforeVideo.style.display = 'none';
                afterVideo.style.display = 'none';
            }
            
            processing.style.display = 'none';
            resultState.style.display = 'block';
        } else {
            throw new Error(data.error || 'Processing failed');
        }
    } catch (error) {
        alert('Error: ' + error.message);
        processing.style.display = 'none';
        previewState.style.display = 'block';
        filterSection.style.display = 'block';
    }
});

// Download Button Click
downloadBtn.addEventListener('click', () => {
    if (resultData && resultData.output_url) {
        const filename = resultData.output_url.split('/').pop();
        const link = document.createElement('a');
        link.href = `/download/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});

// New Media Button Click
newImageBtn.addEventListener('click', () => {
    selectedFile = null;
    resultData = null;
    fileInput.value = '';
    
    resultState.style.display = 'none';
    emptyState.style.display = 'block';
    filterSection.style.display = 'none';
    
    // Reset filter selection
    document.querySelector('input[value="bw_to_color"]').checked = true;
    styleOptions.style.display = 'none';
    
    // Reset media previews
    previewImage.style.display = 'none';
    previewVideo.style.display = 'none';
    beforeImage.style.display = 'none';
    beforeVideo.style.display = 'none';
    afterImage.style.display = 'none';
    afterVideo.style.display = 'none';
});