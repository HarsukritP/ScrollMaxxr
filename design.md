# TikTok FYP Calibrator - Design Specification

**Last Updated:** November 9, 2025

---

## Design Philosophy

### Core Principles

1. **Fun, Slightly Irreverent**
   - Matches Go On Hacks vibe
   - Not too serious, not too silly
   - Personality without being unprofessional
   - Playful emojis in UI (🎯, 🔥, 🤖)

2. **Dark Mode First**
   - Developers love dark mode
   - Easier on eyes during hackathon demos
   - Purple/pink gradient accents pop on dark
   - Light mode as optional enhancement

3. **Minimal but Polished**
   - Clean, uncluttered interfaces
   - Every element serves a purpose
   - Generous whitespace
   - Focus on content, not decoration

4. **Real-time Feedback is Key**
   - Instant visual feedback for every action
   - Smooth animations (not jarring)
   - Progress indicators everywhere
   - Users always know what's happening

5. **Mobile-Responsive Mindset**
   - Even though it's a desktop extension
   - Webapp must work on mobile
   - Flexible layouts
   - Touch-friendly button sizes

---

## Chrome Extension UI Design

### Color Palette

#### Dark Theme (Primary)

```css
/* Background Colors */
--bg-primary: #0a0a0a       /* Main background */
--bg-secondary: #1a1a1a     /* Cards, containers */
--bg-tertiary: #2a2a2a      /* Hover states, elevated elements */

/* Accent Colors */
--accent-primary: #8b5cf6   /* Purple - primary actions, highlights */
--accent-secondary: #ec4899 /* Pink - secondary accents, gradients */
--accent-gradient: linear-gradient(135deg, #8b5cf6, #ec4899)

/* Text Colors */
--text-primary: #ffffff     /* Main text */
--text-secondary: #a1a1aa   /* Muted text, labels */
--text-tertiary: #71717a    /* Disabled, placeholders */

/* Semantic Colors */
--success: #10b981          /* Success states, positive actions */
--warning: #f59e0b          /* Warnings, caution */
--error: #ef4444            /* Errors, destructive actions */
--info: #3b82f6             /* Information, neutral alerts */

/* UI Colors */
--border: #2a2a2a           /* Borders, dividers */
--shadow-sm: rgba(0, 0, 0, 0.1)
--shadow-md: rgba(0, 0, 0, 0.2)
--shadow-lg: rgba(139, 92, 246, 0.3)  /* Accent shadow */
```

#### Light Theme (Optional Phase 2)

```css
/* Background Colors */
--bg-primary-light: #ffffff
--bg-secondary-light: #f5f5f5
--bg-tertiary-light: #e5e5e5

/* Accent Colors (same) */
--accent-primary-light: #7c3aed
--accent-secondary-light: #db2777

/* Text Colors */
--text-primary-light: #0a0a0a
--text-secondary-light: #52525b
--text-tertiary-light: #a1a1aa
```

---

### Extension Popup Layout

#### Dimensions
- **Width:** 320px (standard extension width)
- **Height:** 480px minimum (expandable)
- **Padding:** 20px container padding
- **Gap:** 12-20px between sections

#### Visual Hierarchy

```
┌────────────────────────────────────┐
│ 🎯 FYP Calibrator          [⚙️]   │  ← Header (60px)
│ Optimize your scroll               │
├────────────────────────────────────┤
│ Select Content Categories:         │  ← Category Section
│                                    │
│ [☐ 🔥 Thirst Traps] [☐ 😂 Skits]  │
│ [☐ 🧠 Brainrot    ] [☐ 💻 Tech ]  │  ← 2-column grid
│ [☐ 📰 News        ] [☐ ✂️ Edits]  │
│ [☐ 📸 Photography ]                │
│                                    │
├────────────────────────────────────┤
│ ┌────────────────────────────────┐ │  ← Primary CTA
│ │   Start Calibration ▶          │ │
│ └────────────────────────────────┘ │
│                                    │
├────────────────────────────────────┤
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━ 65%   │  ← Progress Bar
│                                    │
│ 📊 Videos: 23    ✅ Matches: 15   │  ← Stats Grid
│ 📈 Rate: 65%     ⚡ Status: Active │  (2x2)
│                                    │
└────────────────────────────────────┘
│ Made for Go On Hacks 2025          │  ← Footer
└────────────────────────────────────┘
```

