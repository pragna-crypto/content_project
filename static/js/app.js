document.addEventListener('DOMContentLoaded', () => {

    // Text area character counter
    const textArea = document.getElementById('manual-text');
    const charCounter = document.getElementById('char-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    function toggleAnalyzeBtn(hasContent) {
        if (analyzeBtn) {
            analyzeBtn.style.display = hasContent ? 'block' : 'none';
        }
    }
    
    if (textArea && charCounter) {
        textArea.addEventListener('input', () => {
            const length = textArea.value.trim().length;
            charCounter.innerText = `${length} characters`;
            toggleAnalyzeBtn(length > 0 || (fileInput && fileInput.files.length > 0));
        });
    }

    // Drag and Drop
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-upload');
    
    if (dropZone && fileInput) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, (e) => {
                dropZone.classList.remove('dragover');
            });
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                toggleAnalyzeBtn(true);
                handleAnalysis(fileInput.files[0], null);
            }
        });
        
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                toggleAnalyzeBtn(true);
                handleAnalysis(fileInput.files[0], null);
            }
        });
    }
    
    // Manual text analyze btn
    if (analyzeBtn && textArea) {
        analyzeBtn.addEventListener('click', () => {
            if (textArea.value.trim().length > 0) {
                handleAnalysis(null, textArea.value);
            } else if (fileInput && fileInput.files.length > 0) {
                handleAnalysis(fileInput.files[0], null);
            } else {
                alert('Please enter some text or upload a file.');
            }
        });
    }

    // AJAX Analysis function
    function handleAnalysis(file, text) {
        const overlay = document.getElementById('scanner-overlay');
        overlay.classList.add('active');
        
        const formData = new FormData();
        if (file) {
            formData.append('file', file);
        } else if (text) {
            formData.append('text', text);
        }
        
        // Setup CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Fake latency for the "scanning feel"
        setTimeout(() => {
            fetch('/api/analyze/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin', // Ensure cookies are sent for CSRF
                body: formData
            })
            .then(async response => {
                const contentType = response.headers.get("content-type");
                let data;
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    data = await response.json();
                } else {
                    const text = await response.text();
                    // if it's an HTML error page (e.g., 403 CSRF or 500), wrap it
                    throw new Error(`Server returned ${response.status}: ` + text.substring(0, 100));
                }
                
                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                return data;
            })
            .then(data => {
                overlay.classList.remove('active');
                if(data.error) {
                    alert(data.error);
                } else {
                    renderResults(data);
                }
            })
            .catch(error => {
                overlay.classList.remove('active');
                console.error(error);
                alert("Error analyzing content. Try reloading the page if this persists.");
            });
        }, 1500); // 1.5s scanning effect
    }

    // Render results
    function renderResults(data) {
        // Hide input area, show results
        document.getElementById('input-section').style.display = 'none';
        const resultsGrid = document.getElementById('results-section');
        resultsGrid.classList.add('visible');
        
        // Update Gauge
        const gauge = document.getElementById('ai-gauge');
        const gaugeVal = document.getElementById('ai-gauge-value');
        
        // Define color based on probability
        let color = '#10b981'; // emerald
        if (data.ai_probability > 70) color = '#ef4444'; // red
        else if (data.ai_probability > 40) color = '#f59e0b'; // amber
        
        gauge.style.setProperty('--gauge-color', color);
        // Animate gauge from 0 to value
        setTimeout(() => {
            gauge.style.setProperty('--gauge-deg', `${(data.ai_probability / 100) * 360}deg`);
        }, 100);
        
        gaugeVal.innerText = `${data.ai_probability}%`;
        gaugeVal.style.color = color;
        
        // Metrics
        document.getElementById('metric-perplexity').innerText = data.perplexity;
        document.getElementById('metric-burstiness').innerText = data.burstiness;
        
        // Heatmap
        const heatmapContainer = document.getElementById('heatmap-content');
        heatmapContainer.innerHTML = '';
        
        data.heatmap_data.forEach(item => {
            const span = document.createElement('span');
            span.className = `sentence ${item.color}`;
            span.innerText = item.text + ' ';
            // Adding a title for hover detail
            span.title = `AI Score: ${item.score}`;
            heatmapContainer.appendChild(span);
        });
    }
});
