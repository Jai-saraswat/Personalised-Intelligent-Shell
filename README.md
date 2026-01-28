# Personalised Intelligent Shell (JaiShell) 🌟

![Version](https://img.shields.io/badge/version-0.5-blue) ![Status](https://img.shields.io/badge/status-Active_Development-green) ![AI-Powered](https://img.shields.io/badge/AI-Hybrid_Shell-purple) ![Python](https://img.shields.io/badge/python-3.10+-blue)

## 📝 Overview

**JaiShell** (Personalised Intelligent Shell) is an advanced AI-powered command-line interface that seamlessly integrates traditional shell capabilities with cutting-edge natural language processing. Built on a fine-tuned sentence transformer model trained on 3000+ synthetically generated command descriptions, JaiShell provides intelligent command routing, semantic intent matching, and multi-modal interaction patterns.

### What Makes JaiShell Unique?
- 🧠 **Fine-tuned AI Model**: Custom-trained GTE-large-en-v1.5 model on 3000+ synthetic command descriptions for precise intent recognition
- 🎯 **Semantic Command Routing**: Vector embeddings enable natural language command execution with confidence scoring
- 🔄 **Three Operating Modes**: Rule-based, AI-assisted, and conversational chat modes
- 📊 **Complete Observability**: SQLite-backed session tracking, command logging, and analytics
- 🛡️ **Safety First**: Schema validation, confirmation gates, and explainable AI decisions

---

## 🏗️ Technical Architecture

### Core Components

```
┌───────────────────────────────────────────────────────────────┐
│                         CoreShell.py                           │
│            (Single Orchestrator • REPL • Logging)              │
│                                                               │
│  - Input loop                                                  │
│  - Mode switching                                              │
│  - Turn management                                             │
│  - Context lifecycle                                           │
│  - DB logging (sessions, turns, errors)                        │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌───────────────────────┐
                   │   ContextManager.py   │
                   │  (In-Memory State)    │
                   │  • session_id         │
                   │  • turn_id            │
                   │  • mode               │
                   │  • memory / flags     │
                   └───────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────────┐
              │        MODE DISPATCH GATE          │
              │   (Exactly ONE path per turn)     │
              └───────────────────────────────────┘
                  │                │               │
                  ▼                ▼               ▼
┌────────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│        RULE MODE        │ │        AI MODE       │ │       CHAT MODE       │
│  (Deterministic Path)  │ │ (Intent-Driven Path) │ │ (Explain-Only Path)   │
│                        │ │                      │ │                      │
│ • shlex parsing        │ │ • natural language   │ │ • conversational     │
│ • FUNCTION_MAP lookup  │ │ • no syntax required │ │ • no execution       │
│ • direct execution     │ │                      │ │ • no DB writes       │
└─────────────┬──────────┘ └──────────┬───────────┘ └──────────┬───────────┘
              │                        │                         │
              │                        ▼                         │
              │        ┌────────────────────────────────┐       │
              │        │      Function_Router.py        │       │
              │        │  (AI-Mode ONLY)                │       │
              │        │                                │       │
              │        │ • Load command embeddings      │       │
              │        │ • Cosine similarity            │       │
              │        │ • Confidence + margin logic    │       │
              │        │ • AUTO / CONFIRM / REJECT      │       │
              │        └───────────────┬────────────────┘       │
              │                        │                         │
              │                        ▼                         │
              │        ┌────────────────────────────────┐       │
              │        │    groq_client / server_api    │       │
              │        │  (Argument Extraction ONLY)    │       │
              │        │                                │       │
              │        │ • Schema-guided JSON output    │       │
              │        │ • No execution                 │       │
              │        └───────────────┬────────────────┘       │
              │                        │                         │
              └──────────────┬─────────┴─────────┬─────────────┘
                             ▼                   ▼
              ┌──────────────────────────┐   ┌──────────────────────────┐
              │     Command Execution     │   │        ChatCore.py        │
              │ (External / General Cmds)│   │  (Read-Only Assistant)   │
              │                          │   │                          │
              │ • OS / API calls         │   │ • Sees full context      │
              │ • Server / GitHub / etc  │   │ • Explains               │
              │ • NO logging here        │   │ • NO execution           │
              └───────────────┬──────────┘   └───────────────┬──────────┘
                              │                              │
                              ▼                              ▼
                 ┌────────────────────────────────────────────────┐
                 │            command_result CONTRACT              │
                 │                                                │
                 │  status | message | data | confidence | effects │
                 └──────────────────────────┬─────────────────────┘
                                            ▼
                        ┌───────────────────────────────────┐
                        │        CoreShell OUTPUT + DB       │
                        │                                   │
                        │ • Render response                 │
                        │ • Log command execution           │
                        │ • Log conversation turn           │
                        │ • Persist context snapshot        │
                        └───────────────────────────────────┘

```

### Database Schema

JaiShell uses **SQLite** with WAL mode for ACID compliance:

- **sessions**: Shell lifecycle tracking
- **commands**: Authoritative command registry (source of truth)
- **command_embeddings**: 1024-dim vectors for semantic routing
- **command_executions**: Immutable execution history
- **ai_decisions**: Explainability layer with confidence scores
- **conversation_history**: Multi-turn conversation memory
- **registry**: User-defined shortcuts (apps, folders, URLs)
- **settings**: Global configuration store
- **errors**: Comprehensive error logging

### AI/ML Pipeline

1. **Model**: Fine-tuned `gte-large-en-v1.5` (1024-dimensional embeddings)
2. **Training Data**: 3000+ synthetically generated command descriptions
3. **Routing Thresholds**:
   - Auto-execute: ≥0.75 confidence
   - Confirm: ≥0.60 confidence
   - Reject: <0.60 or margin <0.08
4. **LLM Backend**: Groq API for argument parsing and chat interactions

---

## ✨ Features

### Multi-Modal Operation

| **Mode**       | **Description**                                                                 | **Use Case** |
|----------------|---------------------------------------------------------------------------------|--------------|
| **Rule Mode**  | Traditional keyword-based execution with strict schema validation              | Power users, scripts, deterministic workflows |
| **AI Mode**    | Natural language → command translation with semantic intent matching           | General usage, exploration, natural interaction |
| **Chat Mode**  | Conversational assistant (no command execution)                                | Help, explanations, troubleshooting |

### Core Capabilities

- ✅ **Semantic Command Routing**: Vector similarity search across command embeddings
- ✅ **Confidence-Based Execution**: Auto-execute high-confidence matches, confirm ambiguous ones
- ✅ **LLM Argument Extraction**: Schema-guided parameter parsing via Groq
- ✅ **Session Persistence**: Complete conversation and execution history
- ✅ **Registry System**: Custom shortcuts for applications, folders, and URLs
- ✅ **Safety Mechanisms**: Destructive command confirmation, schema validation
- ✅ **Analytics Dashboard**: Session stats, command frequency, error tracking
- ✅ **Cross-Platform**: Windows, macOS, Linux support

---

## 📦 Installation & Setup

### Prerequisites

- **Python**: 3.10 or higher
- **pip**: 21.0+
- **Git**: For cloning repository

### Step 1: Clone Repository

```bash
git clone https://github.com/Jai-saraswat/Personalised-Intelligent-Shell.git
cd Personalised-Intelligent-Shell
```

### Step 2: Install Dependencies

```bash
pip install -r Requirements.txt
```

**Key Dependencies:**
- `sentence-transformers` (≥2.6.0): Embedding generation
- `torch` (≥2.0.0): Neural network backend
- `groq` (≥0.5.0): LLM API client
- `scikit-learn`, `numpy`: Vector operations
- `rich`: Terminal formatting

### Step 3: Download Fine-Tuned Model

Download the custom fine-tuned embedding model:

| **Model**                   | **Download Link**                                                              | **Size** |
|-----------------------------|--------------------------------------------------------------------------------|----------|
| Finetuned-gte-large-en-v1.5 | [📂 Google Drive](https://drive.google.com/file/d/1zyB2SB-8NYZVzRwnV9pV083kpO-NrjNS/view?usp=sharing) | ~1.5 GB  |

**Extract the model to the root directory:**
```bash
# After downloading, extract to project root
unzip Finetuned-gte-large-en-v1.5.zip
# Should create: Personalised-Intelligent-Shell/Finetuned-gte-large-en-v1.5/
```

Alternatively, set `EMBEDDING_MODEL_PATH` environment variable to a custom location.

### Step 4: Initialize Database & Seed Commands

**CRITICAL**: Run these initialization steps in order **before first use**:

```bash
# 1. Create database schema (tables, indexes, constraints)
python Core/db_init.py

# 2. Seed command definitions into database
python Core/seed_commands.py

# 3. Generate and store command embeddings (vectorization)
python Core/db_vector_manager.py
```

**What each step does:**
- **db_init.py**: Creates SQLite database with 9 tables (sessions, commands, embeddings, etc.)
- **seed_commands.py**: Populates `commands` table with 19 predefined commands
- **db_vector_manager.py**: Generates 1024-dim embeddings for all commands using fine-tuned model

⚠️ **Important**: Re-run `db_vector_manager.py` whenever you:
- Add new commands via `seed_commands.py`
- Change command descriptions
- Update the embedding model

### Step 5: Configure Environment (Optional)

Create a `.env` file for API keys and settings:

```bash
# Groq API for LLM interactions (required for AI/Chat modes)
GROQ_API_KEY=your_groq_api_key_here

# Optional: Custom model path
EMBEDDING_MODEL_PATH=/path/to/custom/model

# Optional: User name for shell prompt
USER_NAME=YourName
```

Get your Groq API key at: https://console.groq.com/

---

## 🚀 Usage

### Starting the Shell

```bash
python Core/CoreShell.py
```

You'll see:
```
Initializing core systems...
Database schema ready.
Welcome, user.
JaiShell is online.
Type 'help' to see available commands.

JaiShell [RULE] ▸
```

### Mode Switching

```bash
# Switch to AI mode (natural language)
JaiShell [RULE] ▸ mode ai
Switched to AI mode.

# Switch to Chat mode (conversational, no execution)
JaiShell [AI] ▸ mode chat
Switched to Chat mode.

# Return to Rule mode
JaiShell [CHAT] ▸ mode rule
Switched to Rule mode.
```

### Example Commands

#### Rule Mode (Direct Execution)
```bash
JaiShell [RULE] ▸ weather Tokyo
🌤️ Current weather in Tokyo: 15°C, Clear sky

JaiShell [RULE] ▸ register vscode "C:\Program Files\Microsoft VS Code\Code.exe" program
✅ Registered shortcut: vscode

JaiShell [RULE] ▸ open vscode
Opening: vscode
```

#### AI Mode (Natural Language)
```bash
JaiShell [AI] ▸ what's the weather like in New York?
🌧️ Current weather in New York: 8°C, Light rain

JaiShell [AI] ▸ show me my GitHub repositories
📦 Your GitHub Repositories:
1. Project-Alpha (⭐ 45)
2. Personal-Website (⭐ 12)
...

JaiShell [AI] ▸ summarize the file at ~/notes/meeting.txt
📝 Summary: The meeting covered Q4 roadmap...
```

#### Chat Mode (No Execution)
```bash
JaiShell [CHAT] ▸ how do I register a new shortcut?
To register a shortcut, use the 'register' command:
register <name> <path> [type]
Example: register myapp "C:\Apps\myapp.exe" program
```

---

## 🛠️ Available Commands

### System & Registry
| Command | Arguments | Description | Example |
|---------|-----------|-------------|---------|
| `open` | `<name>` | Open registered shortcut | `open firefox` |
| `register` | `<name> <path> [type]` | Register new shortcut | `register docs ~/Documents folder` |

### Information & Monitoring
| Command | Arguments | Description | Example |
|---------|-----------|-------------|---------|
| `weather` | `<city>` | Get weather information | `weather London` |
| `news` | - | Fetch latest headlines | `news` |
| `system-specs` | - | Display system info | `system-specs` |
| `system-uptime` | - | Show uptime | `system-uptime` |
| `wifi-status` | - | Current WiFi network | `wifi-status` |

### Server Management (Custom)
| Command | Arguments | Description | Example |
|---------|-----------|-------------|---------|
| `server-state` | - | Check server reachability | `server-state` |
| `server-health` | - | CPU, RAM, GPU, temp stats | `server-health` |
| `server-last-boot` | - | Last boot timestamp | `server-last-boot` |
| `server-ssh` | - | Open admin PowerShell | `server-ssh` |
| `nextcloud-status` | - | Check Nextcloud service | `nextcloud-status` |

### GitHub Integration
| Command | Arguments | Description | Example |
|---------|-----------|-------------|---------|
| `github-repos` | - | List your repositories | `github-repos` |
| `github-repo-summary` | `<repo>` | Repository overview | `github-repo-summary my-project` |
| `github-recent-commits` | `<repo>` | Recent commit history | `github-recent-commits my-project` |
| `github-repo-activity` | `<repo>` | Activity metrics | `github-repo-activity my-project` |
| `github-languages` | `<repo>` | Language breakdown | `github-languages my-project` |

### AI & Analytics
| Command | Arguments | Description | Example |
|---------|-----------|-------------|---------|
| `summarize` | `<file_path>` | AI-powered file summarization | `summarize notes.txt` |
| `analytics` | - | Shell usage analytics | `analytics` |

### Shell Control
| Command | Arguments | Description | Example |
|---------|-----------|-------------|---------|
| `help` | - | Show available commands | `help` |
| `status` | - | Current session info | `status` |
| `history` | - | Command history | `history` |
| `logs` | - | View error logs | `logs` |
| `clear` | - | Clear screen | `clear` |
| `exit` / `quit` | - | Close shell | `exit` |

---

## 📚 Technical Details

### Command Routing Algorithm

1. **User Input** → Tokenization and preprocessing
2. **Embedding Generation** → Convert to 1024-dim vector (normalized)
3. **Similarity Search** → Cosine similarity against all command embeddings
4. **Confidence Scoring** → Top match score and margin calculation
5. **Decision Logic**:
   - Score ≥0.75: Auto-execute
   - 0.60 ≤ Score <0.75: Request confirmation
   - Score <0.60 or margin <0.08: Reject (ambiguous)
6. **Argument Extraction** → Groq LLM parses schema-compliant arguments
7. **Validation** → Schema enforcement (type, required fields)
8. **Execution** → Call registered function
9. **Logging** → Record in database (execution, decision, conversation)

### Model Training Details

- **Base Model**: Alibaba-NLP/gte-large-en-v1.5
- **Fine-tuning Dataset**: 3000+ synthetically generated command descriptions
- **Training Method**: Contrastive learning with hard negatives
- **Output Dimension**: 1024
- **Normalization**: L2 normalized embeddings
- **Purpose**: Specialized for shell command intent recognition

### Safety Features

1. **Schema Validation**: All arguments validated against JSON schemas
2. **Destructive Command Flags**: Commands marked as destructive require confirmation
3. **Confidence Thresholds**: Low-confidence matches rejected
4. **Margin Enforcement**: Similar commands trigger disambiguation
5. **Explainability**: All AI decisions logged with reasoning
6. **Session Isolation**: Each session has independent context

---

## 🔧 Advanced Configuration

### Custom Commands

Add custom commands by editing `Core/seed_commands.py`:

```python
{
    "command_name": "my-command",
    "category": "custom.tools",
    "description": "Description for semantic matching",
    "schema": {
        "arg1": {"type": "string", "required": True},
        "arg2": {"type": "integer", "required": False}
    },
    "is_destructive": 0,
    "requires_confirmation": 0,
}
```

Then:
1. Implement function in `External_Commands/commands.py`
2. Register in `FUNCTION_MAP` (CoreShell.py) and `COMMAND_REGISTRY` (AICore.py)
3. Re-run: `python Core/seed_commands.py && python Core/db_vector_manager.py`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMBEDDING_MODEL_PATH` | Path to fine-tuned model | `./Finetuned-gte-large-en-v1.5` |
| `GROQ_API_KEY` | Groq API key for LLM | Required for AI/Chat |
| `USER_NAME` | Display name in prompt | `user` |
| `DB_PATH` | SQLite database location | `./jaishell.db` |

---

## 🐛 Troubleshooting

### Common Issues

**"Embedding model not found"**
```bash
# Ensure model is extracted to correct location
ls -la Finetuned-gte-large-en-v1.5/
# Should contain: config.json, model files, tokenizer files

# Or set custom path
export EMBEDDING_MODEL_PATH=/path/to/model
```

**"No commands found" when running db_vector_manager.py**
```bash
# Ensure you ran seed_commands.py first
python Core/seed_commands.py
python Core/db_vector_manager.py
```

**AI/Chat mode not working**
```bash
# Ensure GROQ_API_KEY is set in .env file
echo "GROQ_API_KEY=your_key_here" > .env
```

**"Unknown command" in Rule mode**
```bash
# Use 'help' to see available commands
# Or switch to AI mode for natural language
mode ai
```

---

## 📊 Analytics & Monitoring

View shell usage statistics:

```bash
JaiShell [RULE] ▸ analytics

📊 Shell Analytics Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Total Sessions: 47
⚡ Commands Executed: 1,203
❌ Total Errors: 12
📈 Success Rate: 99.0%
🔥 Most Used: weather (87 times)
```

Database location: `./jaishell.db` (can be queried with any SQLite client)

---

## 🗺️ Roadmap

### Version 0.5 (Current)
- ✅ Fine-tuned model on 3000+ synthetic descriptions
- ✅ Refactored function routing architecture
- ✅ Enhanced database schema with embeddings table
- ✅ Comprehensive session and conversation tracking

### Version 0.6 (Planned)
- 🔄 Plugin system for community extensions
- 🔄 Multi-language support (embeddings)
- 🔄 Real-time command suggestions
- 🔄 Web-based dashboard for analytics

### Version 1.0 (Future)
- 🔮 Local LLM support (Ollama, llama.cpp)
- 🔮 Multi-agent workflows
- 🔮 Voice command integration
- 🔮 Cloud sync for registry and history

---

## 📚 Contribution Guidelines

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/Personalised-Intelligent-Shell.git
cd Personalised-Intelligent-Shell

# Create feature branch
git checkout -b feature/your-feature-name

# Install dev dependencies
pip install -r Requirements.txt

# Initialize database for testing
python Core/db_init.py
python Core/seed_commands.py
python Core/db_vector_manager.py
```

### Contribution Workflow

1. **Create an Issue**: Describe the bug or feature
2. **Fork & Branch**: Create a feature branch
3. **Implement**: Follow existing code style
4. **Test**: Ensure all modes work correctly
5. **Document**: Update README if adding features
6. **Pull Request**: Reference the issue number

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings for functions
- Comment complex logic
- Keep functions focused and small

### Testing Your Changes

```bash
# Start the shell
python Core/CoreShell.py

# Test all three modes
mode rule   # Test direct commands
mode ai     # Test natural language
mode chat   # Test conversational mode

# Verify database integrity
sqlite3 jaishell.db "PRAGMA integrity_check;"
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author & Contact

**Jai Saraswat**  
- 🐙 GitHub: [@Jai-saraswat](https://github.com/Jai-saraswat)
- 📧 Email: saraswatjai1409@gmail.com
- 💼 LinkedIn: [Connect on LinkedIn](https://www.linkedin.com/in/jai-saraswat-877809284/)

---

## 🙏 Acknowledgments

- **Alibaba-NLP** for the base GTE-large-en-v1.5 model
- **Groq** for providing fast LLM inference
- **sentence-transformers** community for excellent embedding tools
- All contributors and users of JaiShell

---

## ⚠️ Disclaimer

**JaiShell v0.5** is under active development. This is beta software:

- ⚠️ Expect breaking changes between versions
- ⚠️ Always test in a safe environment first
- ⚠️ Back up important data before using destructive commands
- ⚠️ Review generated commands before execution
- ⚠️ API keys should be kept secure and never committed to version control

**Use at your own risk. The authors are not responsible for any damage or data loss.**

---

## 📖 Citation

If you use JaiShell in your research or project, please cite:

```bibtex
@software{jaishell2026,
  author = {Saraswat, Jai},
  title = {JaiShell: Personalised Intelligent Shell},
  year = {2026},
  version = {0.5},
  url = {https://github.com/Jai-saraswat/Personalised-Intelligent-Shell}
}
```

---

<div align="center">

**[⭐ Star this repository](https://github.com/Jai-saraswat/Personalised-Intelligent-Shell)** if you find it useful!

Made with ❤️ and 🤖 by [Jai Saraswat](https://github.com/Jai-saraswat)

</div>
