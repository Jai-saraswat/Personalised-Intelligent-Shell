# Personalised Intelligent Shell

![Version](https://img.shields.io/badge/version-1.0-blue) ![Status](https://img.shields.io/badge/status-Stable-green) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![AI](https://img.shields.io/badge/AI-Hybrid_Shell-purple)

**Version 1.0 - Stable Release**

---

## Project Overview

**Personalised Intelligent Shell** is a production-grade command-line interface that integrates deterministic shell execution with AI-powered natural language processing. Built on a fine-tuned sentence transformer model and designed with execution safety as a core principle, this system provides three distinct operational modes: rule-based command execution, AI-assisted semantic routing, and conversational assistance.

The shell addresses the fundamental challenge of bridging traditional command-line precision with natural language flexibility while maintaining strict execution boundaries, full observability, and explainability at every layer.

### What Problem Does It Solve?

Traditional shells require exact syntax and memorization of command structures. Conversational AI assistants lack execution boundaries and provenance tracking. This system provides:

- **Semantic command routing** using vector similarity search
- **Execution-safe AI orchestration** with strict confirmation gates
- **Full session persistence** with immutable execution history
- **Deterministic fallback** to rule-based execution when needed
- **Explainability-first design** with confidence scoring and decision logging

### High-Level Capabilities

- Multi-mode architecture supporting rule-based, AI-assisted, and chat-only interactions
- Natural language to command translation via fine-tuned embeddings (1024-dimensional vectors)
- LLM-powered argument extraction with schema validation
- Comprehensive session tracking across all modes
- SQLite-backed persistence with ACID compliance
- Registry system for custom shortcuts and workflows
- Cross-platform support (Windows, macOS, Linux)

---

## Core Features (v1.0)

### Multi-Mode Shell Architecture

**RULE Mode**: Traditional keyword-based execution with direct function mapping. Provides deterministic behavior with exact syntax requirements.

**AI Mode**: Natural language command interpretation using semantic embeddings. Automatically routes user intent to appropriate commands with confidence-based execution gates.

**CHAT Mode**: Conversational assistant mode with strict non-execution boundaries. Provides explanations, help, and context-aware responses based on full session history.

### AI-Powered Semantic Command Routing

- Fine-tuned GTE-large-en-v1.5 model trained on 3000+ synthetic command descriptions
- 1024-dimensional vector embeddings for semantic similarity matching
- Cosine similarity search with confidence thresholds:
  - Auto-execute: ≥0.75 confidence
  - Confirm: ≥0.60 confidence  
  - Reject: <0.60 or margin <0.08 between top candidates

### Execution-Safe AI Orchestration

- **Schema validation**: All arguments validated against JSON schemas before execution
- **Confirmation gates**: Ambiguous or destructive commands require user approval
- **No hallucinated execution**: AI layer never simulates command outputs
- **Strict mode boundaries**: CHAT mode cannot execute commands
- **Immutable logging**: All executions logged with provenance tracking

### LLM-Powered Conversational Mode

- Full session awareness spanning RULE, AI, and CHAT modes
- Execution-aware context: ChatCore sees real past command outputs
- Groq API backend for fast inference
- Temperature-controlled responses (0.2) for technical accuracy
- Historical context window (12 turns) for conversation continuity

### Full Session Persistence

- Session lifecycle tracking from initialization to termination
- Turn-by-turn conversation history with mode tagging
- Command execution logs with timestamps and status codes
- AI decision logging with confidence scores and reasoning
- Error tracking with function-level attribution

### Execution-Aware Conversational Memory

- ChatCore has read-only access to complete session history
- Distinguishes between RULE-mode executions and AI-mode executions
- Never claims credit for system executions
- Explains past results based on logged outputs, not inference
- Maintains strict boundaries between explanation and execution

### Strict Separation of Execution vs Explanation

- RULE mode: Direct execution, no AI involvement
- AI mode: Semantic routing + LLM argument extraction, then execution
- CHAT mode: Explanation only, zero execution capability
- Clear labeling of which mode executed each command
- Conversation history preserves execution provenance

### Deterministic + AI Hybrid Design

- Rule mode provides fallback for exact command needs
- AI mode uses deterministic routing thresholds, not probabilistic execution
- Confidence scores guide automation vs human-in-the-loop
- Schema validation ensures type safety regardless of mode
- Command registry serves as single source of truth

---

## Architecture Overview

The system is structured as a layered architecture with clear separation of concerns and unidirectional data flow.

### Component Responsibilities

**CoreShell**: Central orchestrator managing the REPL loop, mode switching, turn management, context lifecycle, and database logging. Acts as the single entry point coordinating all subsystems.

**ContextManager**: In-memory state manager tracking session_id, turn_id, current mode, and conversation memory. Provides context serialization for persistence.

**AICore**: AI-mode orchestration layer responsible for routing user intent via Function_Router, extracting arguments via LLM, executing registered commands, and enforcing safety boundaries.

**ChatCore**: Conversational assistant with read-only access to full session history. Explains system behavior, answers questions about past executions, and maintains strict non-execution boundaries.

**Function_Router**: Semantic intent router loading command embeddings, computing cosine similarity, applying confidence thresholds, and producing routing decisions with explainability.

**Database (SQLite)**: Persistence layer with 9 tables tracking sessions, commands, embeddings, executions, AI decisions, conversations, errors, registry, and settings. Provides ACID guarantees and foreign key enforcement.

**Command Registry**: Authoritative source of truth defining all valid commands with schemas, categories, descriptions, and safety flags. Populated via seed_commands.py and vectorized via db_vector_manager.py.

### Execution Provenance and Safety

Every command execution is logged with:
- Raw user input (exact text entered)
- Resolved command_id (which command was matched)
- Execution status (success/failure)
- Mode used (RULE/AI/CHAT)
- Function called (actual Python function invoked)
- Timestamp (ISO 8601 format)

AI decisions are separately logged with:
- Chosen command and confidence score
- Decision type (AUTO/CONFIRM/REJECT)
- Reasoning text
- All top candidates with scores

This dual-logging ensures full explainability and audit trails.

---

## Architectural Diagrams

### Overall System Architecture

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
│ • direct execution     │ │                      │ │ • history-aware      │
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
              │ • Registry operations    │   │ • NO execution           │
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
### Request Flow Per Mode

```
┌─────────────────────────────────────────────────────────────────────┐
│                      USER INPUT: "show me weather"                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                ┌──────────────────┴───────────────────┐
                │      CoreShell REPL Loop             │
                │   - Increment turn_id                │
                │   - Check mode flag in context       │
                └──────────────────┬───────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│   RULE MODE    │     │     AI MODE       │     │    CHAT MODE     │
└────────────────┘     └───────────────────┘     └──────────────────┘
         │                         │                         │
         │                         │                         │
         ▼                         ▼                         ▼
┌────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ shlex.split()  │     │ Function_Router   │     │ ChatCore Engine  │
│ FUNCTION_MAP   │     │ - Load embeddings │     │ - Get history    │
│ Direct call    │     │ - route_command() │     │ - Build messages │
└─────────┬──────┘     └─────────┬─────────┘     │ - Groq API call  │
         │                       │                 └─────────┬────────┘
         │                       ▼                           │
         │             ┌─────────────────────┐              │
         │             │ get_function_schema │              │
         │             │ extract_arguments   │              │
         │             │ (LLM → JSON)        │              │
         │             └─────────┬───────────┘              │
         │                       │                          │
         │                       ▼                          │
         │             ┌─────────────────────┐              │
         │             │ execute_command()   │              │
         │             │ (COMMAND_REGISTRY)  │              │
         │             └─────────┬───────────┘              │
         │                       │                          │
         └───────────────────────┴──────────────────────────┘
                                 │
                                 ▼
                ┌──────────────────────────────────┐
                │      command_result CONTRACT      │
                │  {status, message, data, ...}    │
                └──────────────────┬───────────────┘
                                   │
                                   ▼
                ┌──────────────────────────────────┐
                │     CoreShell OUTPUT + LOGGING    │
                │  - print_response()              │
                │  - log_command_execution()       │
                │  - log_conversation_turn()       │
                └──────────────────────────────────┘
```

### AI Command Execution Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  USER INPUT: "what's the weather like in San Francisco?"    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      AICore.ai_engine()      │
              │  Entry point for AI mode     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  Function_Router             │
              │  • Load command embeddings   │
              │  • Encode user query         │
              │  • Compute cosine similarity │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Confidence Thresholds      │
              │  ≥ 0.75 → AUTO_EXECUTE       │
              │  ≥ 0.60 → CONFIRM            │
              │  < 0.60 → REJECT             │
              └──────────────┬───────────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
         ┌─────────────────┐   ┌──────────────┐
         │     REJECT      │   │ AUTO/CONFIRM │
         │  Return error   │   │  Proceed     │
         └─────────────────┘   └──────┬───────┘
                                      │
                                      ▼
                     ┌─────────────────────────────┐
                     │  get_function_schema()      │
                     │  • Load from commands table │
                     │  • Get schema_json          │
                     │  • Get command_name         │
                     └─────────┬───────────────────┘
                               │
                               ▼
                     ┌─────────────────────────────┐
                     │ extract_arguments()         │
                     │ (Groq LLM)                  │
                     │                             │
                     │ Input: prompt + schema      │
                     │ Output: {arg1: val1, ...}   │
                     └─────────┬───────────────────┘
                               │
                               ▼
                     ┌─────────────────────────────┐
                     │  Normalize to CLI format    │
                     │  Convert dict → List[str]   │
                     └─────────┬───────────────────┘
                               │
                               ▼
                     ┌─────────────────────────────┐
                     │  execute_command()          │
                     │  • Lookup COMMAND_REGISTRY  │
                     │  • Call function(args, ctx) │
                     │  • Catch exceptions         │
                     └─────────┬───────────────────┘
                               │
                               ▼
                     ┌─────────────────────────────┐
                     │   command_result            │
                     │   + confidence score        │
                     └─────────────────────────────┘
```

### Chat Mode History + Context Flow

```
┌────────────────────────────────────────────────────────┐
│  USER: "summarize what I've done this session"         │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │   ChatCore.chat_engine()           │
         │   • Validate input                 │
         │   • Extract context (session_id)   │
         └────────────────┬───────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │  get_conversation_history()        │
         │  (Database Query)                  │
         │                                    │
         │  SELECT * FROM conversation_history│
         │  WHERE session_id = ?              │
         │  ORDER BY turn_id DESC             │
         │  LIMIT 12                          │
         └────────────────┬───────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │  Build LLM message array           │
         │                                    │
         │  [0] system: SYSTEM_PROMPT         │
         │  [1..N] history messages           │
         │      - CHAT turns → user/assistant │
         │      - RULE/AI executions →        │
         │        system message with:        │
         │          • Mode                    │
         │          • User input              │
         │          • Command called          │
         │          • Status                  │
         │          • Output (verbatim)       │
         │  [N+1] user: current prompt        │
         └────────────────┬───────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │   groq_client.chat_complete()      │
         │   • Model: llama3-8b-8192          │
         │   • Temperature: 0.2               │
         │   • Max tokens: 800                │
         └────────────────┬───────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │  command_result                    │
         │  {                                 │
         │    status: "success",              │
         │    message: <LLM response>,        │
         │    confidence: 0.85                │
         │  }                                 │
         └────────────────────────────────────┘
```

### Database Schema Relationships

```
┌─────────────────┐
│    sessions     │◄────────────────────┐
│─────────────────│                     │
│ session_id (PK) │                     │
│ start_timestamp │                     │
│ end_timestamp   │                     │
└─────────────────┘                     │
         ▲                              │
         │                              │
         │ FK                           │ FK
         │                              │
┌────────┴────────────┐      ┌──────────┴────────────┐
│ command_executions  │      │ conversation_history  │
│─────────────────────│      │───────────────────────│
│ execution_id (PK)   │      │ id (PK)               │
│ session_id (FK)     │      │ session_id (FK)       │
│ raw_input           │      │ turn_id               │
│ command_id (FK)     │      │ mode                  │
│ status              │      │ user_input            │
│ mode                │      │ assistant_output      │
│ function_called     │      │ command_called        │
│ timestamp           │      │ status                │
└─────────┬───────────┘      │ confidence            │
          │                  │ context_snapshot      │
          │                  │ timestamp             │
          │                  └───────────────────────┘
          │ FK
          │
          ▼
┌─────────────────┐
│    commands     │◄─────────────────┐
│─────────────────│                  │
│ command_id (PK) │                  │
│ command_name    │                  │ FK
│ category        │                  │
│ description     │         ┌────────┴────────┐
│ schema_json     │         │  ai_decisions   │
│ is_destructive  │         │─────────────────│
│ requires_conf.. │         │ decision_id (PK)│
└────────┬────────┘         │ session_id (FK) │
         │                  │ raw_input       │
         │ FK (1:1)         │ chosen_cmd.. FK │
         ▼                  │ confidence      │
┌─────────────────┐         │ decision_type   │
│command_embeddings│        │ reason          │
│─────────────────│         │ timestamp       │
│ command_id (PK) │         └─────────────────┘
│ embedding_json  │
└─────────────────┘         ┌─────────────────┐
                            │     errors      │
┌─────────────────┐         │─────────────────│
│    registry     │         │ error_id (PK)   │
│─────────────────│         │ session_id (FK) │
│ name (PK)       │         │ error_name      │
│ path            │         │ error_descrip.. │
│ type            │         │ origin_function │
└─────────────────┘         │ timestamp       │
                            └─────────────────┘
┌─────────────────┐
│    settings     │
│─────────────────│
│ key (PK)        │
│ value           │
└─────────────────┘
```

---

## Execution Modes Explained

### RULE Mode

**What It Does**

RULE mode provides deterministic, keyword-based command execution identical to traditional Unix shells. User input is tokenized using `shlex`, the first token is matched against `FUNCTION_MAP`, and the corresponding Python function is invoked directly with remaining tokens as arguments.

**What It Is Allowed To Do**

- Parse user input as space-separated tokens
- Look up commands in the static `FUNCTION_MAP` dictionary
- Execute registered functions with provided arguments
- Return results via the standardized `command_result` contract
- Log all executions to `command_executions` table

**What It Is NOT Allowed To Do**

- Interpret natural language or handle semantic variations
- Use AI models for routing or argument extraction
- Execute commands not explicitly defined in `FUNCTION_MAP`
- Modify database schema or settings without explicit commands
- Access external APIs without corresponding registered commands

**History and Context Interaction**

All RULE mode executions are logged with:
- Raw input text
- Resolved command ID (if matched to database)
- Execution status (success/error)
- Function name invoked
- Timestamp

These logs populate `conversation_history` with `mode="rule"` and are visible to ChatCore when operating in CHAT mode. ChatCore references these as factual execution records, not inferences.

**Use Cases**

- Users who prefer exact syntax and predictable behavior
- Scripting and automation requiring deterministic outcomes
- Fallback when AI mode produces ambiguous or incorrect routing
- Power users familiar with command structures
- Scenarios requiring zero AI inference latency

---

### AI Mode

**What It Does**

AI mode interprets natural language input and routes it to appropriate commands using semantic similarity. The system embeds user input into 1024-dimensional vectors, computes cosine similarity against pre-vectorized command embeddings, applies confidence thresholds, and routes to the best-match command. If confidence is sufficient, it uses an LLM to extract arguments in JSON format validated against command schemas before execution.

**What It Is Allowed To Do**

- Encode user input via fine-tuned SentenceTransformer model
- Compute similarity scores against all registered command embeddings
- Apply decision thresholds (AUTO_EXECUTE ≥0.75, CONFIRM ≥0.60, REJECT <0.60)
- Query `commands` and `command_embeddings` tables for routing
- Use Groq LLM API for argument extraction with schema validation
- Execute commands from `COMMAND_REGISTRY` with extracted arguments
- Log routing decisions to `ai_decisions` table with confidence and reasoning

**What It Is NOT Allowed To Do**

- Execute commands below confidence thresholds without confirmation
- Hallucinate command outputs or simulate execution results
- Bypass schema validation or execute with malformed arguments
- Execute commands not present in `COMMAND_REGISTRY`
- Modify system state outside registered command boundaries
- Access CHAT mode history injection or explanation logic

**History and Context Interaction**

AI mode logs two distinct record types:

1. **AI Decisions** (`ai_decisions` table):
   - Raw input
   - Chosen command ID
   - Confidence score
   - Decision type (AUTO_EXECUTE/CONFIRM/REJECT)
   - Reasoning

2. **Command Executions** (`command_executions` and `conversation_history`):
   - Actual execution results
   - Mode = "ai"
   - Function called
   - Status and output

ChatCore sees both the routing decision and execution outcome, enabling it to explain why AI mode chose a particular command and what the result was.

**Use Cases**

- Users unfamiliar with exact command syntax
- Natural language queries ("show me recent GitHub activity")
- Exploratory workflows where command names aren't memorized
- Reducing cognitive load for infrequent commands
- Environments where typing speed and fluency matter more than precision

---

### CHAT Mode

**What It Does**

CHAT mode provides a conversational assistant with read-only access to full session history spanning all modes. It uses the Groq LLM API with a strict system prompt enforcing non-execution boundaries. ChatCore can explain past executions, answer questions about system behavior, summarize session activity, and guide users on mode switching, but cannot execute or simulate commands.

**What It Is Allowed To Do**

- Query `conversation_history` for up to 12 past turns
- Read `command_executions` and `ai_decisions` tables for provenance
- Build LLM context with factual execution records from RULE/AI modes
- Explain system behavior based on logged outputs
- Suggest mode switches when users request actions
- Summarize session history accurately
- Reason about past command results
- Answer questions about command availability and usage

**What It Is NOT Allowed To Do**

- Execute or simulate any commands
- Access files, network, system state, or database directly
- Invent command outputs or imply system changes occurred
- Claim credit for executions performed by RULE or AI modes
- Modify database records or system state
- Bypass mode boundaries or escalate privileges
- Provide placeholders or hypothetical execution results

**History and Context Interaction**

ChatCore constructs LLM messages from `conversation_history` as follows:

- **CHAT turns**: Injected as `user`/`assistant` message pairs
- **RULE/AI executions**: Injected as `system` messages containing:
  - Mode (RULE/AI)
  - User input
  - Command called
  - Status (success/error)
  - Output (verbatim from `assistant_output`)
  - Explicit label: "(This execution was performed by the system, not ChatCore.)"

This design ensures ChatCore never confuses explanation with execution and always attributes commands to their source mode.

**Use Cases**

- Understanding past command behavior without re-execution
- Learning what commands are available and how they work
- Debugging unexpected results from previous executions
- Reviewing session activity before termination
- Getting explanations without risking side effects
- Users who want conversational help without execution risk

---

## Database Design

The database consists of 9 tables providing full session persistence, execution provenance, and AI explainability.

### Table 1: `sessions`

**Purpose**

Track individual shell lifecycles from initialization to termination.

**Schema**

```sql
CREATE TABLE sessions (
    session_id INTEGER PRIMARY KEY,
    start_timestamp TEXT NOT NULL,
    end_timestamp TEXT,
    grace_termination BOOLEAN DEFAULT 0
);
```

**Why This Design**

- `session_id`: Derived from Unix timestamp at shell start, providing uniqueness and chronological ordering.
- `start_timestamp`/`end_timestamp`: ISO 8601 format for precise lifecycle tracking.
- `grace_termination`: Distinguishes clean exits from crashes, enabling reliability audits.

All other tables reference `session_id` as a foreign key, forming the root of the relational hierarchy.

---

### Table 2: `commands`

**Purpose**

Define all valid shell commands as a single source of truth. This table is the authoritative registry for both RULE and AI modes.

**Schema**

```sql
CREATE TABLE commands (
    command_id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    schema_json TEXT NOT NULL,
    is_destructive BOOLEAN DEFAULT 0,
    requires_confirmation BOOLEAN DEFAULT 0
);
```

**Why This Design**

- `command_name`: Unique identifier used in `FUNCTION_MAP` and `COMMAND_REGISTRY`.
- `description`: Natural language text used for embedding generation during vectorization.
- `schema_json`: JSON schema defining argument structure, enabling LLM-guided extraction with validation.
- `is_destructive`: Safety flag for commands with irreversible effects.
- `requires_confirmation`: Forces user approval even in AUTO_EXECUTE scenarios.

This table is populated by `seed_commands.py` and remains immutable during runtime.

---

### Table 3: `command_embeddings`

**Purpose**

Store 1024-dimensional semantic vectors for each command, enabling similarity-based intent routing in AI mode.

**Schema**

```sql
CREATE TABLE command_embeddings (
    command_id INTEGER PRIMARY KEY,
    embedding_json TEXT NOT NULL,
    FOREIGN KEY (command_id) REFERENCES commands (command_id)
);
```

**Why This Design**

- One-to-one relationship with `commands` enforced by primary key constraint.
- `embedding_json`: Stores NumPy array as JSON for portability and SQLite compatibility.
- Populated by `db_vector_manager.py` using fine-tuned SentenceTransformer model.
- Loaded into memory at startup by `Function_Router` for fast cosine similarity computation.

---

### Table 4: `command_executions`

**Purpose**

Provide immutable audit trail of all user actions across all modes.

**Schema**

```sql
CREATE TABLE command_executions (
    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    raw_input TEXT NOT NULL,
    command_id INTEGER,
    status TEXT NOT NULL,
    mode TEXT NOT NULL,
    function_called TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
    FOREIGN KEY (command_id) REFERENCES commands (command_id)
);
```

**Why This Design**

- `raw_input`: Exact user input for reproducibility and debugging.
- `command_id`: Links to `commands` table for provenance (NULL if no match).
- `mode`: Distinguishes RULE vs AI vs CHAT executions.
- `function_called`: Python function name for code-level traceability.
- `status`: Success/error flag for filtering and analytics.

Indexed on `session_id` for fast session-scoped queries.

---

### Table 5: `ai_decisions`

**Purpose**

Log AI routing decisions with confidence scores and reasoning for explainability.

**Schema**

```sql
CREATE TABLE ai_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    raw_input TEXT NOT NULL,
    chosen_command_id INTEGER,
    confidence REAL,
    decision_type TEXT NOT NULL,
    reason TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
    FOREIGN KEY (chosen_command_id) REFERENCES commands (command_id)
);
```

**Why This Design**

- `confidence`: Cosine similarity score from semantic routing.
- `decision_type`: AUTO_EXECUTE, CONFIRM, or REJECT based on threshold logic.
- `reason`: Optional human-readable explanation for decision.
- Separate from `command_executions` because AI mode can decide without executing (e.g., REJECT).

Enables post-session analysis of AI behavior and threshold tuning.

---

### Table 6: `errors`

**Purpose**

Track all system, execution, and internal failures with function-level attribution.

**Schema**

```sql
CREATE TABLE errors (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    error_name TEXT NOT NULL,
    error_description TEXT,
    origin_function TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);
