# Professional Industrial Monitoring Workbench Design

## Objective

Upgrade the petrochemical simulation interface from a demonstration-oriented
technology dashboard into a professional industrial monitoring product while
preserving a separate presentation mode for competitions and demonstrations.

The default professional mode prioritizes rapid alarm discovery, spatial
orientation, and in-context incident handling. Existing simulation data,
backend integration, map entities, and major feature logic remain in place.

## Product Modes

### Professional Monitoring Mode

This is the default mode. It is designed for prolonged use by an operator and
uses restrained motion, consistent status semantics, and an alarm-first
workflow.

### Presentation Dashboard Mode

The existing large-screen presentation mode remains available through an
explicit mode switch. It may retain more expressive animation, larger metrics,
and visual effects because its purpose is demonstration rather than continuous
operation.

## Information Architecture

The professional monitoring mode uses the selected "Spatial Situation
Workbench" layout:

1. A compact top command bar.
2. A map-dominant main workspace.
3. A fixed alarm and response rail on the right.
4. A contextual evidence strip below the map.

The map remains visible throughout alarm investigation and response.

## Top Command Bar

The top bar contains only operationally important information:

- System name and connectivity state.
- Overall plant health.
- Unacknowledged alarm count.
- Current time.
- Professional/presentation mode switch.
- Link to the MiMo AI interface.

Simulation controls and secondary tools move out of the primary navigation and
into a compact operations menu.

## Spatial Situation Map

The map is the largest element in the workspace and provides the primary
spatial context.

- Alarmed zones use clear amber or red boundaries and restrained fills.
- Selecting an alarm focuses and highlights its related zone, device, or person.
- Layer controls show entity counts, for example `Personnel 12` and `Equipment
  8`.
- A persistent legend explains status colors and entity symbols.
- Selected items receive a blue selection state that is visually distinct from
  alarm severity.
- Normal map entities do not pulse. Only new, unacknowledged critical alarms
  may use a short pulse.

## Alarm And Response Rail

The fixed right rail is the primary operational workflow.

### Alarm Queue

Each alarm row displays:

- Severity.
- Alarm title and location.
- Time since occurrence.
- Acknowledgement state.
- Related device or sensor.

Unacknowledged critical alarms appear first, followed by warning and
acknowledged alarms.

### In-Context Alarm Detail

Selecting an alarm expands its detail inside the right rail without obscuring
the map. The detail includes:

- Alarm summary and timestamp.
- Related zone, equipment, sensors, and personnel.
- Likely cause or AI assessment.
- Recommended response steps.
- Actions for acknowledge, dispatch, escalate, and resolve.

Actions provide explicit visual feedback and update the alarm state in place.

## Contextual Evidence Strip

The bottom strip changes with the selected alarm, zone, equipment, or person.
For an alarm, it displays the evidence needed for a response decision:

- Relevant sensor readings and short trends.
- Equipment condition.
- Personnel presence.
- Recent related events.

The strip uses tabs on narrow screens to avoid excessive vertical height.

## Visual Language

The professional mode uses an industrial control-room visual language:

- Dark neutral blue-gray surfaces with limited transparency.
- Subtle borders instead of widespread glow effects.
- Cyan-blue exclusively for navigation, focus, and selection.
- Green exclusively for normal state.
- Amber exclusively for warning state.
- Red exclusively for alarm and critical state.
- Purple exclusively for AI assessment and recommendations.

Typography prioritizes legibility. Numeric readings use a monospaced face while
labels and actions use a clear Chinese UI sans-serif stack. Contrast and type
size must support extended use.

## Motion

- Normal online indicators remain static.
- New critical alarms may pulse briefly, then become static.
- Panel and detail transitions are short and functional.
- Background particles and decorative shimmer are disabled in professional
  mode.
- `prefers-reduced-motion` disables nonessential animation in both modes.

## Responsive Behavior

- Desktop: map, fixed right alarm rail, and bottom evidence strip.
- Tablet: map remains primary; the alarm rail becomes a dismissible drawer.
- Narrow screens: alarm queue is the default view, with map and evidence
  available through tabs.

No breakpoint should turn the full three-column interface into one long,
unstructured page.

## Accessibility

- Interactive `div` elements in the primary workflow become semantic buttons
  or receive equivalent keyboard behavior where conversion is impractical.
- All icon-only actions receive accessible labels.
- Controls expose visible `:focus-visible` states.
- Status is never communicated by color alone.
- Primary controls have a minimum practical target size of approximately 40
  pixels.

## Implementation Strategy

Use a progressive professionalization approach:

- Preserve existing data structures, Flask/WebSocket integration, simulation
  behavior, and SVG map.
- Add a professional-mode layout and design layer around the current logic.
- Reuse existing functions through stable IDs and classes where possible.
- Refactor only interaction points required for the alarm-first workflow.
- Preserve presentation dashboard mode behind the explicit mode switch.

## Verification Criteria

- Professional mode is the default and presentation mode remains available.
- The map is the dominant desktop element.
- Alarm selection updates map focus and the in-rail detail without covering the
  map.
- The evidence strip reflects the active alarm or selected map entity.
- Normal states do not use continuous attention-seeking animation.
- Severity colors and AI colors follow the defined semantic system.
- Desktop and tablet layouts remain usable without an unstructured long page.
- Existing simulation, map selection, AI actions, and page switching continue
  to work.
- Keyboard users can reach and operate primary monitoring and alarm controls.
