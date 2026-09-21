import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

describe('test infrastructure', () => {
  it('renders and queries a component', () => {
    render(<div>RAMS AI Demo</div>)
    expect(screen.getByText('RAMS AI Demo')).toBeInTheDocument()
  })
})
