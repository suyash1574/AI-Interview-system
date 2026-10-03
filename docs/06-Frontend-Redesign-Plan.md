# Autergo Frontend Redesign Plan

## Document Header

| Field | Value |
| :--- | :--- |
| **Document ID** | 06-Frontend-Redesign-Plan |
| **Product** | Autergo AI Interview System |
| **Version** | 1.0 |
| **Date** | October 2026 |
| **Status** | Approved for Implementation |
| **Document Owner** | Product Design & Engineering |
| **Purpose** | Complete specification for rebuilding the Autergo frontend as a premium, production-grade enterprise product. Covers information architecture, design system, component inventory, animation system, screen-by-screen wireframe descriptions, and implementation directives. |

### Revision History

| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| 1.0 | Oct 2026 | Product Design Lead | Initial complete specification |

### References

| Document | Relevance |
| :--- | :--- |
| [00-Master-Requirements-Baseline](00-Master-Requirements-Baseline.md) | Entity registry, role definitions, product identity |
| [01-BRD](01-BRD.md) | Business objectives driving UX priorities |
| [02-PRD](02-PRD.md) | Personas, user journeys, feature scope |
| [03-FRD](03-FRD.md) | Workflows and functional actors |
| [04-FRS](04-FRS.md) | Detailed functional specifications |
| [05-SRS](05-SRS.md) | System architecture, external interfaces |
| [07-Technology-Decision-Matrix](07-Technology-Decision-Matrix.md) | Approved tech stack |
| [DESIGN.md](../DESIGN.md) | Authoritative visual direction — Apple-influenced premium design language |

### Assumptions

- [ASSUMPTION] The approved frontend stack is HTML + Tailwind CSS (CDN or build) + vanilla JavaScript. No framework migration is required.
- [ASSUMPTION] Inter variable font (Google Fonts) is used as the SF Pro substitute per DESIGN.md guidance.
- [ASSUMPTION] All existing frontend files are placeholder shells with no reusable implementation. The rebuild starts from scratch.
- [ASSUMPTION] Tailwind CSS is configured via a `tailwind.config.js` with custom design tokens; CDN play mode is used for prototype, replaced by a build pipeline for production.
- [ASSUMPTION] Motion library: CSS animations and the Web Animations API are the default. GSAP ScrollTrigger is permitted only for the landing page scroll animations.
- [ASSUMPTION] Charts: Chart.js (lightweight, no React dependency) is the approved charting library.
- [ASSUMPTION] Icons: Phosphor Icons (Duotone weight for key actions, Regular weight for navigation) via CDN. No decorative AI icons.

### Open Decisions

- [OPEN DECISION] Whether the recruiter sidebar is a persistent left rail (≥1280px) or always-collapsible. Recommendation: persistent at ≥1280px, icon-only rail at 1024–1279px, drawer on mobile.
- [OPEN DECISION] Dark mode support timeline. Recommendation: implement design tokens as CSS custom properties from day one to allow dark mode to be added in a future sprint without a rewrite.

---

## 1. Executive Summary

The current Autergo frontend consists of five HTML placeholder shells with no visual implementation. The product requires a complete rebuild to match its enterprise positioning.

Autergo's product is sophisticated: real-time voice AI interviews, adaptive candidate screening, multi-agent evaluation, and evidence-backed reporting. The UI must reflect that sophistication without decorative AI clichés. Intelligence is communicated through workflow clarity, information density, and interaction quality — not through glowing graphics.

The visual direction is grounded in DESIGN.md's Apple-influenced language: a near-invisible UI that recedes behind the product's data. A restrained color system, strong typographic hierarchy, consistent spatial rhythm, and purposeful motion.

This document specifies everything required before a single line of implementation code is written.

---

## 2. Visual Direction

### 2.1 Design Philosophy

Autergo must look like **serious enterprise software built by people who care about craft**. The reference points for quality level — not visual copying — are Linear (information density, keyboard-first interactions), Stripe (documentation clarity, trust through restraint), Notion (spatial rhythm, progressive disclosure), and Vercel (dark surfaces done right, monochromatic excellence).

The product communicates intelligence through:
- **Workflow** — a recruiter can run a drive from creation to report in a logical, low-friction sequence
- **Data** — candidates' scores, evidence, and transcripts are presented with clarity and hierarchy
- **Speed** — micro-interactions, skeleton loaders, and optimistic UI signal that the system is fast
- **Restraint** — nothing competes with the data; chrome disappears

What the product explicitly does not do:
- Use robot, brain, circuit-board, neural-network, sparkle, or wand iconography
- Use neon purple/blue glows or glassmorphic blobs
- Label things "AI Powered" in badges
- Create decorative motion that has no information value

### 2.2 Surface Strategy

Autergo operates two distinct surface modes:

| Surface | Users | Character |
| :--- | :--- | :--- |
| **Recruiter Portal** | Head Recruiter, Sub-Recruiter, Company Admin | Dense, operational, desktop-first. Information hierarchy matters. Tables, charts, activity streams. |
| **Candidate Surface** | Guest Candidate, Student | Calm, focused, minimal. One task at a time. Generous whitespace. |
| **Landing Page** | Prospects | Editorial, polished, product-forward. Demonstrates the product visually. |
| **Super Admin** | Platform Admin | Utilitarian. Oversight and configuration. No decorative chrome. |

---

## 3. Design System

### 3.1 Color Tokens

All colors are defined as CSS custom properties on `:root`. Tailwind config maps these tokens into utility classes.

#### Brand & Primary

| Token | Value | Use |
| :--- | :--- | :--- |
| `--color-primary` | `#1a56db` | Primary interactive element: links, focused inputs, primary buttons. A deep, confident blue — not bright, not electric. |
| `--color-primary-hover` | `#1648c4` | Hover state of primary elements. |
| `--color-primary-active` | `#1340b0` | Active/pressed state. Paired with `transform: scale(0.97)`. |
| `--color-primary-subtle` | `#eff3ff` | Low-emphasis primary surface: selected row backgrounds, tag backgrounds on light surfaces. |
| `--color-primary-on-dark` | `#6ea8ff` | Links and inline emphasis on dark surfaces where `--color-primary` would disappear. |

#### Neutral Scale (Light Mode)

| Token | Value | Use |
| :--- | :--- | :--- |
| `--color-canvas` | `#ffffff` | Primary page background. |
| `--color-canvas-subtle` | `#f8f9fa` | Secondary background: sidebar, table header bands, input fill. |
| `--color-canvas-muted` | `#f1f3f5` | Tertiary background: hover states on list items, code blocks. |
| `--color-border` | `#e5e7eb` | Default 1px border for cards, inputs, dividers. |
| `--color-border-strong` | `#d1d5db` | Stronger border: focused input ring base, table column separators. |
| `--color-ink` | `#111827` | Primary text: headings, data values. |
| `--color-ink-secondary` | `#374151` | Body text, descriptions. |
| `--color-ink-muted` | `#6b7280` | Metadata, captions, placeholder text. |
| `--color-ink-disabled` | `#9ca3af` | Disabled state text. |

#### Dark Surface (Recruiter sidebar, candidate interview background)

