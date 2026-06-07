# Industrial Monitoring Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the petrochemical simulation's default view into a map-dominant, alarm-first professional industrial monitoring workbench while preserving the existing presentation dashboard and simulation logic.

**Architecture:** Add a professional-mode layout and interaction layer inside the existing `petrochemical.html`. Reuse the current SVG map, data arrays, render functions, and dashboard mode; add stable workbench containers and small JavaScript state/render helpers for alarm selection, response state, evidence updates, and responsive navigation.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, SVG, Python `unittest` static contract tests, Flask test client.

---

### Task 1: Professional Workbench Contract

**Files:**
- Create: `tests/test_professional_workbench.py`
- Modify: `petrochemical.html`

- [ ] Write static contract tests requiring professional mode markers, alarm rail, evidence strip, accessible controls, reduced-motion styles, and presentation mode preservation.
- [ ] Run `python -m unittest tests.test_professional_workbench -v` and verify the new tests fail because the professional workbench markers are absent.
- [ ] Add the professional mode body class, structural containers, labels, and stable IDs while preserving existing map and dashboard IDs.
- [ ] Run the contract tests and verify they pass.

### Task 2: Industrial Visual System And Layout

**Files:**
- Modify: `petrochemical.html`
- Test: `tests/test_professional_workbench.py`

- [ ] Extend the contract tests to require semantic industrial color tokens, map-dominant grid rules, alarm rail styles, evidence strip styles, and tablet/mobile breakpoints.
- [ ] Run the tests and verify the new visual contract fails.
- [ ] Add a scoped professional-mode CSS layer that reduces decorative motion, establishes status color semantics, creates the map/right-rail/bottom-strip layout, and converts narrow layouts to drawer/tab behavior.
- [ ] Run tests and verify they pass.

### Task 3: Alarm Selection And In-Rail Response

**Files:**
- Modify: `petrochemical.html`
- Test: `tests/test_professional_workbench.py`

- [ ] Extend tests to require `selectAlarm`, `renderAlarmDetail`, `updateAlarmState`, and map-focus helpers.
- [ ] Run tests and verify failure.
- [ ] Enrich alarm records with operational metadata and render them as accessible alarm queue buttons.
- [ ] Implement in-rail details and acknowledge, dispatch, escalate, resolve actions without navigating away.
- [ ] Implement alarm-to-map focus and selected-state styling.
- [ ] Run tests and verify they pass.

### Task 4: Contextual Evidence And Entity Selection

**Files:**
- Modify: `petrochemical.html`
- Test: `tests/test_professional_workbench.py`

- [ ] Extend tests to require `renderEvidence`, `selectWorkbenchContext`, and layer-count updates.
- [ ] Run tests and verify failure.
- [ ] Render selected alarm/entity sensor evidence, equipment condition, personnel presence, and recent events in the bottom strip.
- [ ] Replace disruptive entity-selection alerts with contextual workbench selection.
- [ ] Add live counts to layer controls and top operational metrics.
- [ ] Run tests and verify they pass.

### Task 5: Accessibility, Responsive Behavior, And Verification

**Files:**
- Modify: `petrochemical.html`
- Test: `tests/test_professional_workbench.py`

- [ ] Add keyboard/focus behavior and labels for primary workbench controls.
- [ ] Add responsive rail toggle behavior and narrow-screen workspace tabs.
- [ ] Run `python -m unittest tests.test_professional_workbench -v`.
- [ ] Run `python -m py_compile server.py`.
- [ ] Run Flask test-client checks for `/` and `/petrochemical.html`.
- [ ] Run `git diff --check` and inspect remaining warnings.
- [ ] Review the final diff against the approved design specification.
