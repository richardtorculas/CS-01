# Design System

> **Status: draft.** Colors and typography below are placeholders until the team finalizes them during wireframing (Sprint 0). Update this file, not individual components, when they change.

## Principles

- **Clarity over decoration.** Residents may be first-time app users on low-end Android phones; officials scan queues all day.
- **Status is always visible.** Every report shows its status and priority with both color *and* text; never color alone.
- **Accessible by default.** WCAG AA contrast (4.5:1 for text), touch targets at least 44×44 px, labels on every input.
- **Bilingual-ready.** Layouts must tolerate Filipino strings roughly 30% longer than English.

## Color tokens (placeholders)

| Token | Use | Value |
|---|---|---|
| `primary` | Main actions, links, active nav | `#1D4ED8` |
| `primary-foreground` | Text on primary | `#FFFFFF` |
| `surface` | Page background | `#F8FAFC` |
| `card` | Cards, panels | `#FFFFFF` |
| `text` | Body text | `#0F172A` |
| `text-muted` | Secondary text | `#475569` |
| `border` | Dividers, inputs | `#E2E8F0` |
| `danger` | Destructive actions, errors | `#DC2626` |
| `success` | Confirmations | `#16A34A` |

### Status colors

| Status | Color |
|---|---|
| SUBMITTED | slate |
| VALIDATED | blue |
| ASSIGNED | indigo |
| IN_PROGRESS | amber |
| RESOLVED | green |
| CLOSED | gray |
| REJECTED | red |
| REOPENED | orange |

### Priority bands

| Band | Score | Color |
|---|---|---|
| Critical | 80–100 | red |
| High | 60–79 | orange |
| Medium | 40–59 | yellow |
| Low | < 40 | gray |

## Typography

- Font: **Inter** (web), system default (mobile) — placeholder.
- Scale: 12 / 14 / 16 (body) / 18 / 20 / 24 / 30 px.
- Minimum body size on mobile: 16 px.

## Spacing and layout

- 4 px base unit: 4, 8, 12, 16, 24, 32, 48.
- Border radius: 6 px (inputs, buttons), 12 px (cards).
- Web target: 1366×768 and above. Mobile: 360 px width and above.

## Core components

| Component | Web | Mobile | Notes |
|---|---|---|---|
| Button | ✓ | ✓ | primary, secondary, danger, ghost; loading state |
| Status badge | ✓ | ✓ | color + label from API enums |
| Priority badge | ✓ | — | band + score; opens "Why this score?" panel |
| Report card / row | ✓ | ✓ | reference no., category, barangay, age, status |
| Status timeline | ✓ | ✓ | vertical, dated, office name only |
| Photo gallery | ✓ | ✓ | before/after side by side |
| Form field | ✓ | ✓ | label, hint, error, character counter |
| Empty / error / loading states | ✓ | ✓ | required on every list and detail view |
| KPI tile, chart card | ✓ | — | dashboard |
| Map | ✓ | ✓ | Leaflet (web), react-native-maps (mobile) |

## Implementation

- **Web:** tokens defined in the Tailwind config; components in `web/src/components/`.
- **Mobile:** tokens in `mobile/src/theme/`; components in `mobile/src/components/`.
- Don't hardcode colors or spacing values in components; always use tokens.
