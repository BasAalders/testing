# Pocket Code

A code editor built for phones, in the spirit of VS Code. It is a single web page with no build step and no server.

## What it does

- **Editor** with syntax colors for HTML, CSS, JavaScript, TypeScript, JSON, Python, Markdown, C, C++, Java, C#, Kotlin, Shell, SQL, YAML, XML and Jinja templates.
- **Tabs** for open files and an **explorer** with folders. Rename, move, duplicate and delete from the dots on each row.
- **Key row** above the phone keyboard with Tab, arrow keys, brackets, symbols, undo, redo and comment toggle. Hold an arrow to repeat it.
- **Search bar** at the top works like VS Code's quick open. Type a file name, `>` for commands, or `:42` to jump to line 42.
- **Find and replace** for the current file.
- **Run** shows a live preview of HTML pages. Linked `.css` and `.js` files from the project are pulled in automatically. Markdown files render as formatted pages.
- **Console** shows `console.log` output and errors, and can run JavaScript inside the preview.
- **Settings** for text size, dark or light theme, word wrap, indent size and the key row.
- **Import** text files or a ZIP. **Export** the whole project as a ZIP.
- **Offline** after the first visit when served over HTTPS, and installable with "Add to Home Screen".

Files save automatically in the browser's local storage on your device. They are not synced anywhere, so export a ZIP now and then as a backup.

Python files get syntax colors but can't run in the browser.

## Put it on your phone

The easiest way is GitHub Pages:

1. On GitHub, open the repository's **Settings**, then **Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**, pick the branch, and pick `/ (root)`.
3. After a minute, open `https://<your-username>.github.io/<repo>/pocket_code/` on your phone.
4. Use your browser's **Add to Home Screen** so it opens like an app.

To try it on a computer, open `index.html` in a browser, or serve the folder:

```bash
cd pocket_code
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole app: layout, styles and script |
| `manifest.webmanifest` | Lets phones install it as a home-screen app |
| `sw.js` | Caches the app so it works offline |
| `icon.svg` | App icon |

## Shortcuts with a hardware keyboard

| Keys | Action |
| --- | --- |
| Ctrl/Cmd + P | Quick open a file |
| Ctrl/Cmd + Shift + P | Command palette |
| Ctrl/Cmd + F | Find and replace |
| Ctrl + G | Go to line |
| Ctrl/Cmd + / | Toggle comment |
| Ctrl/Cmd + Enter | Run preview |
| Ctrl/Cmd + S | Save now |

The editor is [CodeMirror 5](https://codemirror.net/5/), loaded from the jsDelivr CDN along with [marked](https://marked.js.org/) for Markdown and [JSZip](https://stuk.github.io/jszip/) for ZIP files.