---

### Component Specifications

#### 1. Header Section

**Design:**
```
┌────────────────────────────────────┐
│ 🎯 FYP Calibrator          [⚙️]   │
│ Optimize your scroll               │
└────────────────────────────────────┘
```

**Specifications:**
- **Title Font:** 24px, weight 800, line-height 1.2
- **Icon:** 48×48px emoji or SVG
- **Tagline:** 14px, weight 400, color: `--text-secondary`
- **Settings Icon:** 20×20px, top-right corner
- **Spacing:** 16px bottom margin

**CSS:**
```css
.header {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
}

.header h1 {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tagline {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.settings-icon {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.settings-icon:hover {
  opacity: 1;
}
```

---

#### 2. Category Selection

**Design:**
```
┌─────────────────────────────────────┐
│ Select Content Categories:          │
│                                     │
│ ┌──────────────┐  ┌──────────────┐ │
│ │☐ 🔥 Thirst  │  │☐ 😂 Skits   │ │
│ │   Traps     │  │             │ │
│ └──────────────┘  └──────────────┘ │
│ ┌──────────────┐  ┌──────────────┐ │
│ │☐ 🧠 Brainrot│  │☐ 💻 Tech    │ │
│ └──────────────┘  └──────────────┘ │
└─────────────────────────────────────┘
```

**Specifications:**
- **Grid:** 2 columns, 8px gap
- **Card Size:** ~145px width, auto height
- **Padding:** 12px inside each card
- **Border Radius:** 8px
- **Background:** `--bg-secondary`
- **Hover:** Scale 1.02, background: `--bg-tertiary`
- **Checked:** Border 2px `--accent-primary`, background: `rgba(139, 92, 246, 0.1)`

**Category Labels:**
- 🔥 Thirst Traps
- 😂 Skits
- 🧠 Brainrot
- 💻 Tech
- 📰 News
- ✂️ Edits
- 📸 Photography

**CSS:**
```css
.categories {
  margin-bottom: 20px;
}

.categories h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.category-item:hover {
  background: var(--bg-tertiary);
  transform: scale(1.02);
}

.category-item:active {
  transform: scale(0.98);
}

.category-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--accent-primary);
}

.category-item.checked {
  background: rgba(139, 92, 246, 0.1);
  border-color: var(--accent-primary);
}

.category-item.checked span {
  color: var(--accent-primary);
  font-weight: 600;
}

.category-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

#### 3. Control Buttons

**Design:**
```
┌─────────────────────────────────┐
│   Start Calibration ▶          │  ← Primary (gradient)
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   Stop ⏹                        │  ← Danger (shown when active)
└─────────────────────────────────┘
```

**Specifications:**

**Primary Button:**
- **Width:** 100% (280px)
- **Height:** 48px
- **Border Radius:** 8px
- **Background:** Linear gradient 135deg, `#8b5cf6` → `#ec4899`
- **Font:** 16px, weight 600
- **Shadow:** `0 4px 12px rgba(139, 92, 246, 0.3)`
- **Hover:** Translate Y -2px, shadow: `0 6px 16px rgba(139, 92, 246, 0.4)`
- **Active:** Translate Y 0, shadow: `0 2px 8px rgba(139, 92, 246, 0.3)`

**Danger Button:**
- **Background:** Solid `--error`
- **Margin Top:** 8px
- **Same dimensions as primary**

**CSS:**
```css
.controls {
  margin-bottom: 20px;
}

.btn {
  width: 100%;
  height: 48px;
  padding: 0 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: var(--error);
  color: white;
  margin-top: 8px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: #dc2626;
  transform: translateY(-2px);
}

/* Loading state */
.btn.loading {
  position: relative;
  color: transparent;
}

.btn.loading::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

#### 4. Progress Bar

**Design:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 65%
████████████████░░░░░░░░░░░░░
```