```

**Why This Design**

- `error_name`: Categorized error type (CommandError, CriticalCrash, etc.).
- `origin_function`: Pinpoints failure location for debugging.
- Logged automatically by CoreShell on exceptions.
- Indexed on `session_id` for session-scoped error analysis.

---

### Table 7: `conversation_history`

**Purpose**

Persistent turn-by-turn conversation memory spanning all modes, enabling ChatCore to reconstruct full context.

**Schema**

```sql
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    turn_id INTEGER NOT NULL,
    mode TEXT NOT NULL,
    user_input TEXT NOT NULL,
    assistant_output TEXT,
    command_called TEXT,
    status TEXT,
    confidence REAL,
    context_snapshot TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);
```

**Why This Design**

- `turn_id`: Monotonic counter per session for chronological ordering.
- `mode`: RULE/AI/CHAT for mode-specific rendering in ChatCore.
- `assistant_output`: Flattened text output from `command_result` for replay.
- `context_snapshot`: Serialized JSON of `ContextManager` state for debugging.
- `confidence`: Preserved from AI mode for explainability.

Unique index on `(session_id, turn_id)` enforces sequential consistency. ChatCore queries this table with `LIMIT 12` and `ORDER BY turn_id DESC` to build LLM context.

---

### Table 8: `registry`

**Purpose**

Store user-defined shortcuts for the `open` command, enabling quick access to programs, folders, and URLs.

**Schema**

```sql
CREATE TABLE registry (
    name TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    type TEXT CHECK (type IN ('program', 'folder', 'url')) NOT NULL
);
```

**Why This Design**

- `name`: User-chosen alias for registry entry.
- `path`: Absolute path or URL to resource.
- `type`: Constrained to three valid types via CHECK constraint.

Populated via `register` command and consumed by `open` command. Independent of session lifecycle.

---

### Table 9: `settings`

**Purpose**

Centralized key-value store for global configuration.

**Schema**

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Why This Design**

Simple key-value structure for configuration parameters that must persist across sessions (e.g., API keys, preferences, feature flags). Currently unused in v1.0 but reserved for future extensions.

---

## Session & History Model

### How Sessions Are Created

1. **Initialization**: CoreShell calls `create_context()` from `ContextManager.py` at startup.
2. **Session ID Generation**: Unix timestamp (`int(time.time())`) provides unique, chronological identifier.
3. **Database Logging**: `log_session_start()` inserts record into `sessions` table with `start_timestamp`.
4. **Context Object**: In-memory dictionary created with:
   ```python
   {
       "session_id": <timestamp>,
       "user_name": <from env var>,
       "mode": "rule",
       "turn_id": 0,
       "start_time": <ISO 8601>,
       "memory": {},
       "last_command": None
   }
   ```

### Turn Tracking

Each user input increments `turn_id` via `next_turn(context)`:

```python
context["turn_id"] += 1
return context["turn_id"]
```

Turn IDs are monotonic integers starting from 1. Every turn produces exactly one entry in `conversation_history` with the corresponding `turn_id`, creating a deterministic timeline.

### Conversation History Spanning All Modes

The `conversation_history` table is mode-agnostic. Every turn logs:
- User input
- Assistant output (flattened text from `command_result`)
- Mode used (RULE/AI/CHAT)
- Command function called
- Status and confidence

This unified storage enables ChatCore to:
- Reconstruct chronological session flow
- Distinguish CHAT conversations from command executions
- Explain what happened in RULE/AI modes with exact outputs
- Build LLM context that reflects actual system behavior

### ChatCore Awareness of Past Executions

When ChatCore calls `get_conversation_history(session_id, limit=12)`:

1. Database returns last 12 turns in reverse chronological order
2. ChatCore iterates in chronological order (reversed list)
3. For each turn:
   - If `mode == "chat"`: Inject as user/assistant message pair
   - If `mode == "rule"` or `mode == "ai"`: Inject as system message with execution details
4. Execution records include verbatim output from `assistant_output` column

This design ensures ChatCore:
- Never invents outputs
- Always attributes executions to correct mode
- Maintains strict boundaries between explanation and execution
- Can answer questions like "what did the server-health command show?" using logged data

---

## Trial Run / Example Usage

### Starting the Shell

```bash
$ python Core/CoreShell.py
Initializing core systems...
Database schema ready.
Welcome, user.
JaiShell is online.
Type 'help' to see available commands.

