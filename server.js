const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const fs = require('fs/promises');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

app.post('/api/generate', (req, res) => {
    const { url } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    console.log(`Starting generation for: ${url}`);
    
    // Spawn the Python process
    // Using the python executable in the active environment or system python
    const pythonProcess = spawn('python', ['main.py', '--url', url]);

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
        console.log(`Python stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        console.error(`Python stderr: ${data}`);
    });

    pythonProcess.on('close', async (code) => {
        if (code !== 0) {
            console.error(`Python process exited with code ${code}`);
            return res.status(500).json({ 
                error: 'Generation failed',
                details: stderr || stdout
            });
        }

        try {
            // Find the generated file path in the output
            // Output is like: ✓ File: output\webcmd-browser-infrastructure-that-learns-launch-kit.md
            const match = stdout.match(/File:\s+(.+\.md)/);
            if (!match || !match[1]) {
                throw new Error("Could not find generated file path in output");
            }

            const filePath = match[1].trim();
            const absolutePath = path.resolve(__dirname, filePath);
            const fileName = path.basename(absolutePath);

            // Read the markdown file
            const fileContent = await fs.readFile(absolutePath, 'utf8');

            res.json({
                success: true,
                fileName: fileName,
                content: fileContent
            });

        } catch (error) {
            console.error("Error processing output:", error);
            res.status(500).json({ 
                error: 'Failed to process generated file',
                details: error.message
            });
        }
    });
});

app.listen(PORT, () => {
    console.log(`DemoForge Web running at http://localhost:${PORT}`);
});