**Specifications:**
- **Height:** 8px
- **Width:** 100%
- **Border Radius:** 4px
- **Background:** `--bg-tertiary`
- **Fill:** Linear gradient 90deg, `#8b5cf6` → `#ec4899`
- **Animation:** Shimmer effect (pulse opacity)
- **Transition:** Width 0.5s ease

**CSS:**
```css
.progress-section {
  margin-bottom: 20px;
}

.progress-bar {
  height: 8px;
  width: 100%;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  animation: shimmer 2s ease-in-out infinite;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: slide 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

@keyframes slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
  margin-top: 4px;
}
```

---

#### 5. Stats Grid

**Design:**
```
┌──────────────┬──────────────┐
│ Videos       │ Matches      │
│ Processed    │ Found        │
│    23        │    15        │
├──────────────┼──────────────┤
│ Match        │ Status       │
│ Rate         │              │
│    65%       │   Active     │
└──────────────┴──────────────┘
```

**Specifications:**
- **Grid:** 2×2
- **Gap:** 12px
- **Card Padding:** 12px
- **Background:** `--bg-secondary`
- **Border Radius:** 8px
- **Label:** 11px, `--text-secondary`
- **Value:** 20px, weight 700, `--accent-primary`

**CSS:**
```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-primary);
  font-variant-numeric: tabular-nums;
}

.stat-value.success {
  color: var(--success);
}

.stat-value.warning {
  color: var(--warning);
}

.stat-value.error {
  color: var(--error);
}

/* Animated counter */
.stat-value.animating {
  animation: countUp 0.3s ease-out;
}

@keyframes countUp {
  from {
    transform: scale(1.2);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
```

---

#### 6. Messages / Alerts

**Design:**
```
┌─────────────────────────────────┐
│ ✅ Calibration complete!        │  ← Success
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ ⚠️  Please select a category    │  ← Warning
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ ❌ API error, retrying...       │  ← Error
└─────────────────────────────────┘
```

**Specifications:**
- **Padding:** 12px
- **Border Radius:** 8px
- **Font Size:** 14px
- **Margin:** 12px 0
- **Animation:** Slide in from top

**CSS:**
```css
.message {
  padding: 12px;
  border-radius: 8px;
  margin: 12px 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: slideIn 0.3s ease-out;
}

.message-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
  border: 1px solid var(--success);
}

.message-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
  border: 1px solid var(--warning);
}

.message-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
  border: 1px solid var(--error);
}

.message-info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--info);
  border: 1px solid var(--info);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

#### 7. Footer

**Design:**
```
─────────────────────────────────
Made for Go On Hacks 2025
```

**Specifications:**
- **Font Size:** 11px
- **Color:** `--text-secondary`
- **Text Align:** Center
- **Border Top:** 1px solid `--border`
- **Padding Top:** 16px
- **Margin Top:** 20px

**CSS:**
```css
.footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.footer small {
  font-size: 11px;
  color: var(--text-secondary);
}

