# Personalised Intelligent Shell 🌟

![Version](https://img.shields.io/badge/version-0.2-blue) ![Status](https://img.shields.io/badge/status-Active_Development-green) ![AI-Powered](https://img.shields.io/badge/AI-Hybrid_Shell-purple)

## 📝 Description

Personalised Intelligent Shell is a **state-of-the-art configurable shell interface** that combines the strengths of traditional command-line interfaces with the power of **AI-driven intent understanding**. It is tailored for advanced developers and automation engineers who value precision and safety while leveraging AI capabilities to simplify complex workflows.

Gone are the days of typing long and confusing command sequences! With **natural language understanding**, the shell empowers users to interact using plain text while ensuring **deterministic execution pathways** for safety and compliance. 

---

## ✨ Features

### Core Objectives:
1. **AI-Powered Natural Language Commands**  
    - Translate human-like instructions directly into executable shell commands.
    - Example: `"Check the weather in New York"` or `"Download this file (URL)"`.

2. **Rule-Based Deterministic Mode**  
    - Offers a traditional shell with strict keyword-based mappings for system commands.
    - No AI involved—making it safe, predictable, and efficient for automation.

3. **Session Persistence**  
    - Logs session history, captures executed commands, errors, and offers full traceability.

4. **Safety First** 🎯
    - Ensures clear segregation between reasoning and execution to prevent unwanted or hallucinated outputs.
    - Commands execute deterministically through strict schemas and AI pipelines.

5. **Customizable Commands**  
    - Easily register applications, folders, and shortcuts for rapid tasks.
    - Includes extensible options to adjust behavior according to needs.

---

## 💡 Usage

### Running the Shell

To run the shell locally, follow these steps:

1. **Install Dependencies:**
   ```bash
   pip install -r Requirements.txt
   ```

2. **Start the Shell:**
   ```bash
   python Core/CoreShell.py
   ```

3. **Modes of Operation:**
   - **Rule Mode:**  
     Use direct system-like commands (e.g., `open chrome`, `clean temp`, `read file.txt`).
   - **AI Mode:**  
     Utilize natural language for tasks (e.g., `"Summarize this document"`, `"Search for the latest news"`).

### Core Commands

| **Command**    | **Functionality**                           | **Example**                         |
|----------------|-------------------------------------------|-------------------------------------|
| `open`         | Open registered applications, folders, or URLs | `open chrome`                      |
| `clean`        | Clean temporary files or folder paths.     | `clean temp`                       |
| `read`         | Read local files from a given directory.   | `read notes.txt`                   |
| `weather`      | Retrieve the latest weather updates.       | `weather New York`                 |
| `summarize`    | Summarize text or the contents of a file.  | `summarize report.txt`             |

For a detailed list of commands, switch to **help mode** and type:
```bash
help
```
---

## 📥 Model Weights (Required)

To run the AI Mode effectively, you must download the fine-tuned embedding model:

| Model Name                | Download Link                                                                                      |
|---------------------------|---------------------------------------------------------------------------------------------------|
| **Finetuned-gte-large-en-v1.5** | [📂 Download from Google Drive](https://drive.google.com/file/d/1tnAGQwr1tUUYgTLwp6oLiTOB8oqCXfd2/view?usp=sharing) |

> Place the downloaded model file in the root directory or update your configuration.

---

---

## 📋 Architecture

### How It Works:
1. **Rule-Based Deterministic Workflow:**  
    - Executes commands through predefined mappings directly.
    - Ensures full control by skipping AI interpretation.

2. **AI-Powered Execution Pipeline:**
    - **Intent Identification:** Classifies the user's input based on their intent.
    - **Argument Parsing + Validation:** Extracts arguments securely without assumptions.
    - **Safe Execution:** Executes commands only if verified against pre-defined schemas.

---

## 🚀 Roadmap and Milestones 🛣️

### Future Enhancements:
- **Improved Intent Prediction**:
    - Advanced classification mechanisms for distinguishing chat, execution, and hybrid interactions.
  
- **API Integrations:**
    - Extend native support to integrate external APIs such as:
      - **News Feeds** 📰 
      - **Stock Market Data** 📈
      - **System Health Monitoring** ⚙️

- **Regex-Based Argument Validation:**
    - Speedier and more precise argument parsing mechanisms.

- **Advanced Context Retention:**
    - Leverage prior session memory for richer interactions and context-aware recommendations.

---

## 📌 Version & Author

**Version:** `0.2`  
**Author:** Jai Saraswat  
[GitHub Profile](https://github.com/Jai-saraswat)

---

## 👥 Audience

This project is ideal for:
- **Automation Engineers** looking to simplify workflows.
- **Developers** leveraging AI for better command orchestration.
- **ML Enthusiasts** eager to explore integrations of rule-based and AI approaches for CLI interfaces.
- **Security-Focused Teams** needing controlled automation tools.

Feel free to contribute, raise issues, or share feedback!
