# The Whisperer

The Whisperer is a context-aware, non-generative agent demonstrator for professional music-production workflows. It explores how an assistant can retain an artist's stated intentions across sessions, recover useful context on re-entry, and choose whether to speak at all. The artist remains the author and decision-maker.

## The problem

Production sessions contain more than parameter changes and playback history. An artist may leave a specific thought about *why* something needs attention, then return later without that thought in view. An assistant that treats repeated listening as a sign of difficulty can interrupt normal creative exploration. The Whisperer tests a narrower response: preserve explicit creative notes and offer relevant continuity only when the context warrants it.

Silence is a first-class agent decision. Repeated playback alone is weak evidence; it can mean the artist is listening and experimenting. Explicit artist intentions carry more weight than inferred behaviour, and any surfaced context is offered for the artist to accept or ignore. The system does not generate music or make artistic choices.

## Architecture

The current demonstrator uses simulated session events rather than a live DAW connection:

```text
session events → observer → context reconstruction → intervention policy → agent → terminal output
                      ↓                 ↑
              explicit artist notes → persistent creative memory
```

- `observer.py` turns playback, artist notes and session opening events into workflow signals.
- `memory.py` stores explicit artist notes and their status in a local JSON file.
- `context.py` combines current signals with previously stored active and unresolved notes, including simple subject matching.
- `intervention.py` applies a transparent scoring rule: unresolved context and project re-entry support intervention; active exploration discourages it.
- `agent.py` coordinates the decision, then persists the current session's explicit notes for later sessions. It constructs a factual continuity prompt when intervention is warranted.
- `app.py` loads the two simulated sessions and prints the decision and evidence in the terminal.

## Two-session demonstrator

1. **Creative work:** The artist repeatedly listens to the chorus and leaves an unresolved note: “Chorus still feels crowded. Revisit the guitars tomorrow.” With no prior unresolved memory, repetition is treated as active exploration. The agent stays **SILENT** (score **-1.25**) and stores the note for future context.
2. **Project re-entry:** The artist opens the project and plays the chorus. The previous unresolved note is now available. The agent **INTERVENES** (score **3.25**) by presenting the note and asking whether the artist wants to resume from it.

## Run

From the repository root, with Python 3.9 or newer:

```bash
python app.py
```

The script resets its local `creative_memory.json` demo state on each run. That file is generated at runtime and ignored by Git. The session inputs are `demo/session_01.json` and `demo/session_02.json`; no external packages or DAW installation are required.

The demonstrator shows an end-to-end, inspectable decision across two simulated production sessions: an explicit intention becomes persistent context for a later session, while repeated playback in the current creative session does not trigger an interruption. It models an agent architecture and terminal interface; it does not currently integrate directly with Pro Tools or another DAW.