JaiShell [RULE] ▸
```

### RULE Mode Usage Examples

**Example 1: Get system status**

```
JaiShell [RULE] ▸ status
Session ID: 1704897234
Current Mode: rule
Turn: 1
```

**Example 2: Check weather**

```
JaiShell [RULE] ▸ weather San Francisco
Weather in San Francisco:
Temperature: 62°F
Conditions: Partly Cloudy
Humidity: 72%
Wind: 8 mph NW
```

**Example 3: Register a shortcut**

```
JaiShell [RULE] ▸ register code /usr/local/bin/code program
Registered 'code' as program → /usr/local/bin/code
```

**Example 4: Open registered program**

```
JaiShell [RULE] ▸ open code
Launching program: code
```

---

### Switching to AI Mode Examples

**Example 1: Switch mode**

```
JaiShell [RULE] ▸ mode ai
Switched to AI mode.

JaiShell [AI] ▸
```

**Example 2: Natural language system info**

```
JaiShell [AI] ▸ show me system information
[Routing to: system-specs]
Confidence: 0.82

Hostname: MacBook-Pro
OS: macOS 14.2
CPU: Apple M2, 8 cores
RAM: 16.0 GB
Disk: 512 GB SSD (234 GB free)
```

**Example 3: GitHub query without exact syntax**

```
JaiShell [AI] ▸ what are my github repositories?
[Routing to: github-repos]
Confidence: 0.88

