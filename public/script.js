document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generate-form');
    const urlInput = document.getElementById('url-input');
    
    const formState = document.getElementById('generate-form');
    const loadingState = document.getElementById('loading-state');
    const successState = document.getElementById('success-state');
    const errorState = document.getElementById('error-state');
    
    const errorMessage = document.getElementById('error-message');
    
    const downloadBtn = document.getElementById('download-btn');
    const resetBtn = document.getElementById('reset-btn');
    const retryBtn = document.getElementById('retry-btn');

    let currentFileContent = '';
    let currentFileName = 'launch-kit.md';

    function showState(stateElement) {
        formState.classList.add('hidden');
        loadingState.classList.add('hidden');
        successState.classList.add('hidden');
        errorState.classList.add('hidden');
        
        if (stateElement) {
            stateElement.classList.remove('hidden');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        // Switch to loading
        showState(loadingState);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate Launch Kit');
            }

            // Success
            currentFileContent = data.content;
            currentFileName = data.fileName;
            showState(successState);

        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = error.message;
            showState(errorState);
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (!currentFileContent) return;

        const blob = new Blob([currentFileContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = currentFileName;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    const resetUI = () => {
        urlInput.value = '';
        showState(formState);
        urlInput.focus();
    };

    resetBtn.addEventListener('click', resetUI);
    retryBtn.addEventListener('click', () => {
        showState(formState);
    });
});