| Token | Value | Use |
| :--- | :--- | :--- |
| `--color-dark-base` | `#0f1117` | True dark surface base. Recruiter sidebar background on dark variant. Candidate interview screen. |
| `--color-dark-surface` | `#181c27` | Elevated surface within dark base. Cards on dark. |
| `--color-dark-border` | `rgba(255,255,255,0.08)` | Hairline border on dark surfaces. |
| `--color-dark-ink` | `#f1f3f5` | Primary text on dark. |
| `--color-dark-ink-muted` | `#9ca3af` | Secondary text on dark. |

#### Semantic

| Token | Value | Use |
| :--- | :--- | :--- |
| `--color-success` | `#16a34a` | Pass states, completed status, positive scores. |
| `--color-success-subtle` | `#f0fdf4` | Success background tint. |
| `--color-warning` | `#d97706` | Attention needed, moderate risk, pending states. |
| `--color-warning-subtle` | `#fffbeb` | Warning background tint. |
| `--color-error` | `#dc2626` | Failures, integrity flags, critical errors. |
| `--color-error-subtle` | `#fef2f2` | Error background tint. |
| `--color-info` | `#0284c7` | Informational callouts. |
| `--color-info-subtle` | `#f0f9ff` | Info background tint. |

#### Score Visualization (Candidate Reports)

| Token | Value | Score Range | Use |
| :--- | :--- | :--- | :--- |
| `--color-score-strong` | `#16a34a` | 75–100 | Strong performer |
| `--color-score-good` | `#65a30d` | 60–74 | Good performer |
| `--color-score-moderate` | `#d97706` | 40–59 | Moderate — review needed |
| `--color-score-weak` | `#dc2626` | 0–39 | Weak — flag for recruiter |

**Color usage rule:** Do not use color decoratively. Color signals state, hierarchy, interaction, or an alert condition. Neutral ink + strong typography carries hierarchy on most surfaces.

---

### 3.2 Typography

Inter variable font via Google Fonts. Applied per DESIGN.md's SF Pro substitute guidance.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

:root {
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
}
```

#### Type Scale

| Token | Size | Weight | Line Height | Letter Spacing | Use |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `display` | 48px | 600 | 1.08 | -0.03em | Landing page hero headline |
| `display-md` | 36px | 600 | 1.11 | -0.025em | Section headlines, major page titles |
| `heading-xl` | 28px | 600 | 1.25 | -0.02em | Page-level headings, drive title |
| `heading-lg` | 22px | 600 | 1.30 | -0.015em | Section titles, card headings |
| `heading-md` | 18px | 600 | 1.40 | -0.01em | Subsection headings, modal titles |
| `heading-sm` | 15px | 600 | 1.45 | 0 | Table column headers, sidebar section labels |
| `body-lg` | 17px | 400 | 1.65 | -0.01em | Primary body text (per DESIGN.md: 17px not 16px) |
| `body` | 15px | 400 | 1.60 | 0 | Standard UI text, table rows, descriptions |
| `body-strong` | 15px | 600 | 1.60 | 0 | Emphasized inline text, data labels |
| `caption` | 13px | 400 | 1.50 | 0 | Metadata, timestamps, secondary labels |
| `caption-strong` | 13px | 600 | 1.50 | 0.01em | Badge text, status labels |
| `label` | 12px | 500 | 1.40 | 0.04em | Form labels (uppercase optional for section labels) |
| `data` | 24px | 600 | 1.0 | -0.02em | KPI numbers, metric values on dashboards |
| `data-lg` | 36px | 600 | 1.0 | -0.03em | Hero metrics on overview cards |
| `mono` | 13px | 400 | 1.70 | 0 | Code, transcript text, API values |

**Typography principles:**
- Negative letter-spacing at all heading sizes (per DESIGN.md). No negative tracking below 15px.
- Weight ladder: 400 → 500 (labels only) → 600 (headings, data, strong) → 700 (reserved for critical alerts only).
- Do not use `font-weight: 700` for display headings. 600 is the heading ceiling.
- All-caps labels (`letter-spacing: 0.08em`, `font-size: 11px`, `font-weight: 500`) are permitted for table column headers and sidebar section dividers only.

---

### 3.3 Spacing Scale

Base unit: 4px. All values are multiples of 4.

| Token | Value | Use |
| :--- | :--- | :--- |
| `space-1` | 4px | Minimum internal gap, icon-to-label spacing |
| `space-2` | 8px | Tight inline spacing, compact form field groups |
| `space-3` | 12px | Default inner card padding (compact mode) |
| `space-4` | 16px | Standard component padding |
| `space-5` | 20px | Comfortable form field spacing |
| `space-6` | 24px | Card padding default |
| `space-8` | 32px | Section separator within a page panel |
| `space-10` | 40px | Generous section padding |
| `space-12` | 48px | Major section separation |
| `space-16` | 64px | Hero section padding |
| `space-20` | 80px | Landing page section rhythm (per DESIGN.md) |
| `space-24` | 96px | Landing page hero vertical breathing |

---

### 3.4 Border Radius Scale

| Token | Value | Use |
| :--- | :--- | :--- |
| `radius-xs` | 3px | Inline code badges, very compact chips |
| `radius-sm` | 6px | Buttons, input fields, compact cards |
| `radius-md` | 10px | Standard cards, modals, dropdowns |
| `radius-lg` | 16px | Large cards, sheet panels, onboarding cards |
| `radius-xl` | 24px | Landing page feature cards |
| `radius-pill` | 9999px | Primary CTA buttons, search inputs, status badges |

---

### 3.5 Elevation & Shadow

Per DESIGN.md philosophy: shadow is used only to lift interactive surfaces, not for decoration.

| Level | Treatment | Use |
| :--- | :--- | :--- |
| **Flat** | No shadow, `border: 1px solid var(--color-border)` | Cards, table borders, input fields at rest |
| **Raised** | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05)` | Dropdown menus, tooltips, floating action bars |
| **Elevated** | `0 4px 16px rgba(0,0,0,0.10), 0 1px 4px rgba(0,0,0,0.06)` | Modals, drawers, popovers |
| **Overlay** | `0 20px 48px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.08)` | Full-screen overlays, command palettes |
| **Product** | `0 3px 30px rgba(0,0,0,0.20)` | Product UI screenshots in landing page only |

**Dark surface rule:** No shadows on dark surfaces. Separation is achieved through color steps (`--color-dark-base` → `--color-dark-surface`) and the hairline border.

---

### 3.6 Animation System

All durations and easings are centrally defined as CSS custom properties.

#### Timing Tokens

| Token | Value | Use |
| :--- | :--- | :--- |
| `--duration-micro` | `120ms` | Button press, hover color change, icon swap |
| `--duration-fast` | `180ms` | Dropdown open/close, tooltip appear, badge state change |
| `--duration-base` | `240ms` | Modal open, drawer slide, tab indicator move |
| `--duration-slow` | `360ms` | Page section reveal, skeleton fade, large panel transition |
| `--duration-page` | `300ms` | Page-level transition (fade + translate) |

#### Easing Tokens

