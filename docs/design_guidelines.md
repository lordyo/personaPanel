# Frontend Design Guidelines - Solarized Dark Theme

## Overview
This document outlines the design guidelines for the Entity Simulation Framework frontend, based on the Solarized Dark color scheme. The Solarized Dark theme provides a high-contrast, accessible color palette that reduces eye strain during extended coding sessions.

## Color Palette

### Base Colors
- **Background (Base03)**: `#002b36` - Primary background color
- **Content Background (Base02)**: `#073642` - Secondary background, for cards and containers
- **Subtle Content (Base01)**: `#586e75` - Subtle highlights, borders
- **Body Text (Base0)**: `#839496` - Default text color
- **Emphasized Text (Base1)**: `#93a1a1` - Emphasized content, headings
- **Background Highlights (Base2)**: `#eee8d5` - Highlights in light areas
- **Background Content (Base3)**: `#fdf6e3` - Background for pop-ups, modals

### Accent Colors
- **Yellow**: `#b58900` - Primary buttons, important actions
- **Orange**: `#cb4b16` - Warnings, secondary actions
- **Red**: `#dc322f` - Errors, destructive actions
- **Magenta**: `#d33682` - Highlights, special features
- **Violet**: `#6c71c4` - Links, interactive elements
- **Blue**: `#268bd2` - Information, primary brand color
- **Cyan**: `#2aa198` - Success, confirmations
- **Green**: `#859900` - Positive feedback, completed actions

## Typography

### Font Families
- **Primary Font**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Monospace Font**: `'Fira Code', 'Source Code Pro', monospace` (for code displays)

### Font Sizes
- **Base Size**: `16px`
- **Small Text**: `14px`
- **Extra Small Text**: `12px`
- **Large Text**: `18px`
- **Heading 1**: `24px`
- **Heading 2**: `20px`
- **Heading 3**: `18px`

### Font Weights
- **Regular**: `400`
- **Medium**: `500`
- **Bold**: `600`

## Components

### Cards
- Background: Content Background (Base02)
- Border: 1px solid Subtle Content (Base01)
- Border Radius: 4px
- Box Shadow: `0 2px 4px rgba(0, 0, 0, 0.2)`
- Padding: 16px

```css
.card {
  background-color: #073642;
  border: 1px solid #586e75;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  padding: 16px;
}
```

### Buttons

#### Primary Button
- Background: Yellow
- Text Color: Background (Base03)
- Hover: Darken by 10%
- Border Radius: 4px
- Padding: 8px 16px

```css
.button-primary {
  background-color: #b58900;
  color: #002b36;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
}

.button-primary:hover {
  background-color: #9a7600;
}
```

#### Secondary Button
- Background: Transparent
- Border: 1px solid Violet
- Text Color: Violet
- Hover: Background Violet at 10% opacity
- Border Radius: 4px
- Padding: 8px 16px

```css
.button-secondary {
  background-color: transparent;
  color: #6c71c4;
  border: 1px solid #6c71c4;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
}

.button-secondary:hover {
  background-color: rgba(108, 113, 196, 0.1);
}
```

#### Destructive Button
- Background: Red
- Text Color: Background (Base03)
- Hover: Darken by 10%
- Border Radius: 4px
- Padding: 8px 16px

```css
.button-destructive {
  background-color: #dc322f;
  color: #002b36;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
}

.button-destructive:hover {
  background-color: #c42e2c;
}
```

### Form Elements

#### Text Input
- Background: Background (Base03)
- Border: 1px solid Subtle Content (Base01)
- Text Color: Body Text (Base0)
- Focus Border: Blue
- Border Radius: 4px
- Padding: 8px 12px

```css
.input-text {
  background-color: #002b36;
  color: #839496;
  border: 1px solid #586e75;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 16px;
}

.input-text:focus {
  border-color: #268bd2;
  outline: none;
}
```

#### Select
- Background: Background (Base03)
- Border: 1px solid Subtle Content (Base01)
- Text Color: Body Text (Base0)
- Focus Border: Blue
- Border Radius: 4px
- Padding: 8px 12px

```css
.select {
  background-color: #002b36;
  color: #839496;
  border: 1px solid #586e75;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 16px;
}

.select:focus {
  border-color: #268bd2;
  outline: none;
}
```

### Entity Card
- Background: Content Background (Base02)
- Border: 1px solid Subtle Content (Base01)
- Border Radius: 4px
- Padding: 16px
- Title: Emphasized Text (Base1)
- Attributes: Body Text (Base0)
- Selection Indicator: Blue
- Hover: Border color Blue

