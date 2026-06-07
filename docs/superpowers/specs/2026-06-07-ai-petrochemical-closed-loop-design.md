# AI And Petrochemical Closed-Loop Integration Design

## Goal

Connect the AI page and professional petrochemical monitoring workbench into a
reliable closed loop: state flows to AI immediately, AI commands flow back to
the workbench, and AI analysis results become visible operational records.

## State Contract

The server owns the latest petrochemical snapshot:

- `personnel`
- `equipment`
- `sensors`
- `alerts`
- `selectedContext`
- `lastUpdate`
- `sourceOnline`

The AI page receives this complete snapshot immediately after joining
`ai_room`. Incremental `petrochemical_update` events are merged into the
snapshot by type rather than replacing the entire snapshot.

## Closed-Loop Events

- `petrochemical_state`: complete current snapshot.
- `petrochemical_update`: typed incremental update.
- `ai_command`: command from AI to the workbench.
- `command_ack`: server acknowledgement that a command was queued.
- `command_result`: workbench acknowledgement that a command was executed.
- `ai_analysis_result`: AI analysis submitted to the server.
- `ai_analysis`: analysis delivered to the workbench.
- `integration_timeline`: recent commands, results, alerts, and analyses.

## AI Page

- Render the initial snapshot immediately; do not remain in a waiting state.
- Merge typed updates without losing other state sections.
- Show connection state, source freshness, last update, counts, alarms, and
  recent timeline entries.
- Provide quick command actions for focus, acknowledge, dispatch, escalate, and
  resolve.
- Submit a structured AI analysis result for the selected alarm or context.
- Preserve selected alarm/context when returning to the petrochemical page.

## Petrochemical Workbench

- Publish a complete snapshot after connecting and whenever the operator
  changes alarm or selected-context state.
- Execute AI commands through existing workbench functions.
- Return command results to the server.
- Display received AI analysis as an operational recommendation and append it
  to the workbench evidence/timeline.
- Pass the current alarm or selected context when navigating to AI.

## Resilience

- The server keeps the last snapshot when the petrochemical page is closed.
- Snapshot freshness is exposed to AI so stale data is clearly marked.
- Empty snapshots still render a connected-but-no-source-data state.
- Unknown commands return a failed command result instead of silently doing
  nothing.

## Verification

- AI receives a full state immediately on joining.
- AI merges an incremental update while retaining unrelated data.
- AI query responses update the visible panel.
- Commands are queued, delivered, executed, and recorded.
- AI analysis reaches the workbench and is recorded.
- Page navigation preserves selected operational context.