| Token | Value | Character |
| :--- | :--- | :--- |
| `--ease-default` | `cubic-bezier(0.16, 1, 0.3, 1)` | Snappy deceleration — default for all UI motion |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving the screen |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Micro bounce for confirmation states only. Use sparingly. |
| `--ease-linear` | `linear` | Progress bars, audio visualization |

#### Motion Principles

1. **Purposeful**: Every animation communicates a state change or aids spatial orientation.
2. **Fast**: UI interactions complete in ≤240ms. Nothing lingers.
3. **Directional**: Elements enter from the direction they originated (dropdown falls from trigger, drawer slides from right).
4. **Consistent**: Same animation for the same component type, everywhere.
5. **Reducible**: All transitions respect `prefers-reduced-motion: reduce`. When reduced motion is preferred, duration collapses to 0ms and transforms are removed; opacity transitions may remain at ≤120ms.

#### Animation Catalogue

| Component | Enter | Exit | Duration |
| :--- | :--- | :--- | :--- |
| Page transition | `opacity: 0→1` + `translateY(6px→0)` | `opacity: 1→0` | `--duration-page` |
| Dropdown menu | `opacity: 0→1` + `translateY(-4px→0)` + `scale(0.97→1)` | Reverse | `--duration-fast` |
| Modal | `opacity: 0→1` + `scale(0.97→1)` | Reverse | `--duration-base` |
| Drawer (right) | `translateX(100%→0)` | Reverse | `--duration-base` |
| Toast | `translateX(calc(100% + 24px)→0)` | `translateX(calc(100% + 24px))` | `--duration-fast` |
| Skeleton → content | `opacity: 0→1` | — | `--duration-slow` |
| Row appear (table) | `opacity: 0→1` + `translateY(4px→0)` | — | `--duration-fast` |
| Number transition | Countup via JS (50–300ms depending on magnitude) | — | Variable |
| Tab indicator | `scaleX` slide to new position | — | `--duration-fast` |
| Button press | `transform: scale(0.97)` on `:active` | Release → scale(1) | `--duration-micro` |
| Status pill state | `background-color` crossfade | — | `--duration-fast` |
| Progress bar fill | Width transition `--ease-linear` | — | Proportional |
| Audio waveform | CSS `scaleY` on bars, driven by amplitude | — | `--ease-linear` real-time |
| Interview state (Speaking→Listening) | Opacity crossfade on indicator | — | `--duration-base` |

#### Scroll Animation (Landing Page Only)

- Use Intersection Observer API. No GSAP on the recruiter portal.
- Trigger: element enters viewport at 80% threshold.
- Effect: `opacity: 0→1` + `translateY(16px→0)`, `--duration-slow`, `--ease-default`.
- Stagger: 60ms between sibling elements in a feature grid.
- **Do not** animate headers, navigation, or any element the user needs to see immediately.

---

## 4. Information Architecture

### 4.1 Recruiter Portal Navigation

```
Autergo Portal
├── Overview (Dashboard)
├── Drives
│   ├── Drive List
│   ├── Create Drive
│   └── [Drive Detail]
│       ├── Overview
│       ├── Candidates
│       ├── Interviews
│       ├── Evaluation
│       ├── Integrity
│       └── Settings
├── Jobs
│   ├── Job List
│   └── Create/Edit Job
├── Candidates
│   ├── All Candidates
│   └── [Candidate 360]
│       ├── Summary
│       ├── Interview
│       ├── Scores
│       ├── Transcript
│       └── Integrity
├── Question Bank
│   ├── All Questions
│   └── Create/Edit Question
├── Reports
├── Settings
│   ├── Company
│   ├── Team
│   ├── Billing
│   └── Integrations
└── Help
```

### 4.2 Candidate Flow

```
Invitation Link
→ Candidate Entry (token verify + instructions)
→ Device Check (microphone, browser, connection)
→ Identity Verification (optional, per drive config)
→ Interview Lobby (brief, countdown, confirm)
→ Voice Interview (active session)
→ Interview Complete (thank you, next steps)
```

### 4.3 Landing Page Sections

```
Landing Page
├── Global Navigation
├── Hero (headline + CTA + product preview)
├── Problem Statement (the status quo is broken)
├── How It Works (3-step process)
├── Feature Showcase (for recruiters)
├── Feature Showcase (for candidates)
├── Integrity & Trust
├── Metrics / Social Proof
├── Pricing (teaser or CTA)
├── Final CTA Section
└── Footer
```

### 4.4 Super Admin Portal

```
Super Admin
├── Platform Overview
├── Tenants (Companies)
│   └── [Tenant Detail]
├── Users
├── AI Provider Config
├── Feature Flags
├── Billing & Subscriptions
├── System Health
└── Audit Logs
```

---

## 5. Page Hierarchy & Screen Inventory

The following 21 screens are in scope. Screen IDs are used throughout this document.

| ID | Screen | Surface | Priority |
| :--- | :--- | :--- | :--- |
| SCR-01 | Landing Page | Public | P1 |
| SCR-02 | Recruiter Login / Signup | Auth | P1 |
| SCR-03 | Recruiter Dashboard (Overview) | Portal | P1 |
| SCR-04 | Drive List | Portal | P1 |
| SCR-05 | Create Drive (Wizard) | Portal | P1 |
| SCR-06 | Drive Overview (Command Center) | Portal | P1 |
| SCR-07 | Drive → Candidate List | Portal | P1 |
| SCR-08 | Candidate 360 | Portal | P1 |
| SCR-09 | Interview Configuration | Portal | P2 |
| SCR-10 | Interview Scheduling | Portal | P2 |
| SCR-11 | Candidate Invitation | Portal | P2 |
| SCR-12 | Candidate Entry & Verification | Candidate | P1 |
| SCR-13 | Device Check | Candidate | P1 |
| SCR-14 | Voice Interview | Candidate | P1 |
| SCR-15 | Interview Complete | Candidate | P1 |
| SCR-16 | Recruiter Evaluation View | Portal | P1 |
| SCR-17 | Candidate Report (Recruiter view) | Portal | P1 |
| SCR-18 | Candidate Report (Candidate-facing) | Candidate | P2 |
| SCR-19 | Question Bank | Portal | P2 |
| SCR-20 | Settings | Portal | P2 |
| SCR-21 | Super Admin Dashboard | Admin | P2 |

---

## 6. Component Inventory

All components are reusable, token-driven, and documented below. Implementation lives in `frontend/components/`. Each component is a self-contained HTML+CSS block with a corresponding JS class or module where behavior is required.

### 6.1 Primitive Components

| Component | File | Description |
| :--- | :--- | :--- |
| `Button` | `components/button.html` | Variants: primary, secondary (outline), ghost, danger, link. Sizes: sm, md, lg. States: default, hover, active, disabled, loading. |
| `Input` | `components/input.html` | Text, email, password, number. States: default, focused, error, disabled. Includes label, helper text, error message. |
| `Textarea` | `components/textarea.html` | Auto-resize variant. Same states as Input. |
| `Select` | `components/select.html` | Custom dropdown replacement. Supports search/filter for long lists. |
| `Checkbox` | `components/checkbox.html` | Single and indeterminate state for table select-all. |
| `Radio` | `components/radio.html` | Radio group with label. |
| `Toggle` | `components/toggle.html` | On/off switch. |
| `Badge` | `components/badge.html` | Status, label, count. Variants: default, success, warning, error, info, neutral. |
| `Avatar` | `components/avatar.html` | Initials fallback. Sizes: sm, md, lg. |
| `Tooltip` | `components/tooltip.html` | Lightweight hover tooltip. No external lib. |
| `Spinner` | `components/spinner.html` | Size variants. Accessible (role=status). |
| `Progress` | `components/progress.html` | Linear bar. Animated fill. Accessible. |
| `Skeleton` | `components/skeleton.html` | Line, block, circle, table row variants. Shimmer animation. |

