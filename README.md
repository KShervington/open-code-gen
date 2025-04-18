# Open Code Gen

A VSCode extension that uses LLM-powered code completion to help developers write code more efficiently. This extension leverages the Ollama API to generate contextually relevant code suggestions based on your current code.

## Features

### AI-Powered Code Completion

This extension provides intelligent code completion using a local LLM through Ollama:

- **Context-Aware Completions**: The extension analyzes your code context to provide relevant suggestions
- **Right-Click to Complete Code**: Simply right-click in your editor and select "Complete code" from the context menu
- **Progress Notification**: A notification shows the progress while the LLM generates your code completion

## Requirements

- [Ollama](https://ollama.ai/) must be installed and running locally
- The `qwen2.5-coder:7b` model should be pulled in Ollama (or modify the model in the source code)

## Installation

### From Source

1. Clone this repository
2. Run `npm install` to install dependencies
3. Run `npm run compile` to compile the TypeScript code
4. Press F5 in VSCode to launch the extension in debug mode

## Usage

1. Open any code file in VSCode
2. Position your cursor where you want to insert code
3. Right-click and select "Complete code" from the context menu
4. Wait for the LLM to generate a completion (a notification will show progress)
5. The generated code will be inserted at your cursor position

## How It Works

The extension uses the following components:

- **ReviewProvider**: Interfaces with the Ollama API to generate code completions
- **Context Menu Integration**: Provides a right-click option to trigger code completion
- **Code Context Analysis**: Extracts relevant code context from your current file

## Technical Details

The extension is built with:

- TypeScript
- VSCode Extension API
- LangChain.js for Ollama integration
- Ollama for local LLM inference

## Known Issues

- The extension requires Ollama to be running locally
- Large code completions may take some time to generate depending on your hardware
- The extension currently uses a fixed number of lines for context (6 lines)

## Future Improvements

- Add configuration options for model selection
- Implement customizable context window size
- Add support for more advanced code generation features
- Improve error handling and user feedback

## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0

Initial release of ...

### 1.0.1

Fixed issue #.

### 1.1.0

Added features X, Y, and Z.

---

## Following extension guidelines

Ensure that you've read through the extensions guidelines and follow the best practices for creating your extension.

* [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Working with Markdown

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