Your GitHub Repositories:
1. Personalised-Intelligent-Shell (Python) - 34 stars
2. ml-research-toolkit (Jupyter) - 12 stars
3. api-gateway-template (Go) - 8 stars
```

**Example 4: Natural language weather query**

```
JaiShell [AI] ▸ what's the weather like in Tokyo?
[Routing to: weather]
Confidence: 0.91

Weather in Tokyo:
Temperature: 18°C
Conditions: Clear
Humidity: 58%
Wind: 5 mph E
```

---

### Switching to CHAT Mode Examples

**Example 1: Switch mode**

```
JaiShell [AI] ▸ mode chat
Switched to Chat mode.

JaiShell [CHAT] ▸
```

**Example 2: Ask about available commands**

```
JaiShell [CHAT] ▸ what commands can I use in this shell?
JaiShell supports multiple command categories:

1. System Commands: system-specs, system-uptime, wifi-status
2. GitHub Commands: github-repos, github-repo-summary, github-recent-commits
3. Server Commands: server-health, server-state, server-ssh
4. Information Commands: weather, news
5. Core Commands: help, status, history, exit

You can use these in RULE mode with exact syntax, or in AI mode with natural language.
```

**Example 3: Ask about past execution**

```
JaiShell [CHAT] ▸ what did the system-specs command show earlier?
Based on the execution record from turn 2 (AI mode), the system-specs command showed:

- Hostname: MacBook-Pro
- OS: macOS 14.2
- CPU: Apple M2 with 8 cores
- RAM: 16.0 GB
- Disk: 512 GB SSD with 234 GB free

This was a real execution performed by the AI mode, not a simulation.
```

**Example 4: Request action (boundary enforcement)**

```
JaiShell [CHAT] ▸ can you check the weather in London?
I cannot execute commands in CHAT mode. To check the weather, you have two options:

1. Switch to RULE mode and use: `weather London`
2. Switch to AI mode and use natural language: `what's the weather in London?`

CHAT mode is for explanation and assistance only, not execution.
```

---

### Asking About Previous Executions

**Example: Session summary**

```
JaiShell [CHAT] ▸ summarize what I've done this session
Here's your session summary:

Turn 1 (RULE mode): You requested system status. The shell returned session ID and current mode.

Turn 2 (AI mode): You asked "show me system information". The system routed this to system-specs with 0.82 confidence and returned your machine specifications.

Turn 3 (AI mode): You asked "what are my github repositories?". The system routed this to github-repos with 0.88 confidence and listed 3 repositories.

Turn 4 (AI mode): You asked "what's the weather like in Tokyo?". The system routed this to weather with 0.91 confidence and returned Tokyo weather data.

All executions completed successfully.
```

---

## Safety & Design Principles

### No Hallucinated Execution

**Principle**: The system never simulates command outputs or invents execution results.

**Implementation**:
- AI mode routes to real commands in `COMMAND_REGISTRY`, not synthesized responses
- ChatCore injects execution records from database, not generated placeholders
- All outputs in `conversation_history` are from actual function returns
- LLMs used only for routing and argument extraction, never output generation

**Why This Matters**: Users must trust that displayed results reflect actual system state. Hallucinated outputs create false confidence and dangerous decision-making.

---

### No Silent Side Effects

**Principle**: Every command execution is logged with full provenance.

**Implementation**:
- `command_executions` table captures all invocations
- `ai_decisions` table logs routing logic even when rejected
- `errors` table tracks all failures with function attribution
- `conversation_history` preserves turn-by-turn timeline

**Why This Matters**: Audit trails enable debugging, security analysis, and reproducibility. Silent operations create accountability gaps.

---

### Strict Execution Boundaries

**Principle**: Each mode has explicit capabilities enforced by code structure, not prompts.

**Implementation**:
- RULE mode: Direct function map lookup, no AI involvement
- AI mode: Semantic routing + LLM argument extraction, execution via `COMMAND_REGISTRY`
- CHAT mode: LLM responses only, zero access to execution functions

**Why This Matters**: Prompt-based boundaries are fragile and easily bypassed. Architectural enforcement provides hard guarantees.

---

### Explainability-First Design

**Principle**: All AI decisions must be inspectable and understandable.

**Implementation**:
- Confidence scores displayed to users
- Decision types (AUTO/CONFIRM/REJECT) based on explicit thresholds
- AI decisions logged with reasoning text
- Function_Router uses interpretable cosine similarity, not black-box models
- Schema validation errors surfaced to users

**Why This Matters**: Users must understand why the system behaved a certain way. Opaque AI systems erode trust and hinder debugging.

---

### Deterministic Fallback Philosophy

**Principle**: Rule-based execution must always be available as a reliable alternative.

**Implementation**:
- RULE mode independent of AI subsystems
- `FUNCTION_MAP` and `COMMAND_REGISTRY` overlap intentionally
- Mode switching available at any time via `mode rule` / `mode ai` / `mode chat`
- No command exclusively gated behind AI mode

**Why This Matters**: AI systems have failure modes (embedding drift, API outages, ambiguous inputs). Deterministic fallback ensures mission-critical operations remain accessible.

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Groq API key ([get one here](https://console.groq.com/keys))
- 2 GB disk space (for embedding model)
- Linux, macOS, or Windows with WSL

---

### Step 1: Clone Repository

```bash
git clone https://github.com/Jai-saraswat/Personalised-Intelligent-Shell.git
cd Personalised-Intelligent-Shell
```

---

### Step 2: Install Dependencies

```bash
pip install -r Requirements.txt
```

**Key Dependencies:**
- `sentence-transformers>=2.2.2` - Embedding model infrastructure
- `torch>=2.0.0` - PyTorch for model inference
- `groq>=0.4.0` - Groq API client for LLM calls
- `numpy>=1.24.0` - Vector operations
- `scikit-learn>=1.3.0` - Cosine similarity
- `python-dotenv>=1.0.0` - Environment variable management
- `requests>=2.31.0` - HTTP client for external APIs

---

### Step 3: Download Fine-Tuned Embedding Model

The system requires a fine-tuned sentence transformer model for semantic routing. Download from the releases page or train your own:

```bash
# Option 1: Download pre-trained model
# Note: Model not yet released - coming soon in v1.0 release
# wget https://github.com/Jai-saraswat/Personalised-Intelligent-Shell/releases/download/v1.0/Finetuned-gte-large-en-v1.5.tar.gz
# tar -xzf Finetuned-gte-large-en-v1.5.tar.gz