### 6.2 Composite Components

| Component | File | Description |
| :--- | :--- | :--- |
| `Card` | `components/card.html` | Header/body/footer slots. Flat (border only) and raised variants. No decorative shadow on data cards. |
| `StatCard` | `components/stat-card.html` | Single KPI: label + `data-lg` value + delta (↑/↓ with color). Used on dashboard and drive overview. |
| `Table` | `components/table.html` | Sortable headers, row hover, row selection, sticky header, bulk action bar. No library dependency. |
| `Pagination` | `components/pagination.html` | Page numbers + prev/next. Shows item count. |
| `Tabs` | `components/tabs.html` | Underline indicator variant (portal pages) and pill variant (settings). Animated indicator. |
| `Modal` | `components/modal.html` | Centered overlay. Sizes: sm, md, lg, full. Focus trap. ESC to close. |
| `Drawer` | `components/drawer.html` | Right-slide panel. Used for candidate detail preview, create forms. |
| `Dropdown` | `components/dropdown.html` | Action menu. Triggered by button or icon. Keyboard navigable. |
| `Toast` | `components/toast.html` | Notification system. Top-right stack. Auto-dismiss at 4s. Variants: success, error, warning, info. |
| `Alert` | `components/alert.html` | Inline contextual message. Dismissible. Same variants as Toast. |
| `Stepper` | `components/stepper.html` | Horizontal step progress for wizards (Create Drive, Device Check). |
| `EmptyState` | `components/empty-state.html` | Title + description + single CTA. No illustrations. Uses a subtle icon. |
| `ErrorState` | `components/error-state.html` | Actionable error with retry, context, and support link. |
| `SearchInput` | `components/search-input.html` | Pill-shaped input with leading search icon. Keyboard shortcut hint. |
| `FilterBar` | `components/filter-bar.html` | Horizontal row of filter chips + sort dropdown. Used on table views. |
| `Breadcrumb` | `components/breadcrumb.html` | Portal navigation trail. |

### 6.3 Domain-Specific Components

| Component | File | Description |
| :--- | :--- | :--- |
| `DriveCard` | `components/drive-card.html` | Drive summary card: name, role, status, candidate count, progress bar, last activity. |
| `CandidateRow` | `components/candidate-row.html` | Table row with avatar, name, stage badge, score, last activity, action menu. |
| `ScoreBar` | `components/score-bar.html` | Horizontal bar with score value and color band. Used in competency tables. |
| `CompetencyGrid` | `components/competency-grid.html` | Grid of competency rows, each with label, score bar, evidence count. |
| `TranscriptBlock` | `components/transcript-block.html` | Alternating candidate/AI exchange blocks. Monospace candidate voice, serif AI voice (body font). Timestamp per block. |
| `IntegrityEvent` | `components/integrity-event.html` | Timestamped event row with severity icon, description, and expandable evidence. |
| `InterviewStateIndicator` | `components/interview-state.html` | Voice interview state display. States: Idle, Listening, Speaking, Processing, Error, Complete. |
| `AudioVisualizer` | `components/audio-visualizer.html` | Custom minimal waveform. CSS animated bars driven by Web Audio API amplitude. |
| `DeviceCheckItem` | `components/device-check-item.html` | Single device check row: icon, label, status (checking → pass/fail), optional action. |
| `DriveProgressRing` | `components/drive-progress-ring.html` | Thin SVG ring showing completion %. Animated on mount. |
| `RecruiterNote` | `components/recruiter-note.html` | Inline note block with timestamp, author, editable text. |
| `LiveCounterBadge` | `components/live-counter.html` | Animated number that transitions when value changes. Used in Drive Command Center. |

### 6.4 Layout Components

| Component | File | Description |
| :--- | :--- | :--- |
| `AppShell` | `layouts/app-shell.html` | Portal shell: top bar + left sidebar + main content area. |
| `Sidebar` | `layouts/sidebar.html` | Left navigation rail. Persistent at ≥1280px, icon-only at 1024–1279px, drawer on mobile. |
| `TopBar` | `layouts/topbar.html` | 56px height. Logo, breadcrumb, global actions (notifications, user menu). |
| `PageHeader` | `layouts/page-header.html` | Consistent page title + subtitle + primary action slot. |
| `SplitPane` | `layouts/split-pane.html` | Left detail + right panel for Candidate 360 and Evaluation views. |
| `LandingNav` | `layouts/landing-nav.html` | Landing page top nav. Sticky, frosted glass on scroll. |
| `CandidateShell` | `layouts/candidate-shell.html` | Minimal single-column shell for candidate flows. No sidebar. |

---

## 7. Screen-by-Screen Wireframe Descriptions

### SCR-01 — Landing Page

**Layout:** Full-width editorial layout. No sidebar. LandingNav sticks at top.

**Sections:**

**1. Hero**
- Full-width section, `var(--color-canvas)` background.
- Left column (55%): Display headline (48px/600/−0.03em): `"Interview at Scale. Evaluate with Evidence."` Below: 17px body text explaining the core value proposition in 2 sentences. Two buttons: primary pill (`"Start Free Trial"`) + ghost pill (`"See How It Works"`). Below buttons: trust signal row — 3 short social proof items (e.g., `"1,200+ recruiters"`, `"98% report time saved"`).
- Right column (45%): Actual product UI screenshot of the Drive Overview screen, lightly elevated (the single product-shadow from DESIGN.md), slightly rotated 2° for editorial quality. No gradient behind it.
- Vertical padding: 96px top, 80px bottom.

**2. Problem Statement**
- `var(--color-canvas-subtle)` background tile.
- Centered narrow column (640px max).
- Section label (11px/500/uppercase): `"The Status Quo"`.
- Heading: `"Manual screening doesn't scale."`.
- 2–3 sentence description of the problem.
- 3 compact stat callouts in a row: e.g., `"45 min per candidate"`, `"3× hiring bias risk"`, `"60% of strong candidates screened out late"`. Each stat: `data-lg` token for number, caption below.

**3. How It Works**
- White background.
- Section heading: `"From Job Post to Evidence Report in One Flow."`.
- 3-step horizontal layout: Step number (small, muted) + heading + 2-sentence description. Connected by a thin horizontal line.
- Steps: 1. Configure the Drive → 2. Candidates Interview by Voice → 3. Review Evidence-Backed Reports.
- No icons for the sake of icons. If icons are used, they are Phosphor Regular weight, directly communicating the action.

**4. Recruiter Feature Showcase**
- Alternating light/dark tile sections (per DESIGN.md section rhythm).
- Feature 1 (white tile): Drive Command Center. Left text, right product screenshot.
- Feature 2 (canvas-subtle tile): Candidate 360 / Evidence Report. Right text, left screenshot.
- Feature 3 (white tile): Adaptive Voice Interview Engine. Text + waveform visualization screenshot.