.footer a {
  color: var(--accent-primary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer a:hover {
  color: var(--accent-secondary);
}
```

---

### Animations and Transitions

#### Celebration Animation

Triggered when calibration completes successfully:

```css
.celebration {
  animation: celebrate 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes celebrate {
  0%, 100% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.05) rotate(2deg);
  }
  50% {
    transform: scale(1.1) rotate(-2deg);
  }
  75% {
    transform: scale(1.05) rotate(1deg);
  }
}

/* Confetti effect (optional) */
.confetti {
  position: fixed;
  width: 10px;
  height: 10px;
  background: var(--accent-primary);
  animation: confettiFall 3s linear;
}

@keyframes confettiFall {
  to {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}
```

#### Loading States

```css
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--bg-tertiary);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-dots::after {
  content: '';
  animation: dots 1.5s steps(4, end) infinite;
}

@keyframes dots {
  0%, 20% { content: ''; }
  40% { content: '.'; }
  60% { content: '..'; }
  80%, 100% { content: '...'; }
}
```

---

## Next.js Webapp Design (Phase 2)

### Technology Stack

**Framework & Language:**
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript 5.0+
- **Runtime:** Node.js 18+

**Styling:**
- **CSS Framework:** Tailwind CSS 3.4+
- **Configuration:** JIT mode, custom theme
- **Plugins:** typography, forms, aspect-ratio

**Component Library:**
- **UI Library:** shadcn/ui (Radix primitives)
- **Components:** Button, Card, Checkbox, Progress, Badge, Dialog, Tabs, Accordion, Select, Input
- **Customization:** Full source control, Tailwind-styled

**Icons:**
- **Library:** Lucide React 0.294.0+
- **Style:** Stroke-based, 24px default
- **Usage:** `<Play />`, `<Pause />`, `<TrendingUp />`, `<Zap />`

**Animations:**
- **Library:** Framer Motion 10.0+
- **Usage:** Page transitions, scroll animations, micro-interactions

**Charts:**
- **Library:** Recharts 2.10+
- **Types:** Line charts, pie charts, bar charts
- **Styling:** Custom theme matching brand colors

**Fonts:**
- **Sans Serif:** Inter (from Google Fonts)
- **Monospace:** Fira Code (for code snippets)
- **Loading:** font-display: swap

**Deployment:**
- **Platform:** Vercel
- **Features:** Automatic deployments, preview URLs, edge functions

---

### Page Structure

#### Landing Page (`app/page.tsx`)

**Sections:**

1. **Hero Section**
   - Headline + subheadline
   - Demo video (autoplay, muted)
   - Primary CTA button
   - Secondary CTA (GitHub)

2. **How It Works** (3 steps)
   - Step 1: Select your vibe
   - Step 2: AI analyzes your feed
   - Step 3: Perfect FYP delivered
   - Visual: Animated diagram

3. **Features Grid** (6 features)
   - 7 Content Categories
   - AI-Powered Classification
   - Real-Time Progress
   - Time Saved Tracking
   - Privacy-First
   - Open Source

4. **Demo Section**
   - Before/after comparison
   - Live stats animation
   - Video walkthrough

5. **Stats Section**
   - Total videos processed (counter)
   - Average time saved
   - Happy users
   - Accuracy percentage

6. **FAQ Accordion**
   - "Is this against TikTok's TOS?"
   - "How accurate is the AI?"
   - "Does it cost money?"
   - "Is my data safe?"

7. **Footer**
   - Links: GitHub, Twitter, Contact
   - Copyright notice
   - Made with ❤️ for Go On Hacks

**Layout:**
```tsx
export default function HomePage() {
  return (
    <main>
      <HeroSection />
      <HowItWorksSection />
      <FeaturesGrid />
      <DemoSection />
      <StatsSection />
      <FAQSection />
      <CTASection />
      <Footer />
    </main>
  );
}
```

---

#### Dashboard Page (`app/dashboard/page.tsx`)

**Layout:**

```
┌─────────────────────────────────────────────┐
│ Sidebar │ Main Content                      │
│         │                                   │
│ [Home]  │ ┌─────────────────────────────┐ │
│ [Dash]  │ │ Quick Stats Cards           │ │
│ [Hist]  │ │ [23 Videos] [15 Matches]    │ │
│ [Sett]  │ └─────────────────────────────┘ │
│         │                                   │
│         │ ┌─────────────────────────────┐ │
│         │ │ Match Rate Over Time        │ │
│         │ │ [Line Chart]                │ │
│         │ └─────────────────────────────┘ │
│         │                                   │
│         │ ┌─────────────────────────────┐ │
│         │ │ Category Distribution       │ │
│         │ │ [Pie Chart]                 │ │
│         │ └─────────────────────────────┘ │
│         │                                   │
│         │ ┌─────────────────────────────┐ │
│         │ │ Recent Sessions Table       │ │
│         │ │ [Data Table]                │ │
│         │ └─────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Components:**
- Sidebar navigation
- Quick stats cards (4 metrics)
- Line chart (match rate over time)
- Pie chart (category distribution)
- Data table (recent sessions)
- Export button

---

### Component Library (shadcn/ui)

#### Installation Commands

```bash
# Initialize shadcn/ui
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add accordion
npx shadcn-ui@latest add select
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add table
```

#### Custom Theme Configuration

**File:** `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: '#8b5cf6',
          50: '#faf5ff',
          100: '#f3e8ff',
          500: '#8b5cf6',
          600: '#7c3aed',
        },
        secondary: {
          DEFAULT: '#ec4899',
          500: '#ec4899',
          600: '#db2777',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      animation: {
        'shimmer': 'shimmer 2s ease-in-out infinite',
        'slide-in': 'slideIn 0.3s ease-out',
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        slideIn: {
          from: { opacity: '0', transform: 'translateY(-10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
export default config
```

---

### Typography Scale

```css
/* Headings */
.text-h1 {
  font-size: 3rem;        /* 48px */
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.text-h2 {
  font-size: 2.25rem;     /* 36px */
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.01em;
}

.text-h3 {
  font-size: 1.875rem;    /* 30px */
  font-weight: 600;
  line-height: 1.4;
}

.text-h4 {
  font-size: 1.5rem;      /* 24px */
  font-weight: 600;
  line-height: 1.5;
}

/* Body */
.text-body-lg {
  font-size: 1.125rem;    /* 18px */
  font-weight: 400;
  line-height: 1.7;
}

.text-body {
  font-size: 1rem;        /* 16px */
  font-weight: 400;
  line-height: 1.6;
}

.text-body-sm {
  font-size: 0.875rem;    /* 14px */
  font-weight: 400;
  line-height: 1.5;
}

.text-caption {
  font-size: 0.75rem;     /* 12px */
  font-weight: 400;
  line-height: 1.4;
}
```

---

### Animation Guidelines

#### Framer Motion Variants

```tsx
// Fade in from bottom
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: 'easeOut' }
}

// Stagger children
const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}

// Scale on hover
const scaleOnHover = {
  hover: { scale: 1.05 },
  tap: { scale: 0.95 }
}

// Slide in from left
const slideInLeft = {
  initial: { opacity: 0, x: -50 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.4 }
}

// Usage
<motion.div
  variants={fadeInUp}
  initial="initial"
  animate="animate"
  whileHover="hover"
>
  Content
</motion.div>
```

---

### Responsive Breakpoints

```css
/* Tailwind breakpoints */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */

/* Usage in Tailwind */
.container {
  @apply w-full px-4;
  @apply sm:px-6;
  @apply md:px-8;
  @apply lg:max-w-7xl lg:mx-auto;
}
```

---

### Accessibility Requirements

#### WCAG 2.1 Level AA Compliance

- [ ] **Color Contrast:** ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- [ ] **Keyboard Navigation:** All interactive elements reachable via Tab
- [ ] **Focus Indicators:** Visible focus rings (2px, `--accent-primary`)
- [ ] **ARIA Labels:** All buttons/links have descriptive labels
- [ ] **Alt Text:** All images have meaningful alt text
- [ ] **Screen Reader:** Semantic HTML, proper heading hierarchy
- [ ] **Form Labels:** All inputs have associated labels
- [ ] **Error Messages:** Clear, descriptive error messages
- [ ] **Skip Links:** "Skip to main content" link

**CSS for Focus Indicators:**
```css
*:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
  border-radius: 4px;
}

button:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}
```

---

### Design Deliverables

#### 1. Extension Popup Mockup

**Format:** Figma or hand-drawn sketch  
**Views:**
- Default state (no selection)
- Categories selected
- Calibration in progress (50%)
- Calibration complete (success)
- Error state

---

#### 2. Webapp Landing Page Mockup

**Sections:**
- Hero (above fold)
- How it works
- Features
- Demo
- CTA

---

#### 3. Dashboard Mockup

**Views:**
- Main dashboard
- Session detail view
- Settings page

---

#### 4. Component Showcase

**Storybook or Static Page:**
- All buttons (primary, secondary, danger)
- All alerts (success, warning, error, info)
- Progress bars (0%, 50%, 100%)
- Cards
- Stats
- Forms

---

#### 5. Style Guide Document

**Contents:**
- Color palette (with hex codes)
- Typography scale
- Spacing system (4px grid)
- Border radius values
- Shadow values
- Animation timing functions

---

### Frontend File Structure

```
scrollmaxxr/
├── extension/
│   ├── manifest.json
│   ├── popup/
│   │   ├── index.html
│   │   ├── popup.js
│   │   └── styles.css
│   ├── content/
│   │   └── content.js
│   ├── background/
│   │   └── background.js
│   ├── assets/
│   │   ├── icons/
│   │   │   ├── icon16.png
│   │   │   ├── icon48.png
│   │   │   └── icon128.png
│   │   └── images/
│   │       └── demo.gif
│   └── utils/
│       ├── api.js
│       └── helpers.js
│
└── webapp/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── globals.css
    │   ├── dashboard/
    │   │   ├── layout.tsx
    │   │   └── page.tsx
    │   └── api/
    │       └── route.ts
    ├── components/
    │   ├── ui/              # shadcn components
    │   │   ├── button.tsx
    │   │   ├── card.tsx
    │   │   └── ...
    │   ├── hero.tsx
    │   ├── features.tsx
    │   ├── how-it-works.tsx
    │   ├── stats.tsx
    │   └── faq.tsx
    ├── lib/
    │   ├── utils.ts
    │   └── api.ts
    ├── public/
    │   ├── demo.mp4
    │   ├── og-image.png
    │   └── favicon.ico
    ├── styles/
    │   └── animations.css
    ├── tailwind.config.ts
    ├── next.config.js
    ├── package.json
    ├── tsconfig.json
    └── README.md
```

---

## Icon Set

### Extension Icons

**Source:** Lucide React or custom SVG

**Key Icons:**
- ▶ Play (start calibration)
- ⏹ Stop (stop calibration)
- ⚙️ Settings
- 📊 Stats
- ✅ Checkmark (success)
- ❌ Error
- 🔄 Refresh/Retry
- 📈 Trending Up
- ⚡ Zap (fast)
- 🎯 Target
- 🤖 Robot (AI)

---

## Branding

### Logo

**Concept:** Target emoji + robot/AI element  
**Primary:** 🎯 (Bullseye emoji)  
**Alternative:** Custom SVG logo with gradient

---

### Name

**Primary:** ScrollMaxxr  
**Alternative:** FYP Calibrator  
**Tagline:** "Optimize your scroll"

---

### Voice & Tone

**Voice:**
- Clever but not pretentious
- Technical but accessible
- Fun but professional

**Examples:**
- ✅ "Stop scrolling past content you hate"
- ✅ "Let AI train your FYP in 2 minutes"
- ❌ "Revolutionary paradigm-shifting solution"
- ❌ "Synergize your social media experience"

---

## Performance Guidelines

### Load Time Targets

- **Extension Popup:** < 100ms
- **Webapp First Paint:** < 1s
- **Webapp Interactive:** < 3s
- **API Response:** < 500ms (classification)

### Optimization Techniques

- [ ] Lazy load components (React.lazy)
- [ ] Image optimization (next/image)
- [ ] Code splitting (dynamic imports)
- [ ] CSS purging (Tailwind JIT)
- [ ] Font subsetting
- [ ] Compress images (WebP)
- [ ] Minimize bundle size

---

## Testing Checklist

### Visual Testing

- [ ] Works in Chrome (primary)
- [ ] Works in Firefox (secondary)
- [ ] Works in Edge (secondary)
- [ ] Responsive on mobile (webapp)
- [ ] Dark mode works correctly
- [ ] Light mode works correctly (optional)
- [ ] All animations smooth (60fps)
- [ ] No layout shifts (CLS < 0.1)

### Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader friendly
- [ ] Color contrast passes WCAG AA
- [ ] Focus indicators visible
- [ ] Alt text present
- [ ] Semantic HTML used

---

**Last Updated:** November 9, 2025

