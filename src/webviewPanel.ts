import * as vscode from 'vscode';
import * as path from 'path';

export class CodeCompletionWebviewPanel {
  public static currentPanel: CodeCompletionWebviewPanel | undefined;
  public readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    
    // Set the webview's initial html content
    this._panel.webview.html = this._getHtmlForWebview(this._panel.webview, extensionUri);
    
    // Listen for when the panel is disposed
    // This happens when the user closes the panel or when the panel is closed programmatically
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it.
    if (CodeCompletionWebviewPanel.currentPanel) {
      CodeCompletionWebviewPanel.currentPanel._panel.reveal(column);
      return CodeCompletionWebviewPanel.currentPanel;
    }

    // Otherwise, create a new panel.
    const panel = vscode.window.createWebviewPanel(
      'codeCompletionView',
      'Code Completion',
      column || vscode.ViewColumn.One,
      {
        // Enable javascript in the webview
        enableScripts: true,
        // Restrict the webview to only load resources from the `media` directory
        localResourceRoots: [
          vscode.Uri.joinPath(extensionUri, 'media')
        ]
      }
    );

    CodeCompletionWebviewPanel.currentPanel = new CodeCompletionWebviewPanel(panel, extensionUri);
    return CodeCompletionWebviewPanel.currentPanel;
  }

  public updateContent(markdownContent: string) {
    // Send a message to the webview with the markdown content
    this._panel.webview.postMessage({ 
      command: 'updateContent', 
      content: markdownContent 
    });
  }

  public dispose() {
    CodeCompletionWebviewPanel.currentPanel = undefined;

    // Clean up our resources
    this._panel.dispose();

    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }

  private _getHtmlForWebview(webview: vscode.Webview, extensionUri: vscode.Uri) {
    // Get the local path to main script run in the webview
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(extensionUri, 'media', 'main.js')
    );

    // Get the local path to css styles
    const styleMainUri = webview.asWebviewUri(
      vscode.Uri.joinPath(extensionUri, 'media', 'styles.css')
    );

    // Use a nonce to only allow specific scripts to be run
    const nonce = getNonce();

    return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
      <link href="${styleMainUri}" rel="stylesheet">
      <title>Code Completion</title>
    </head>
    <body>
      <div class="container">
        <h1>Code Completion</h1>
        <div class="actions">
          <button id="copy-button">Copy to Clipboard</button>
          <button id="insert-button">Insert at Cursor</button>
        </div>
        <div id="content" class="content"></div>
      </div>
      <script nonce="${nonce}" src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
      <script nonce="${nonce}" src="${scriptUri}"></script>
    </body>
    </html>`;
  }
}

function getNonce() {
  let text = '';
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