**5. Candidate Experience**
- Single dark tile (`--color-dark-base`). Text on dark.
- Heading: `"A Professional Interview. Not a chatbot."`.
- 3 compact callouts: `"Calm, focused interface"` / `"Voice-first, no typing"` / `"Clear progress throughout"`.
- Screenshot of the candidate interview screen (dark surface).

**6. Integrity & Trust**
- White tile. Icons used purposefully: shield for security, lock for privacy, eye for monitoring.
- 3-column feature list: Integrity Monitoring, Multi-tenant Data Isolation, Evidence-Backed Scores.

**7. Final CTA**
- `--color-dark-base` tile.
- Large centered heading + primary button + secondary ghost button.

**8. Footer**
- `var(--color-canvas-subtle)`. Dense 4-column link layout. Legal row.

---

### SCR-02 — Recruiter Login / Signup

**Layout:** CandidateShell (no sidebar). Two-panel: left brand panel (40%), right form panel (60%).

**Left panel:** Dark surface (`--color-dark-base`). Autergo wordmark (top left). Centered pull-quote from a recruiter persona — testimonial with name, company, role. Bottom: subtle description of the product value. No decorative graphics.

**Right panel:** White. Vertically centered form.
- Heading: `"Sign in to Autergo"`. Subheading: `"New to Autergo? Start free."` (link).
- Email + Password inputs with labels.
- `"Forgot password?"` link aligned right of password field.
- Primary button: `"Sign In"` (full width, pill).
- Divider: `"or continue with"`.
- OAuth buttons: Google, GitHub (outline style, full width, proper brand icons — no decorative extras).
- Below form: 12px legal line re: data privacy.

**States:** Loading spinner on button during auth, error Alert inline above form on failure.

---

### SCR-03 — Recruiter Dashboard (Overview)

**Layout:** AppShell. PageHeader: `"Overview"`.

**Content structure:**

**Row 1 — KPI Strip (4 StatCards):**
- Active Drives / Total Candidates / Interviews This Week / Avg Completion Rate.
- Each StatCard: label (13px/caption), value (`data-lg`), delta with direction arrow. Flat card, border only.

**Row 2 — Two columns (65% / 35%):**
- Left: `"Active Drives"` — list of 3–5 DriveCards with inline progress bars and `"View Drive"` action. Below list: `"View all drives →"` link.
- Right: `"Upcoming Activity"` — timeline list of upcoming interview slots (candidate name, drive, scheduled time). Badge per item for status.

**Row 3 — Two columns (50% / 50%):**
- Left: `"Recent Completions"` — table: candidate, drive, score badge, completed time, `"View Report"` link.
- Right: `"Alerts"` — list of actionable items: integrity events, expired invitations, pending reviews. Each row: severity icon (color), description, action button.

**Empty state:** When no drives exist, the entire main area shows an EmptyState component: `"Create your first Recruitment Drive"` + `"New Drive"` button.

---

### SCR-04 — Drive List

**Layout:** AppShell. PageHeader: `"Drives"` + `"New Drive"` primary button.

**Content:**
- FilterBar: Search input + Status filter (All / Active / Paused / Draft / Completed) + Sort (Recent / Alphabetical / Candidates).
- Table: Drive name, Role, Status badge, Candidates (invited / completed), Progress bar (thin, inline), Created date, Actions (View, Duplicate, Archive).
- Pagination below table.
- Empty state if no drives match filter.

---

### SCR-05 — Create Drive (Wizard)

**Layout:** AppShell with Stepper at top of content area (not in sidebar).

**Steps:**
1. **Job Details** — Drive name, Job Title, Department, Location, Employment type. Upload or paste Job Description (textarea with AI-parse notice: `"Autergo will extract competencies from this JD"`). No sparkle icon. Just a subtle inline text notice.
2. **Interview Configuration** — Interview type (Technical / Behavioral / Mixed), Duration (15 / 30 / 45 / 60 min), Difficulty level, Required competency sections (multi-select checkboxes), Coding interview toggle (if Technical).
3. **Evaluation Criteria** — Competency weights sliders. Passing score threshold. Custom evaluation notes.
4. **Candidate Invitations** — Upload CSV or enter emails. Preview invitation email text. Set expiry date.
5. **Review & Publish** — Summary of all steps. Edit links per section. `"Publish Drive"` primary button. `"Save as Draft"` ghost button.

**Stepper:** Numbered steps, active step highlighted, completed steps show checkmark. Step titles visible. Click to navigate to completed steps.

---

### SCR-06 — Drive Overview (Command Center)

**Layout:** AppShell. Drive name as page heading with Drive status badge. Tab bar below heading: Overview / Candidates / Interviews / Evaluation / Integrity / Settings.

**Overview Tab:**

**Top: Live Metrics Bar (6 LiveCounterBadge components):**
`Invited` / `Started` / `In Progress` / `Completed` / `Pending Review` / `Flagged`
Values animate when they change (number transition). A subtle green pulse on `In Progress` count when active interviews exist. No flashing.

**Middle: Two columns:**
- Left (60%): Candidate funnel — horizontal stacked bar showing stage distribution. Below: sortable top-5 candidates table (name, score, stage, last activity).
- Right (40%): Activity stream — real-time event list. Each event: timestamp, candidate name, event type (Started Interview, Completed, Integrity Flag, etc.). New events appear at top with a row-appear animation.

**Bottom: Integrity Summary row:**
- 3 compact stat boxes: Integrity Events Total / High Severity / Requiring Review.
- `"View Integrity Report"` link.

---

### SCR-07 — Drive → Candidate List

**Layout:** AppShell. Drive breadcrumb. Tab: Candidates active.

**Content:**
- FilterBar: Search + Stage filter + Score range filter + Sort.
- Table columns: Checkbox | Candidate Name + Avatar | Stage badge | Score | Interviews | Last Activity | Actions.
- Row actions: View, Send Reminder, Move Stage, Flag.
- Bulk action bar appears when rows are selected: `"Send Reminder"` / `"Move Stage"` / `"Export"`.
- Clicking a row opens Drawer with CandidateRow summary + `"Open Full Profile"` button.

---

### SCR-08 — Candidate 360

**Layout:** AppShell, SplitPane layout.

**Left rail (sticky, 280px):**
- Candidate avatar (initials), name, email, Drive name, Stage badge.
- Navigation anchors: Summary / Interview / Competencies / Transcript / Integrity / Notes.
- Action buttons: Advance Stage / Reject / Schedule Next / Add Note.

**Main content (scrollable):**

**Section: Summary**
- Role applied for, Drive, date completed, overall score (`data-lg` prominent, color-coded).
- 2–3 sentence AI-generated summary of candidate performance. Label clearly: `"AI Summary — verify with transcript"`. Not decorated. Just a muted label.
- Quick stats: Time in interview, Questions answered, Code submitted (if applicable).

**Section: Competency Scores**
- CompetencyGrid: each row is a competency (e.g., Problem Solving, Communication, Technical Accuracy), with ScoreBar, numeric score, evidence count as a link.

