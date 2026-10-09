# Pocket Code

A VS Code style code editor for phones. It runs in any mobile browser, and there is an Android app (APK) too.

Pocket Code copies VS Code's layout and its Dark Modern, Light Modern, Dark+ and Light+ themes. It is its own small app built on [CodeMirror 5](https://codemirror.net/5/), not Microsoft's VS Code, and isn't affiliated with Microsoft.

## Install on Android

1. Download [`android/dist/PocketCode.apk`](android/dist/PocketCode.apk) on your phone.
2. Open it. If Android asks, allow your browser or file app to install unknown apps.
3. Open **Pocket Code** from your app drawer.

The app works offline. Your files stay on the phone.

## Use it in a browser

Host the `pocket_code` folder anywhere that serves static files, for example GitHub Pages:

1. On GitHub, open the repository's **Settings**, then **Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**, pick the branch and `/ (root)`.
3. Open `https://<your-username>.github.io/<repo>/pocket_code/` on your phone.
4. Use your browser's **Add to Home Screen** so it opens like an app.

## What's inside

- **Workbench**: title bar with the command center, activity bar, side bar, editor tabs with breadcrumbs, bottom panel and status bar, laid out like VS Code.
- **Explorer**: Open Editors and a folder tree with indent guides. Create, rename and move files inline. Long-press a file, folder or tab for its context menu.
- **Editor**: syntax colors that match VS Code for HTML, CSS, JavaScript, TypeScript, JSON, Python, Markdown, C, C++, Java, C#, Kotlin, Shell, SQL, YAML, XML and Jinja. Bracket pair colors, auto-closing brackets and tags, and the current line highlight.
- **Command center**: type a file name, `>` for commands, `:` to go to a line, `@` to go to a symbol, `?` for help.
- **Find and replace** widget with match case, whole word and regex options. **Search** across all files with replace.
- **Problems**: JavaScript and JSON syntax errors are underlined in red and listed in the Problems panel.
- **Run and Debug**: preview HTML pages in an editor tab. Linked `.css` and `.js` files are pulled in. Markdown renders as a page.
- **Debug Console**: shows `console.log` output and errors from the preview and evaluates JavaScript in it.
- **Terminal**: a small built-in shell with `ls`, `cd`, `cat`, `touch`, `mkdir`, `rm`, `mv`, `cp`, `echo`, `tree`, `code` and `node file.js`. It is not a full system terminal.
- **Settings** editor, Welcome page, application menu (File, Edit, Selection, View, Go, Run, Terminal, Help) and notifications.
- **Key row** above the on-screen keyboard with Tab, arrows, brackets, symbols, undo and redo.
- **Import** files or a ZIP and **Export** the project as a ZIP.

Python files get syntax colors but can't run.

Files save automatically in the browser's local storage, or inside the app on Android. They are not synced anywhere, so export a ZIP now and then as a backup.

## Keyboard shortcuts

These work with a hardware keyboard and match VS Code.

| Keys | Action |
| --- | --- |
| Ctrl+P | Go to file |
| Ctrl+Shift+P or F1 | Command palette |
| Ctrl+Shift+F | Search across files |
| Ctrl+B | Toggle side bar |
| Ctrl+J | Toggle panel |
| Ctrl+` | Toggle terminal |
| F5 | Run |
| Ctrl+F / Ctrl+H | Find / Replace |
| Ctrl+G | Go to line |
| Ctrl+Shift+O | Go to symbol |
| Ctrl+/ | Toggle line comment |
| Alt+Up / Alt+Down | Move line |
| Shift+Alt+Down | Copy line down |
| Ctrl+Shift+K | Delete line |
| F8 | Next problem |
| Ctrl+K Ctrl+T | Color theme |

On a Mac keyboard, use Cmd in place of Ctrl.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | The whole editor: layout, styles and script |
| `manifest.webmanifest`, `sw.js`, `icon.svg` | Home-screen install and offline support in browsers |
| `android/` | Android app wrapper and its build script |
| `android/dist/PocketCode.apk` | Ready-to-install Android app |
| `tools/embed_icons.py` | Rebuilds the embedded icon font after adding icons |

## Rebuild the Android app

You need Java 17 or newer, Python 3, npm and the Android SDK with `platforms;android-34` and `build-tools;34.0.0`.

```bash
cd pocket_code/android
ANDROID_HOME=/path/to/android-sdk ./build.sh
```

The script bundles the editor and its libraries for offline use, compiles the app and signs it. The APK lands in `android/build/PocketCode.apk`. It creates a signing key at `~/.pocketcode/release.jks` on first run. Keep that file, because Android only installs updates signed with the same key.

## Credits

- [CodeMirror 5](https://codemirror.net/5/) (MIT) for the editor.
- [Codicons](https://github.com/microsoft/vscode-codicons) by Microsoft (CC BY 4.0) for the icons.
- [Acorn](https://github.com/acornjs/acorn) (MIT) for JavaScript syntax checks.
- [marked](https://marked.js.org/) (MIT) for Markdown previews.
- [JSZip](https://stuk.github.io/jszip/) (MIT) for ZIP import and export.
