// Get access to the VS Code API from within the webview
const vscode = acquireVsCodeApi();

// Initialize state management
const previousState = vscode.getState() || { content: "" };
let currentContent = previousState.content || "";

// Handle messages from the extension
window.addEventListener("message", (event) => {
  const message = event.data;

  switch (message.command) {
    case "updateContent":
      // Update the content with the markdown
      currentContent = message.content;
      updateContentView();
      break;
  }
});

// Initialize content on load if we have any
document.addEventListener("DOMContentLoaded", () => {
  if (currentContent) {
    updateContentView();
  }
});

// Update the content view with the current markdown content
function updateContentView() {
  const contentElement = document.getElementById("content");

  // Use the marked library to convert markdown to HTML
  contentElement.innerHTML = marked.parse(currentContent);

  // Highlight code blocks and add copy buttons
  document.querySelectorAll("pre code").forEach((block, index) => {
    highlightSyntax(block);
    addCopyButton(block, index);
  });

  // Save state
  vscode.setState({ content: currentContent });
}

// Add a copy button to a code block
function addCopyButton(block, index) {
  // Create wrapper if it doesn't exist yet
  const pre = block.parentElement;
  if (!pre.classList.contains("code-block-wrapper")) {
    // Create wrapper div for positioning
    const wrapper = document.createElement("div");
    wrapper.className = "code-block-wrapper";
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);

    // Create the copy button
    const copyButton = document.createElement("button");
    copyButton.className = "copy-code-button";
    copyButton.textContent = "Copy";
    copyButton.setAttribute("data-index", index.toString());
    wrapper.appendChild(copyButton);

    // Add click event to the copy button
    copyButton.addEventListener("click", (e) => {
      const codeContent = block.textContent;
      navigator.clipboard.writeText(codeContent).then(() => {
        // Visual feedback
        const button = e.target;
        const originalText = button.textContent;
        button.textContent = "Copied!";
        button.classList.add("copied");

        // Reset after a short delay
        setTimeout(() => {
          button.textContent = originalText;
          button.classList.remove("copied");
        }, 2000);

        // Notify extension
        vscode.postMessage({
          command: "notification",
          text: "Code copied to clipboard",
        });
      });
    });
  }
}

// Simple syntax highlighting function
function highlightSyntax(element) {
  // Add a class for styling
  element.classList.add("code-block");

  // You could implement more sophisticated syntax highlighting here
  // or use a library like highlight.js in a production extension
}

// Set up event listeners once the DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  const copyButton = document.getElementById("copy-button");

  // Set up the copy to clipboard button (copies all code blocks)
  copyButton.addEventListener("click", () => {
    // Extract code from markdown (simple approach)
    const codeContent = extractCodeFromMarkdown(currentContent);

    // Copy to clipboard
    navigator.clipboard.writeText(codeContent).then(() => {
      vscode.postMessage({
        command: "notification",
        text: "All code blocks copied to clipboard",
      });
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
  let code = "";

  while ((match = codeBlockRegex.exec(markdown)) !== null) {
    code += match[1] + "\n\n";
  }

  // If no code blocks found, return the original content
  // (might be inline code or just text)
  return code.trim() || markdown;
}