**Section: Interview Playback**
- Interview metadata (date, duration, model used).
- TranscriptBlock list: alternating AI question / Candidate response blocks. Each block: timestamp, text. Candidate blocks have audio playback button (plays original audio clip).

**Section: Integrity**
- IntegrityEvent list. Severity filter. Each event expandable to show screenshot or timestamp evidence.

**Section: Recruiter Notes**
- RecruiterNote list. `"Add Note"` button at top. Inline edit.

---

### SCR-09 — Interview Configuration

**Layout:** AppShell. Tab within Drive: the interview config view for an existing drive's interview setup.

**Content:**
- Question Bank selection panel: search + filter + add questions to the interview pool.
- Section configuration: ordered list of interview sections, each draggable to reorder. Each section: name, question count, weight, required/optional toggle.
- Advanced: follow-up depth, interruption handling, silence detection settings.

---

### SCR-10 — Interview Scheduling

**Layout:** AppShell.

**Content:**
- Calendar view (month/week) showing scheduled interview slots.
- Slot creation: date range picker, time windows, timezone selector.
- Candidate assignment: assign specific candidates to specific slots or leave open.

---

### SCR-11 — Candidate Invitation

**Layout:** AppShell. Modal or Drawer for add/edit.

**Content:**
- Invitation list table: candidate email, status (Pending / Sent / Opened / Started / Completed / Expired), invite date, expiry date.
- Bulk upload CSV button.
- Individual invite form in Drawer: email, name (optional), custom message (optional).
- Invitation email preview panel.

---

### SCR-12 — Candidate Entry & Verification

**Layout:** CandidateShell. Minimal. No sidebar. Top: Autergo wordmark + company name.

**Content:** Centered single card (max 480px wide).
- Company name + role applied for (from token).
- `"Welcome, [name]."` if name is in token.
- Brief explanation of what will happen (3–4 bullet points).
- If identity verification is required: photo upload or webcam capture step.
- Primary CTA: `"Continue to Device Check"`.

**Character:** Calm and professional. Candidates may be nervous. Large readable text. No dense technical language.

---

### SCR-13 — Device Check

**Layout:** CandidateShell. Stepper showing `Device Check → Interview → Complete`.

**Content:** Centered card, max 520px.

**DeviceCheckItem list:**
1. Microphone — `"Checking..."` → `"Detected: [device name]"` (pass) / `"No microphone found"` (fail + help link).
2. Browser compatibility — `"Chrome 118 — Supported"` (pass) / `"Firefox 114 — Limited support"` (warning).
3. Internet connection — Latency test result: `"Excellent (< 50ms)"` / `"Poor (> 500ms)"`.
4. Quiet environment — Manual confirmation toggle.

Each item transitions from checking spinner → pass/warning/fail with a smooth status icon swap.

Primary CTA appears only when all critical checks pass: `"Begin Interview"`.

---

### SCR-14 — Voice Interview

**Layout:** Full-screen. `--color-dark-base` background. No sidebar. Minimal top bar with: Autergo wordmark (left), interview progress indicator (center), connection status (right). The content is the interview — not the interface.

**Primary content area (centered, max 640px):**

**InterviewStateIndicator:**
The interview state is the visual centerpiece. Six states with distinct treatment:

| State | Visual |
| :--- | :--- |
| `Idle` | Thin horizontal center line. Autergo wordmark faintly visible. |
| `Listening` | Microphone icon (Phosphor, solid). Soft slow pulse on the icon (opacity 0.7→1, 1.5s, ease-in-out, loop). Caption: `"Listening..."`. |
| `Candidate Speaking` | AudioVisualizer active. 5 vertical bars, heights driven by Web Audio API amplitude. `caption-strong`: `"Speaking — your microphone is on"`. |
| `AI Speaking` | AudioVisualizer in a different color (primary blue tint bars). Caption: `"Autergo is speaking"`. |
| `Processing` | Thin horizontal progress bar, `--ease-linear`, indeterminate. Caption: `"Processing..."`. |
| `Error` | Error icon (Phosphor WarningCircle). Error message. Retry + Support actions. |
| `Complete` | Checkmark (Phosphor CheckCircle). `"Interview complete."` heading. |

**Below state indicator:**
- Question context card: current question number out of total sections (not individual question count if adaptive). Question topic label (e.g., `"Problem Solving — Q3"`).
- Session info bar (very bottom): elapsed time / connection indicator.

**AudioVisualizer detail:**
- 5 bars, each `width: 4px`, `border-radius: 2px`, gap `6px`. 
- Heights: driven by Web Audio API `AnalyserNode.getByteFrequencyData()`, mapped to 12px–48px range.
- When muted or silent: all bars at minimum height (12px), animated to a gentle uniform slow pulse.
- `--ease-linear` transitions, `50ms` interval updates.
- Colors: `--color-dark-ink-muted` default, primary blue tint when AI speaking.
- Respects `prefers-reduced-motion`: when reduced motion is set, bars are static at mid-height.

**Mute control:** Single mute button, bottom center. Clear icon swap (mic-on / mic-off). When muted, bars show muted state and a prominent muted indicator appears. No confirmation needed.

**Design principle for this screen:** The candidate is in a focused state. Remove every element that is not essential. The interview itself — the state, the question, the microphone — is the product. The UI disappears.

---

### SCR-15 — Interview Complete

**Layout:** CandidateShell. `--color-canvas`.

**Content:** Centered card.
- CheckCircle icon (Phosphor, not animated excessively). Heading: `"Interview Submitted."`.
- 2-sentence description: what happens next (recruiter review, timeline if known).
- If B2C / practice: `"View Your Feedback"` primary button.
- If B2B guest: `"You may close this window."` instruction.
- No gamification. No confetti. No stars. Professional closure.

---

### SCR-16 — Recruiter Evaluation View

**Layout:** AppShell, SplitPane.

**Left:** Candidate list for the drive (compact rows, stage badge, score).

**Right (main):** 
- Selected candidate's competency scores editable by recruiter (override AI score with comment).
- Evaluation form: Pass / Hold / Reject decision. Text field for evaluator notes.
- Evidence panel: shows specific transcript segments cited for each competency score.
- Submit Evaluation button.

---

### SCR-17 — Candidate Report (Recruiter View)

**Layout:** AppShell.

**Content:**
- Report header: Candidate name, role, drive, completion date, overall score (large, color-coded), AI recommendation (Pass / Hold / Reject badge).
- Section: Executive Summary — 3–4 sentences.
- Section: Competency breakdown — CompetencyGrid with evidence citations.
- Section: Interview quality indicators — talk time ratio, follow-up depth, coherence score (these are metadata, not deceptive AI scores).
- Section: Transcript (collapsible). TranscriptBlock list.
- Section: Integrity Events (collapsible). IntegrityEvent list.
- Action bar (sticky): `"Advance"` / `"Hold"` / `"Reject"` + `"Share Report"` + `"Print"`.

**Design principle:** Scores without evidence are meaningless. Every score in this report has a `"See evidence"` inline link that jumps to the relevant transcript block. Trust is built through traceability.

---

### SCR-18 — Candidate Report (Candidate-Facing)

