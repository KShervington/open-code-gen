// Get access to the VS Code API from within the webview
const vscode = acquireVsCodeApi();

// Store state information
let currentContent = '';

// Handle messages from the extension
window.addEventListener('message', event => {
    const message = event.data;
    
    switch (message.command) {
        case 'updateContent':
            // Update the content with the markdown
            currentContent = message.content;
            updateContentView();
            break;
    }
});

// Update the content view with the current markdown content
function updateContentView() {
    const contentElement = document.getElementById('content');
    
    // Use the marked library to convert markdown to HTML
    contentElement.innerHTML = marked.parse(currentContent);
    
    // Highlight code blocks
    document.querySelectorAll('pre code').forEach((block) => {
        highlightSyntax(block);
    });
}

// Simple syntax highlighting function
function highlightSyntax(element) {
    // Add a class for styling
    element.classList.add('code-block');
    
    // You could implement more sophisticated syntax highlighting here
    // or use a library like highlight.js in a production extension
}

// Set up event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const copyButton = document.getElementById('copy-button');
    const insertButton = document.getElementById('insert-button');
    
    // Set up the copy to clipboard button
    copyButton.addEventListener('click', () => {
        // Extract code from markdown (simple approach)
        const codeContent = extractCodeFromMarkdown(currentContent);
        
        // Copy to clipboard
        navigator.clipboard.writeText(codeContent).then(() => {
            vscode.postMessage({
                command: 'notification',
                text: 'Code copied to clipboard'
            });
        });
    });
    
    // Set up the insert at cursor button
    insertButton.addEventListener('click', () => {
        // Extract code from markdown
        const codeContent = extractCodeFromMarkdown(currentContent);
        
        // Send message to extension to insert at cursor
        vscode.postMessage({
            command: 'insertAtCursor',
            text: codeContent
        });
    });
});

// Extract code blocks from markdown
function extractCodeFromMarkdown(markdown) {
    // This is a simple extraction that looks for code blocks
    // A more robust implementation would use a proper markdown parser
    
    // Look for code blocks (```code```)
    const codeBlockRegex = /```(?:\w*\n)?([\s\S]*?)```/g;
    let match;
    let code = '';
    
    while ((match = codeBlockRegex.exec(markdown)) !== null) {
        code += match[1] + '\n\n';
    }
    
    // If no code blocks found, return the original content
    // (might be inline code or just text)
    return code.trim() || markdown;
}