# Option 2: Train from scratch (requires training data)
python AICore/train_embeddings.py
```

Ensure model directory is at: `./Finetuned-gte-large-en-v1.5/`

---

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# API Keys
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: Custom model path
EMBEDDING_MODEL_PATH=./Finetuned-gte-large-en-v1.5

# Optional: User name for personalized prompts
USER_NAME=your_name
```

**Important**: Never commit `.env` to version control. Add to `.gitignore`.

---

### Step 5: Initialize Database and Seed Commands

```bash
# Initialize schema
python Core/db_init.py

# Seed command definitions
python Core/seed_commands.py

# Vectorize commands for AI mode
python Core/db_vector_manager.py
```

**Expected Output:**
```
Initializing database at: ./jaishell.db
Database schema ready.
Seeded 20 commands successfully.
Generating embeddings for 20 commands...
Embeddings stored successfully.
```

---

### Step 6: Verify Installation

```bash
python Core/CoreShell.py
```

**Expected Output:**
```
Initializing core systems...
Database schema ready.
Welcome, user.
JaiShell is online.
Type 'help' to see available commands.

JaiShell [RULE] ▸
```

Test basic commands:
```
JaiShell [RULE] ▸ help
JaiShell [RULE] ▸ status
JaiShell [RULE] ▸ mode ai
JaiShell [AI] ▸ what commands are available?
```

