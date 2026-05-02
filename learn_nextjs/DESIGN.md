---
name: Modern Adaptive
colors:
  primary: "#d97706"
  secondary: "#3f3f46"
  background: "#ffffff"
  foreground: "#1f2937"
  error: "#dc2626"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
  serif:
    fontFamily: Lora
  mono:
    fontFamily: JetBrains Mono
rounded:
  md: 10.4px
---

# Design System

## Overview

A modern, adaptive theme supporting both light and dark modes.
Built with OKLch color space for perceptually uniform color transitions.
Emphasizes clarity, accessibility, and visual hierarchy through color and typography.

## Colors

### Light Theme

- **Primary** (#d97706): CTAs, active states, key interactive elements (orange/amber)
- **Secondary** (#f5f5f5): Supporting UI, secondary actions, muted backgrounds
- **Background** (#ffffff): Page backgrounds
- **Foreground** (#1f2937): Primary text
- **Error** (#dc2626): Validation errors, destructive actions
- **Border**: Light grey for subtle separation

### Dark Theme

- **Primary** (#d97706): CTAs, active states (same orange/amber)
- **Secondary** (#3f3f46): Supporting UI, secondary actions
- **Background** (#1f2937): Page backgrounds
- **Foreground** (#fafafa): Primary text (off-white)
- **Error** (#b34747): Validation errors, destructive actions
- **Border**: Transparent white (10% opacity)

## Typography

- **Sans Serif**: Inter — used for UI elements and body text
- **Serif**: Lora — used for long-form content (optional)
- **Monospace**: JetBrains Mono — used for code blocks and technical content
- **Scale**: Body (16px), Headlines (semi-bold), Labels (medium 12px)

## Spacing & Rounding

- **Base unit**: 0.25rem
- **Radius**: 0.65rem (10.4px) — consistent rounding across all interactive elements
- **Variants**: sm, md, lg, xl, 2xl, 3xl, 4xl for different component sizes

## Components

- **Buttons**: Rounded (10.4px), primary uses orange fill
- **Inputs**: Subtle border, light background (light mode) or semi-transparent white (dark mode)
- **Cards**: Rounded borders, subtle shadows, rely on color and typography for hierarchy
- **Sidebar**: Integrated into layout with distinct background color

## Do's and Don'ts

- Do use the primary orange color sparingly for high-priority actions
- Do maintain the adaptive light/dark theme for all components
- Don't mix border radius sizes within the same view
- Do maintain 4:1 minimum contrast ratio for accessibility
- Do use the typography hierarchy (sans/serif/mono) consistently
