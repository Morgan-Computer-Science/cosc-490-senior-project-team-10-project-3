# Design System Document: The Digital Scholar

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Digital Scholar."** 

This aesthetic moves away from the sterile, "template-first" look of standard educational portals. Instead, it captures the intersection of Morgan State’s historic academic prestige and the cutting-edge logic of Computer Science. We achieve this through "Organic Brutalism"—a style that uses high-contrast typography and a rigid, tech-forward grid, but softens the experience through sophisticated tonal layering and glassmorphism. By utilizing intentional asymmetry and deep, saturated color fields, we create an interface that feels authoritative yet innovative, perfectly suited for a high-performance CS student chatbot.

---

## 2. Colors & Surface Architecture
This system leverages a sophisticated palette anchored in Morgan State’s legacy Navy and Orange, reimagined through a modern Material 3-inspired tonal range.

### The "No-Line" Rule
To maintain a high-end, editorial feel, **1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined solely through background color shifts or subtle tonal transitions. For example, a `surface-container-low` section sitting on a `surface` background creates a natural, modern division without the visual clutter of a line.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of frosted glass.
- **Base Layer:** `surface` (#f9f9f9)
- **Content Blocks:** `surface-container` (#eeeeee) or `surface-container-low` (#f3f3f3)
- **Elevated Interactive Elements:** `surface-container-highest` (#e2e2e2)

### The "Glass & Gradient" Rule
For floating elements, such as chatbot response bubbles or navigation overlays, use **Glassmorphism**. Apply a semi-transparent `surface` color with a `backdrop-blur` of 12px to 20px. 
- **Signature Texture:** Use a subtle linear gradient for primary actions, transitioning from `primary` (#000d2f) to `primary_container` (#00205b). This provides a "soul" and depth that flat hex codes cannot achieve.

---

## 3. Typography
Our typography pairing is a dialogue between "Tech" and "Humanity."

*   **Display & Headlines (Space Grotesk):** This typeface represents the "Tech-Forward" aspect. Its geometric terminals and wide apertures give it a programmed, computational feel. Use `display-lg` to `headline-sm` for high-impact editorial moments.
*   **Body & Titles (Manrope):** A versatile sans-serif that balances modernism with readability. It handles dense academic information and chatbot dialogue with ease.

**The Hierarchy Strategy:**
- **Contrast is Key:** Pair a `display-md` headline with a `body-md` description to create a sophisticated, wide-scale contrast that feels like a premium publication.
- **Labeling:** Use `label-md` in all-caps with 0.05em tracking for metadata or small tech-specs to reinforce the "engineered" aesthetic.

---

## 4. Elevation & Depth
In this design system, depth is a function of light and layer, not structural dividers.

*   **The Layering Principle:** Achieve hierarchy by "stacking." Place a `surface-container-lowest` card on a `surface-container-low` section to create a soft, natural lift.
*   **Ambient Shadows:** For floating chatbot components, use extra-diffused shadows. 
    *   *Specs:* Blur: 32px, Y: 12px, Color: `on_surface` at 4% opacity.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility, use the `outline_variant` token at **20% opacity**. Never use 100% opaque, high-contrast borders.
*   **Depth through Glass:** Use semi-transparent `primary_container` (Navy) with a blur for student chat bubbles to make the UI feel integrated into the "academic atmosphere."

---

## 5. Components

### Buttons
*   **Primary:** Uses the `secondary_container` (Orange #fc6700) with `on_secondary_container` text. Apply `rounded-md` (0.375rem).
*   **Secondary:** Ghost style. No background, `outline_variant` (at 20% opacity) border, and `primary` text.
*   **State Logic:** On hover, primary buttons should shift 10% deeper in saturation; secondary buttons should gain a subtle `surface-container-high` background.

### Chat Bubbles (The Core Component)
*   **Student Input:** `primary_container` (Navy) with `on_primary` text. Aligned right.
*   **AI/Bot Output:** Glassmorphic `surface-container-lowest` with a 15% opacity blur. Aligned left.
*   **Layout:** No dividers between messages. Use 12px vertical spacing between bubbles and 24px between different message clusters.

### Input Fields
*   **Style:** Minimalist. Underline-only or subtle `surface-container` background. 
*   **Active State:** When focused, the label should animate to `label-sm` in `secondary` (Orange), and the indicator line should grow to 2px.

### Cards & Lists
*   **Rule:** Forbid divider lines. Separate list items using `surface_container_low` hover states or strictly defined vertical white space (16px - 24px).
*   **Nesting:** Place `surface-container-lowest` cards inside a `surface-dim` container for maximum legibility.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical layouts. For example, a heavy headline on the left with a wide-margin body text on the right.
*   **Do** prioritize "Breathing Room." Let the `surface` color dominate to prevent the navy/orange from feeling heavy or "retro."
*   **Do** use `secondary` (Orange) sparingly as a "Laser Focus" color—only for critical CTAs or status alerts.

### Don’t:
*   **Don't** use standard drop shadows (e.g., #000 at 25%). It breaks the sophisticated academic tone.
*   **Don't** use 1px solid dividers. If you feel you need a line, use a background color change instead.
*   **Don't** use fully rounded (pill) buttons for everything. Stick to `rounded-md` or `rounded-lg` to maintain a structured, "engineered" feel.
*   **Don't** crowd the interface. Academic information is dense; the UI must be light.