---

### Step 7: Configure External Integrations (Optional)

For GitHub commands, add personal access token:

```bash
# Add to .env
GITHUB_TOKEN=ghp_your_github_token_here
```

For server monitoring commands, configure SSH access:

```bash
# Add to .env
SERVER_HOST=your.server.com
SERVER_USER=admin
SERVER_SSH_KEY=/path/to/ssh/key
```

---

### Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution**: Ensure all dependencies installed: `pip install -r Requirements.txt`

---

**Issue**: `RuntimeError: Model directory not found`

**Solution**: Verify embedding model downloaded to correct path. Check `EMBEDDING_MODEL_PATH` in `.env`.

---

**Issue**: `groq.APIError: Invalid API key`

**Solution**: Verify `GROQ_API_KEY` in `.env` is valid. Get a key from [Groq Console](https://console.groq.com/keys).

---

**Issue**: `sqlite3.OperationalError: no such table: commands`

**Solution**: Run initialization scripts in order:
```bash
python Core/db_init.py
python Core/seed_commands.py
python Core/db_vector_manager.py
```

---

**Issue**: AI mode confidence scores always below threshold

**Solution**: Ensure embeddings generated correctly:
```bash
python Core/db_vector_manager.py --force-regenerate
```

---

**Issue**: CHAT mode not showing execution history

**Solution**: Verify `conversation_history` table populated. Run commands in RULE or AI mode first, then switch to CHAT mode.

---

## Versioning

**Current Version**: 1.0 - Stable Release

This is the first production-ready release of Personalised Intelligent Shell. All core features are implemented, tested, and stable:

- Multi-mode architecture (RULE/AI/CHAT)
- Semantic command routing with fine-tuned embeddings
- LLM-powered argument extraction and conversational assistance
- Full session persistence and provenance tracking
- Execution-safe boundaries and explainability logging

**Release Date**: January 2025

**Semantic Versioning**: This project follows [SemVer](https://semver.org/):
- **Major** (X.0.0): Breaking changes to architecture or API
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes, no feature changes

**Changelog**: See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

---

## License & Author

### License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Jai Saraswat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Full license text: [LICENSE](./LICENSE)

---

### Author

**Jai Saraswat**

Software Engineer specializing in AI systems, natural language processing, and human-computer interaction.

- GitHub: [@Jai-saraswat](https://github.com/Jai-saraswat)

---

### Acknowledgments

This project builds upon foundational work in:
- **Sentence Transformers**: Nils Reimers and Iryna Gurevych for the sentence-transformers library
- **Groq**: High-performance LLM inference infrastructure
- **PyTorch**: Core tensor operations and model serving
- **SQLite**: Reliable embedded database for session persistence

Special thanks to:
- Early adopters who provided feedback during development
- Open-source contributors to dependency libraries
- The NLP research community for advancing embedding techniques

---

### Citation

If you use this project in academic work, please cite:

```bibtex
@software{saraswat2025jaishell,
  author = {Saraswat, Jai},
  title = {Personalised Intelligent Shell: A Hybrid Command-Line Interface with AI-Powered Semantic Routing},
  year = {2025},
  version = {1.0},
  url = {https://github.com/Jai-saraswat/Personalised-Intelligent-Shell}
}
```

---

### Contributing

Contributions are welcome. Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes with clear messages
4. Submit a pull request with detailed description

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

### Support

For bugs, feature requests, or questions:
- **Issues**: [GitHub Issues](https://github.com/Jai-saraswat/Personalised-Intelligent-Shell/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jai-saraswat/Personalised-Intelligent-Shell/discussions)

---

**End of Documentation**
