# Personalised Intelligent Shell 🌟

![Version](https://img.shields.io/badge/version-0.2-blue) ![Status](https://img.shields.io/badge/status-Active_Development-green) ![AI-Powered](https://img.shields.io/badge/AI-Hybrid_Shell-purple)

## 📝 Description

The Personalised Intelligent Shell is a dynamic and AI-infused CLI (Command Line Interface) designed to merge the power of traditional shell scripting with enhanced AI-driven capabilities. This shell empowers users to interact seamlessly through natural language commands, deterministic rule-based workflows, robust session management, and customizable shortcuts.

---

## ✨ Features

### Core Capabilities:
1. **AI-Powered Command Interpretation**  
    Unleashes AI to:
    - Translate user instructions into executable commands.
    - Parse arguments using pre-trained language models seamlessly.
    - Produce deterministic and schema-valid results.

2. **Mode-Based Operation:**
    - **Rule Mode:** Traditional CLI logic, strict keyword mappings.
    - **AI Mode:** Combines reasoning and intent-matching for shell tasks.
    - **Chat Mode:** Provides assistance, explanations, and conversational engagement.

3. **Session Management**:
    - Context persistency with serialized session handling.
    - Tracks command execution, logs, and captures conversational turns.

4. **Safety & Reliability** 🎯:
    - Commands routed via strict confirmation gates.
    - Embedding models ensure intent disambiguation with explainable confidence scores.

5. **User-Extendable Registries**:
    - Register custom commands, applications, and shortcuts for immediate access.
    - Strong database constraints ensure integrity.

6. **System Versatility**:
    - Cross-platform compatibility (Windows, macOS, Linux).
    - Integrations for file manipulations, external tools, logs, and more.

---

## 📦 Requirements

Ensure the following dependencies are installed:

- Python 3.10+
- Modern pip (>=21.0)

Install required Python libraries:
```bash
pip install -r Requirements.txt
```

Download the fine-tuned model weights:
| **Model File**             | **Download Link**                                                                                  |
|----------------------------|---------------------------------------------------------------------------------------------------|
| Finetuned-gte-large-en-v1.5 | [📂 Download from Google Drive](https://drive.google.com/file/d/1tnAGQwr1tUUYgTLwp6oLiTOB8oqCXfd2/view?usp=sharing) |

Place the downloaded model file in the root directory (or reconfigure your model path).

---

## 🚀 Quickstart

1. Start the shell:
   ```bash
   python Core/CoreShell.py
   ```

2. Switch between operational modes:
   ```
   JaiShell [RULE] >> mode ai
   JaiShell [AI] >> mode chat
   ```

3. Use core commands such as:
   - `read myFile.txt`  
   - `summarize "This is a text to analyze!"`  
   - `weather "New York"`

Use the `help` command to view all available options.

### Key Modes:
| **Mode**       | **Description**                                                                 |
|----------------|---------------------------------------------------------------------------------|
| Rule Mode      | Executes deterministic commands with strict schema definitions.                 |
| AI Mode        | Enables natural language-driven command processing & automation.                |
| Chat Mode      | Conversational interface providing assistance, explanations, and no execution.  |

---

## 🛠 Command Highlights

| Command         | Description                                      | Example Command                       |
|------------------|--------------------------------------------------|---------------------------------------|
| **open**        | Opens a registry shortcut, URL, or folder        | `open myShortcut`                     |
| **register**    | Registers any shortcut (folder, app)             | `register myShortcut path/to/file`    |
| **read**        | Reads content from a file                        | `read notes.md`                       |
| **search**      | Web searches simplified                          | `search current innovations in AI`    |
| **weather**     | Checks the weather of any geographic location    | `weather Tokyo`                       |
| **summarize**   | Summarizes either text or file content            | `summarize sample.txt`                |

Check `help` for extended capabilities.

---

## 📋 Architecture Overview

1. **Command Pipeline and Registry:**
   - Based on `command_contract` for output structure enforcement.
   - Centralized function and action routing handled independently from execution.

2. **AI Execution Safety**:
   - Robust schema enforcement for argument validation.
   - Handles destructive actions with user confirmation built-in.

3. **Database Layer**:
   - SQLite-powered persistence of sessions, logs, and registry management.

4. **Embedding and Routing Models**:
   - `sentence-transformers` enable reliable semantic intent mapping.
   - Powered by the Groq LLM for secure external API calls.

5. **Session Awareness**:
   - Tracks historical turns, command invocations, and global statistics.

---

## 📚 Contribution Guidelines

Contributing to the project is simple:
- Clone the repository.
- Use feature branches for any changes.
- Commit responsibly following [GitHub best practices](https://docs.github.com/en/get-started/using-git).

---

## 👨‍💻 Author and Contact

**Jai Saraswat**  
- GitHub: [Jai-saraswat](https://github.com/Jai-saraswat)
- Email: jai.23gcebds005@galgotiacollege.edu

---

## ⚠️ Disclaimer

The "Personalised Intelligent Shell" is actively evolving. Expect breaking changes in beta versions. Always test thoroughly in individual sandbox environments before employing.