**Layout:** CandidateShell (clean, minimal). For B2C/practice candidates only.

**Content:** Simplified version of SCR-17 without recruiter-facing decision fields.
- Overall score + brief narrative.
- Competency feedback per section.
- Suggested improvement areas.
- Transcript access (optional per drive config).
- `"Practice Again"` CTA if B2C.

---

### SCR-19 — Question Bank

**Layout:** AppShell.

**Content:**
- FilterBar: Search + Category + Difficulty + Type (Behavioral / Technical / Situational).
- Table: Question text (truncated), Category, Difficulty, Used in (N drives), Actions.
- Create/Edit in Drawer: question text, category, difficulty, expected answer guidance, follow-up prompts, tags.

---

### SCR-20 — Settings

**Layout:** AppShell. Left settings navigation + right content area.

**Tabs:** Company Profile / Team / Billing / Notifications / Integrations / API Keys.

Each tab is a form section with clear labels, grouped fields, save button fixed to bottom or at section level. No giant single-page form.

---

### SCR-21 — Super Admin Dashboard

**Layout:** AppShell (separate admin shell, distinct from recruiter portal). Dark variant option.

**Content:**
- Platform-wide KPI strip: Total Companies / Total Interviews This Month / System Uptime / Active AI Sessions.
- Tenant table: Company name, plan, last active, interview count, status, actions.
- AI Provider health panel: status per provider (LLM, STT, TTS), error rates, latency P95.
- Feature flags panel: toggle list with description + enabled/disabled toggle.
- Recent audit log list.

---

## 8. Responsive Behavior

### 8.1 Recruiter Portal Breakpoints

| Breakpoint | Sidebar | Layout |
| :--- | :--- | :--- |
| ≥ 1280px | Persistent full sidebar (240px) | Full 2-column layouts |
| 1024–1279px | Icon-only rail (64px) | Tables may compress to fewer visible columns |
| 768–1023px | Hidden, toggle-accessible drawer | Single column main content |
| < 768px | Drawer (hamburger trigger) | Tables become scrollable cards or stacked rows |

### 8.2 Candidate Surface

The candidate flow is the most mobile-critical surface (candidates may join from a phone).

- All candidate screens support 375px minimum width.
- Touch targets minimum 44×44px.
- The voice interview screen must remain functional at 375px. The AudioVisualizer compresses gracefully.
- Device Check items stack vertically on mobile.

### 8.3 Table Responsiveness

- Priority columns: Name, Status, Score, Actions. Always visible.
- Secondary columns: hide behind a `"+"` column expander on mobile.
- Alternative: horizontal scroll within a `overflow-x: auto` container with a visible shadow on the right edge indicating scrollable content.

---

## 9. Accessibility Requirements

All screens must meet WCAG 2.1 AA as a minimum.

| Requirement | Implementation |
| :--- | :--- |
| Color contrast | All text ≥ 4.5:1 (normal), ≥ 3:1 (large/bold). Verify against all token combinations. |
| Keyboard navigation | Full tab order. Modals trap focus. Dropdowns navigable with arrow keys. ESC closes all overlays. |
| Focus indicators | Visible 2px solid `--color-primary` outline on all focusable elements. Never `outline: none` without a visible custom replacement. |
| Semantic HTML | `<nav>`, `<main>`, `<header>`, `<aside>`, `<section>`, `<button>`, `<a>` used correctly. |
| ARIA labels | All icon-only buttons have `aria-label`. Status indicators have `role="status"`. Live regions for real-time updates: `aria-live="polite"`. |
| Form errors | Error messages are associated via `aria-describedby`. Fields in error state have `aria-invalid="true"`. |
| Screen readers | Decorative elements have `aria-hidden="true"`. AudioVisualizer has an accessible text equivalent describing the current state. |
| Reduced motion | All CSS transitions and JS animations respect `prefers-reduced-motion: reduce`. InterviewStateIndicator uses opacity-only transitions when motion is reduced. |

---

## 10. Performance Requirements

| Metric | Target |
| :--- | :--- |
| Largest Contentful Paint (LCP) | < 2.5s on 4G |
| Cumulative Layout Shift (CLS) | < 0.1 |
| First Input Delay (FID) | < 100ms |
| Bundle size | No JS framework overhead. Vanilla JS modules. |
| Font loading | `font-display: swap`. Subset to Latin characters only. |
| Images | WebP format. Lazy-load below fold. Explicit `width` and `height` attributes to prevent CLS. |
| Animations | CSS-driven where possible. JS animations batched in `requestAnimationFrame`. AudioVisualizer updates capped at 30fps. |
| Tailwind CSS | Production build purges unused classes. No CDN play mode in production. |

---

## 11. Technology Directives

### 11.1 Approved Stack

Per `07-Technology-Decision-Matrix.md` and existing implementation:

| Layer | Technology | Notes |
| :--- | :--- | :--- |
| Markup | HTML5 | Semantic, accessible |
| Styling | Tailwind CSS + CSS custom properties for design tokens | Tailwind config extends the token system |
| Scripting | Vanilla JavaScript (ES2022 modules) | No React, Vue, or Angular |
| Charts | Chart.js | Lightweight, no framework dependency |
| Icons | Phosphor Icons (CDN) | Regular + Duotone weights. No decorative AI icons. |
| Font | Inter (Google Fonts, variable) | As per DESIGN.md SF Pro substitute guidance |
| Audio | Web Audio API (native) | AudioVisualizer, amplitude detection |
| WebRTC | LiveKit JS SDK | Voice interview transport |
| Motion | CSS animations + Web Animations API | No GSAP in portal. GSAP ScrollTrigger permitted for landing page only. |

### 11.2 File Structure

```
frontend/
├── index.html                  # Landing page (SCR-01)
├── login.html                  # Recruiter auth (SCR-02)
├── portal/
│   ├── dashboard.html          # SCR-03
│   ├── drives.html             # SCR-04
│   ├── drive-create.html       # SCR-05
│   ├── drive-overview.html     # SCR-06
│   ├── drive-candidates.html   # SCR-07
│   ├── candidate-360.html      # SCR-08
│   ├── interview-config.html   # SCR-09
│   ├── scheduling.html         # SCR-10
│   ├── invitations.html        # SCR-11
│   ├── evaluation.html         # SCR-16
│   ├── report.html             # SCR-17
│   ├── question-bank.html      # SCR-19
│   └── settings.html           # SCR-20
├── candidate/
│   ├── entry.html              # SCR-12
│   ├── device-check.html       # SCR-13
│   ├── interview.html          # SCR-14
│   ├── complete.html           # SCR-15
│   └── report.html             # SCR-18
├── admin/
│   └── dashboard.html          # SCR-21
├── assets/
│   ├── css/
│   │   ├── tokens.css          # Design token CSS custom properties
│   │   ├── base.css            # Reset + base typography
│   │   └── animations.css      # Keyframe definitions
│   ├── js/
│   │   ├── components/         # Component JS modules
│   │   ├── pages/              # Page-specific JS
│   │   └── lib/                # Shared utilities
│   └── images/
│       └── product/            # Product screenshots for landing page
├── components/                 # HTML component partials (reference/documentation)
├── layouts/                    # HTML layout partials
└── tailwind.config.js
```