```css
.entity-card {
  background-color: #073642;
  border: 1px solid #586e75;
  border-radius: 4px;
  padding: 16px;
  transition: border-color 0.2s ease;
}

.entity-card:hover {
  border-color: #268bd2;
}

.entity-card.selected {
  border-color: #268bd2;
  box-shadow: 0 0 0 1px #268bd2;
}

.entity-card h3 {
  color: #93a1a1;
  margin-top: 0;
  font-size: 18px;
}

.entity-card .attribute {
  color: #839496;
  margin: 4px 0;
}

.entity-card .attribute-name {
  font-weight: 500;
}
```

## Layouts

### Main Layout
- Background: Background (Base03)
- Text Color: Body Text (Base0)
- Sidebar Background: Content Background (Base02)
- Header Background: Content Background (Base02)

```css
body {
  background-color: #002b36;
  color: #839496;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  margin: 0;
  padding: 0;
}

.app-container {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background-color: #073642;
  padding: 16px;
}

.main-content {
  flex: 1;
  padding: 24px;
}

.header {
  background-color: #073642;
  padding: 16px 24px;
  border-bottom: 1px solid #586e75;
}
```

### Grid Layout for Entity Gallery
- Grid Template Columns: repeat(auto-fill, minmax(240px, 1fr))
- Gap: 16px

```css
.entity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
```

## Icons
- Default Color: Body Text (Base0)
- Interactive Icons: Blue
- Size: 20px for regular, 16px for small context
- Use consistent style throughout the application

```css
.icon {
  color: #839496;
  font-size: 20px;
}

.icon-small {
  font-size: 16px;
}

.icon-interactive {
  color: #268bd2;
  cursor: pointer;
}

.icon-interactive:hover {
  color: #1a6091;
}
```

## Notification and Feedback

### Success Message
- Background: Cyan (with 10% opacity)
- Border-left: 4px solid Cyan
- Text Color: Cyan

```css
.message-success {
  background-color: rgba(42, 161, 152, 0.1);
  border-left: 4px solid #2aa198;
  color: #2aa198;
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 4px 4px 0;
}
```

### Warning Message
- Background: Orange (with 10% opacity)
- Border-left: 4px solid Orange
- Text Color: Orange

```css
.message-warning {
  background-color: rgba(203, 75, 22, 0.1);
  border-left: 4px solid #cb4b16;
  color: #cb4b16;
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 4px 4px 0;
}
```

### Error Message
- Background: Red (with 10% opacity)
- Border-left: 4px solid Red
- Text Color: Red

```css
.message-error {
  background-color: rgba(220, 50, 47, 0.1);
  border-left: 4px solid #dc322f;
  color: #dc322f;
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 4px 4px 0;
}
```

## Loading States

### Spinner
- Color: Blue
- Size: 24px

```css
.spinner {
  color: #268bd2;
  animation: spin 1s linear infinite;
  width: 24px;
  height: 24px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### Loading Overlay
- Background: Background (Base03) with 80% opacity
- Text Color: Emphasized Text (Base1)

```css
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 43, 54, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  z-index: 10;
}

.loading-overlay .message {
  color: #93a1a1;
  margin-top: 16px;
  font-weight: 500;
}
```

## Implementation Guidelines

1. **CSS Approach**
   - Use CSS modules for component-specific styles
   - Maintain a global theme file with variables for colors and sizing
   - Keep styling simple and consistent

2. **Responsive Design**
   - Design for desktop first, then adapt for smaller screens
   - Use flexible layouts that adapt to different screen sizes
   - Set breakpoints at: 480px, 768px, 1024px, 1280px

3. **Accessibility**
   - Maintain sufficient color contrast (WCAG AA level)
   - Add focus styles for keyboard navigation
   - Include proper aria attributes for interactive elements
   - Test with screen readers for basic compatibility

4. **Implementation Priority**
   - Focus on functional UI first before visual refinements
   - Implement theme basics (colors, typography) early
   - Add animations and transitions last

## React Component Example

```jsx
import React from 'react';
import './EntityCard.css'; // Using CSS modules

const EntityCard = ({ entity, onSelect, isSelected }) => {
  return (
    <div 
      className={`entity-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(entity.id)}
    >
      <h3>{entity.name}</h3>
      <div className="attributes">
        {Object.entries(entity.attributes).map(([key, value]) => (
          <div className="attribute" key={key}>
            <span className="attribute-name">{key}:</span> {value}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EntityCard;
```

This design guide provides a foundation for creating a cohesive, visually appealing interface for the Entity Simulation Framework using the Solarized Dark theme. The guidelines prioritize simplicity and functionality while maintaining a professional and modern aesthetic.