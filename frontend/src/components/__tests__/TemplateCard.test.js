import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TemplateCard from '../TemplateCard';

describe('TemplateCard Component', () => {
  const mockTemplate = {
    id: 'test-template-1',
    name: 'Test Template',
    description: 'This is a test template description'
  };
  
  const mockOnSelect = jest.fn();
  
  beforeEach(() => {
    mockOnSelect.mockClear();
  });
  
  test('renders template information correctly', () => {
    render(<TemplateCard template={mockTemplate} onSelect={mockOnSelect} />);
    
    // Check if the template name and description are displayed
    expect(screen.getByText('Test Template')).toBeInTheDocument();
    expect(screen.getByText('This is a test template description')).toBeInTheDocument();
    expect(screen.getByText('Template')).toBeInTheDocument(); // The tag
  });
  
  test('calls onSelect when the card is clicked', () => {
    render(<TemplateCard template={mockTemplate} onSelect={mockOnSelect} />);
    
    // Click the card using the data-testid
    fireEvent.click(screen.getByTestId('template-card'));
    
    // Check if onSelect was called with the correct template ID
    expect(mockOnSelect).toHaveBeenCalledTimes(1);
    expect(mockOnSelect).toHaveBeenCalledWith('test-template-1');
  });
  
  test('calls onSelect when the button is clicked', () => {
    render(<TemplateCard template={mockTemplate} onSelect={mockOnSelect} />);
    
    // Click the "Use this template" button using data-testid
    fireEvent.click(screen.getByTestId('use-template-button'));
    
    // Check if onSelect was called with the correct template ID
    expect(mockOnSelect).toHaveBeenCalledTimes(1);
    expect(mockOnSelect).toHaveBeenCalledWith('test-template-1');
  });
}); 