### 11.3 Tailwind Configuration Directive

The Tailwind config must extend the default theme with Autergo design tokens. Design tokens defined in `assets/css/tokens.css` as CSS custom properties must be referenced in `tailwind.config.js` so they are accessible as Tailwind utilities.

```javascript
// tailwind.config.js (abbreviated)
module.exports = {
  content: ['./**/*.html', './assets/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        canvas: 'var(--color-canvas)',
        'canvas-subtle': 'var(--color-canvas-subtle)',
        ink: 'var(--color-ink)',
        'ink-secondary': 'var(--color-ink-secondary)',
        'ink-muted': 'var(--color-ink-muted)',
        border: 'var(--color-border)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        'dark-base': 'var(--color-dark-base)',
        'dark-surface': 'var(--color-dark-surface)',
        'dark-ink': 'var(--color-dark-ink)',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        mono: 'var(--font-mono)',
      },
      borderRadius: {
        xs: 'var(--radius-xs)',
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
        pill: 'var(--radius-pill)',
      },
      transitionDuration: {
        micro: 'var(--duration-micro)',
        fast: 'var(--duration-fast)',
        base: 'var(--duration-base)',
        slow: 'var(--duration-slow)',
      },
    },
  },
}
```

---

## 12. Design Review Gate

Before implementation of each screen, the following checklist must be verified:

### Pre-Implementation Checklist

- [ ] Screen is in the approved screen inventory (Section 5)
- [ ] Layout component is identified (AppShell / CandidateShell / LandingNav)
- [ ] All components used are in the component inventory (Section 6) or documented as new
- [ ] Color usage follows Section 3.1 — no undocumented colors
- [ ] Typography uses only tokens from Section 3.2
- [ ] Animations follow the catalogue in Section 3.6
- [ ] Empty state is designed
- [ ] Loading state is designed (skeleton or spinner as appropriate)
- [ ] Error state is designed
- [ ] Responsive behavior at 375px, 768px, 1024px, and 1280px is accounted for
- [ ] Accessibility requirements from Section 9 are considered
- [ ] No decorative AI imagery (robots, brains, sparkles, glowing orbs)
- [ ] DESIGN.md rules are not violated

### Post-Implementation Visual Audit

For each screen, verify:
- [ ] Alignment — all elements snap to the spacing grid
- [ ] Contrast — text passes 4.5:1
- [ ] Typography — hierarchy is clear, no rogue font sizes
- [ ] Consistency — screen feels like it belongs to the same product as adjacent screens
- [ ] State coverage — default, hover, loading, empty, error states all exist
- [ ] Motion — animations work, feel purposeful, don't distract
- [ ] Responsive — no overflow at any tested breakpoint
- [ ] DESIGN.md compliance verified

---

## 13. Implementation Phases

### Phase 1 — Foundation (prerequisite for all screens)

1. `tokens.css` — all design token CSS custom properties
2. `base.css` — reset, typography base, body defaults
3. `animations.css` — all keyframe definitions
4. `tailwind.config.js` — token integration
5. Primitive components: Button, Input, Select, Badge, Avatar, Spinner, Skeleton, Progress
6. Layout components: AppShell, CandidateShell, LandingNav

### Phase 2 — Core Recruiter Screens (P1)

1. SCR-01 Landing Page
2. SCR-02 Login
3. SCR-03 Dashboard
4. SCR-04 Drive List
5. SCR-05 Create Drive
6. SCR-06 Drive Overview
7. SCR-07 Candidate List
8. SCR-08 Candidate 360

### Phase 3 — Core Candidate Screens (P1)

1. SCR-12 Candidate Entry
2. SCR-13 Device Check
3. SCR-14 Voice Interview ← highest complexity
4. SCR-15 Interview Complete

### Phase 4 — Recruiter Deep Screens (P1)

1. SCR-16 Evaluation
2. SCR-17 Candidate Report

### Phase 5 — Supporting Screens (P2)

1. SCR-09 Interview Configuration
2. SCR-10 Scheduling
3. SCR-11 Invitations
4. SCR-18 Candidate Report (candidate-facing)
5. SCR-19 Question Bank
6. SCR-20 Settings
7. SCR-21 Super Admin

---

## 14. Anti-Pattern Reference

This section documents what must not be built, as a permanent reference during implementation.

| Anti-Pattern | Why It's Forbidden | Compliant Alternative |
| :--- | :--- | :--- |
| Glowing purple/blue neon UI | Looks like a crypto dashboard or gaming UI; erodes enterprise trust | Deep navy primary on white/near-white canvas |
| Glassmorphism blobs | Decorative, not informative; distracts from data | Clean flat cards with 1px border |
| Robot / brain / circuit-board icons | AI cliché; communicates nothing about the actual product | Purposeful Phosphor icons for actual actions |
| `"AI POWERED"` badges on every panel | Meaningless; makes the product look like a demo | Let the product behavior demonstrate intelligence |
| Sparkle icons (✨) | Overused AI trope | Remove entirely |
| Giant colorful score donuts | Gamification aesthetic; inappropriate for enterprise HR | Horizontal ScoreBar with numeric value |
| `"Something went wrong."` errors | Not actionable | Specific error message + retry + support link |
| Oversized empty-state illustrations | Generic, generated-looking | Plain text + icon + single CTA |
| Constant infinite animations | Distracting, accessibility violation | Purposeful state-change animations only |
| Every card having a drop shadow | Visual noise; everything appears elevated | Border-only flat cards; shadows for modals/dropdowns only |
| Nested cards inside cards inside cards | Spatial confusion | Clear containment hierarchy using spacing and color |
| Random gradient backgrounds | Decorative; ages poorly | Solid surface colors; alternating light/dark tiles on landing |
| Bold text everywhere | Hierarchy collapse | Only headings and `body-strong` inline emphasis are bold |

---

## 15. DESIGN.md Compliance Summary

The following rules from `DESIGN.md` are directly applied in this specification:

| DESIGN.md Rule | Application in This Spec |
| :--- | :--- |
| Single action-blue primary (`#0066cc` adapted to `#1a56db` for Autergo's deeper tone) | `--color-primary` carries all interactive elements. No second accent color. |
| Negative letter-spacing at display sizes | Applied in Section 3.2 typography scale from `display` through `heading-sm`. |
| Body copy at 17px | `body-lg` token is 17px. Used for all primary reading text. |
| Shadow reserved for product imagery | Product screenshots in landing page use `--elevation-product`. Cards use flat border only. |
| `transform: scale(0.97)` on active buttons | Applied in Button component spec. |
| Section rhythm: light ↔ dark tile alternation | Landing page sections alternate `--color-canvas` and `--color-canvas-subtle` tiles with a single `--color-dark-base` dark section. |
| No decorative gradients | Zero gradient tokens defined. |
| Weight ladder 400 / 500 / 600 | Section 3.2 uses exactly this ladder. Weight 500 reserved for labels only. |
| `rounded-pill` for primary CTAs | Primary buttons and search inputs use `--radius-pill`. |
| Inter as SF Pro substitute | Font stack declared in Section 3.2 per DESIGN.md guidance. Negative tracking applied. |

---

*End of Document*
