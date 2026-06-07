# AI And Petrochemical Closed-Loop Integration Implementation Plan

**Goal:** Fix initial AI state loading and implement reliable two-way commands, analysis feedback, and integration timeline.

**Architecture:** Make `server.py` the state/event hub, normalize state handling in `index.html`, and connect command/analysis handlers to the professional workbench in `petrochemical.html`.

## Tasks

1. Add failing server integration tests for initial snapshot, typed updates,
   commands, command results, analysis results, and timeline.
2. Implement server snapshot freshness, source connection state, command result,
   and timeline events.
3. Add failing static contracts for AI snapshot merge/render/commands and
   workbench command/analysis handlers.
4. Implement AI page initial snapshot listener, typed merge, query rendering,
   quick actions, freshness, and timeline UI.
5. Implement workbench snapshot publishing, command execution/result reporting,
   AI recommendation display, and context-preserving navigation.
6. Run unit, syntax, Flask route, Socket.IO, and real-browser verification.
