# Frontend Design Guidelines - Dark Theme with Tailwind

## Overview
This document outlines the design guidelines for the Entity Simulation Framework frontend, based on a dark color scheme implemented with Tailwind CSS. This theme provides high contrast and reduces eye strain during extended usage sessions.

## Color Palette

### Base Colors
- **Background**: `bg-gray-900` - Main application background
- **Card Background**: `bg-gray-800` - Component backgrounds
- **Secondary Background**: `bg-gray-750` - Hover states, secondary elements
- **Border Color**: `border-gray-700` - Borders and dividers

### Text Colors
- **Primary Text**: `text-white` - Primary text
- **Secondary Text**: `text-gray-300` - Body text
- **Muted Text**: `text-gray-400` - Less important text
- **Heading Text**: `text-blue-300` - Headings and titles

### Interactive Colors
- **Primary**: `text-blue-400`/`bg-blue-600` - Primary interactive elements
- **Primary Hover**: `text-blue-300`/`bg-blue-700` - Hover states
- **Secondary**: `text-purple-400`/`bg-purple-600` - Secondary interactive elements
- **Destructive**: `text-red-400`/`bg-red-600` - Destructive actions
- **Success**: `text-green-400`/`bg-green-600` - Success states

## Typography

### Font Sizes
- **Extra Small**: `text-xs`
- **Small**: `text-sm`
- **Base**: `text-base`
- **Large**: `text-lg`
- **Extra Large**: `text-xl`
- **2XL**: `text-2xl`

### Font Weights
- **Normal**: `font-normal`
- **Medium**: `font-medium`
- **Semibold**: `font-semibold`
- **Bold**: `font-bold`

## Component Examples

### Cards
Cards are used to display content in contained units.

```jsx
<div className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
  <div className="p-5">
    <h3 className="text-xl font-semibold text-blue-300">Card Title</h3>
    <p className="text-gray-300 mb-4">Card description text goes here</p>
    
    {/* Card content */}
    
    <div className="mt-4 flex items-center justify-between">
      <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
        Tag
      </span>
      <button className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
        Action →
      </button>
    </div>
  </div>
</div>
```

### Buttons

#### Primary Button
```jsx
<button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors">
  Primary Button
</button>
```

#### Secondary Button
```jsx
<button className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors">
  Secondary Button
</button>
```

#### Destructive Button
```jsx
<button className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md transition-colors">
  Delete
</button>
```

#### Text Button
```jsx
<button className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
  Text Button
</button>
```

### Form Elements

#### Text Input
```jsx
<div className="mb-4">
  <label className="block text-gray-300 text-sm font-medium mb-2">
    Label
  </label>
  <input 
    type="text" 
    className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    placeholder="Enter text"
  />
</div>
```

#### Select
```jsx
<div className="mb-4">
  <label className="block text-gray-300 text-sm font-medium mb-2">
    Select Option
  </label>
  <select className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
    <option value="">Select an option</option>
    <option value="option1">Option 1</option>
    <option value="option2">Option 2</option>
  </select>
</div>
```

#### Checkbox
```jsx
<div className="flex items-center mb-4">
  <input 
    type="checkbox" 
    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
  />
  <label className="ml-2 text-gray-300 text-sm">
    Checkbox label
  </label>
</div>
```

### Tags/Pills
```jsx
<span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
  Tag Label
</span>
```

### Entity Card
```jsx
<div className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl">
  <div className="p-5">
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-xl font-semibold text-blue-300">Entity Name</h3>
      <button className="text-red-400 hover:text-red-300 transition-colors p-1 rounded hover:bg-red-900/30">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
    <p className="text-gray-300 mb-4 line-clamp-2 min-h-[3rem]">Entity description text</p>
    
    <div className="mt-4 flex items-center justify-between">
      <div className="flex items-center">
        <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
          Attribute
        </span>
      </div>
      <button className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
        View Details →
      </button>
    </div>
  </div>
</div>
```

## Layouts

### Main Layout
```jsx
<div className="bg-gray-900 min-h-screen text-gray-300">
  <header className="bg-gray-800 border-b border-gray-700 py-4 px-6">
    <div className="container mx-auto flex justify-between items-center">
      <h1 className="text-xl font-bold text-blue-300">Application Title</h1>
      <nav>
        {/* Navigation items */}
      </nav>
    </div>
  </header>
  
  <main className="container mx-auto px-4 py-8">
    <div className="flex justify-between items-center mb-6">
      <h1 className="text-2xl font-bold text-blue-300">Page Title</h1>
      <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors">
        Primary Action
      </button>
    </div>
    
    {/* Page content */}
  </main>
</div>
```

### Card Grid Layout
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <Card key={item.id} item={item} />
  ))}
</div>
```

## Notification and Feedback

### Success Message
```jsx
<div className="mb-6 p-4 bg-green-600 bg-opacity-10 border border-green-500 rounded-lg text-green-400">
  Success message text
</div>
```

### Error Message
```jsx
<div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
  Error message text
</div>
```

### Warning Message
```jsx
<div className="mb-6 p-4 bg-orange-400 bg-opacity-10 border border-orange-400 rounded-lg text-orange-300">
  Warning message text
</div>
```

## Loading States

### Spinner
```jsx
<div className="flex justify-center items-center py-8">
  <svg className="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
</div>
```

### Loading Card Placeholder
```jsx
<div className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 animate-pulse">
  <div className="p-5">
    <div className="h-6 bg-gray-700 rounded mb-4 w-3/4"></div>
    <div className="h-4 bg-gray-700 rounded mb-2"></div>
    <div className="h-4 bg-gray-700 rounded mb-2 w-5/6"></div>
    <div className="h-4 bg-gray-700 rounded w-4/6"></div>
    
    <div className="mt-4 flex items-center justify-between">
      <div className="h-6 bg-gray-700 rounded w-16"></div>
      <div className="h-6 bg-gray-700 rounded w-24"></div>
    </div>
  </div>
</div>
```

## Implementation Guidelines

1. **Consistently use Tailwind classes**
   - Use the Tailwind utility classes defined in this guide
   - Avoid creating custom CSS unless absolutely necessary
   - Leverage Tailwind's responsive modifiers (sm:, md:, lg:) for responsive design

2. **Responsive Design Best Practices**
   - Start with mobile design and enhance for larger screens
   - Use Tailwind's grid system with appropriate breakpoints
   - Test on multiple screen sizes

3. **Accessibility Tips**
   - Ensure sufficient color contrast between text and backgrounds
   - Add appropriate `aria-*` attributes to interactive elements
   - Use semantic HTML elements where appropriate

4. **Code Organization**
   - Group related Tailwind classes logically
   - Extract common patterns to reusable components
   - Use consistent class ordering (layout → typography → colors → etc.)

## Unified Simulation Updates

The application has been updated to remove the concept of interaction types (solo, dyadic, group) in favor of a unified simulation approach. When implementing simulation-related UIs:

1. Do not include interaction type selection in forms
2. Do not enforce entity count validation based on interaction types
3. Remove filtering by interaction type from list views
4. Remove interaction type display from simulation details

All simulations now use the unified simulation API which supports any number of entities without type distinction.