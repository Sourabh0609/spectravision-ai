
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

const filterSection = document.getElementById('filterSection');

const processBtn = document.getElementById('processBtn');

const processing = document.getElementById('processing');

const emptyState = document.getElementById('emptyState');

const previewState = document.getElementById('previewState');

const resultState = document.getElementById('resultState');

const previewImage = document.getElementById('previewImage');

const beforeImage = document.getElementById('beforeImage');

const afterImage = document.getElementById('afterImage');

const downloadBtn = document.getElementById('downloadBtn');

const newImageBtn = document.getElementById('newImageBtn');

const styleOptions = document.getElementById('styleOptions');

const styleSelect = document.getElementById('styleSelect');

let selectedFile = null;

let resultData = null;



// CLICK UPLOAD
uploadArea.addEventListener('click', () => {

    fileInput.click();

});



// FILE SELECT
fileInput.addEventListener('change', (e) => {

    if (e.target.files.length > 0) {

        handleFileSelect(e.target.files[0]);

    }

});



// HANDLE FILE
function handleFileSelect(file) {

    if (!file.type.startsWith('image/')) {

        alert('Please upload image only');

        return;
    }

    selectedFile = file;

    const reader = new FileReader();

    reader.onload = (e) => {

        previewImage.src = e.target.result;

        emptyState.style.display = 'none';

        previewState.style.display = 'block';

        resultState.style.display = 'none';

        filterSection.style.display = 'block';

    };

    reader.readAsDataURL(file);

}



// FILTER CHANGE
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



// PROCESS
processBtn.addEventListener('click', async () => {

    if (!selectedFile) {

        alert('Upload image first');

        return;
    }

    const selectedFilter =
        document.querySelector('input[name="filter"]:checked').value;

    const selectedStyle = styleSelect.value;

    processing.style.display = 'block';

    previewState.style.display = 'none';

    filterSection.style.display = 'none';

    const formData = new FormData();

    formData.append('file', selectedFile);

    formData.append('filter', selectedFilter);

    formData.append('style', selectedStyle);

    try {

        const response = await fetch('/upload', {

            method: 'POST',

            body: formData

        });

        let data;

        try {

            data = await response.json();

        } catch {

            throw new Error('Server error');

        }

        if (response.ok && data.success) {

            resultData = data;

            beforeImage.src = data.input_url;

            afterImage.src = data.output_url;

            processing.style.display = 'none';

            resultState.style.display = 'block';

        }

        else {

            throw new Error(data.error || 'Processing failed');

        }

    }

    catch (error) {

        alert(error.message);

        processing.style.display = 'none';

        previewState.style.display = 'block';

        filterSection.style.display = 'block';

    }

});



// DOWNLOAD
downloadBtn.addEventListener('click', () => {

    if (!resultData) return;

    const filename =
        resultData.output_url.split('/').pop();

    const link = document.createElement('a');

    link.href = `/download/${filename}`;

    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

});



// RESET
newImageBtn.addEventListener('click', () => {

    selectedFile = null;

    resultData = null;

    fileInput.value = '';

    resultState.style.display = 'none';

    previewState.style.display = 'none';

    filterSection.style.display = 'none';

    emptyState.style.display = 'block';

});
