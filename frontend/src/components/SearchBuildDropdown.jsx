import React, { useState, useEffect } from 'react'

/**
 * Searchable dropdown component used for filtering builds
 * Allows users to select from a list of options with search capability
 */
const SearchBuildDropdown = ({ label, placeholder, options, onChange, value }) => {
  // ===== STATE =====
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedOption, setSelectedOption] = useState(null)

  // Sync component state with external value
  useEffect(() => {
    setSelectedOption(value);
  }, [value]);

  // Filter options based on search term
  const filteredOptions = options.filter(option =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="flex flex-col gap-1 relative">
      {/* LABEL */}
      <label className="text-sm font-medium">{label}</label>
      
      {/* DROPDOWN TRIGGER BUTTON */}
      <button 
        className="flex items-center justify-between w-full px-3 py-2 text-sm border rounded-lg"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{selectedOption || placeholder}</span>
        <svg className="w-4 h-4" viewBox="0 0 32 32">
          <path d="M6 13l10 10l10-10"></path>
        </svg>
      </button>
      
      {/* DROPDOWN MENU - Only shown when open */}
      {isOpen && (
        <div className="absolute top-full left-0 w-full mt-1 bg-white border rounded-lg shadow-lg z-50">
          {/* SEARCH INPUT */}
          <div className="p-2">
            <input
              type="text"
              placeholder="Search..."
              className="w-full px-2 py-1 text-sm border rounded"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
          </div>
          
          {/* OPTIONS LIST */}
          <div className="max-h-48 overflow-y-auto">
            {filteredOptions.map((option, index) => (
              <button
                key={index}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100"
                onClick={() => {
                  setSelectedOption(option)
                  setIsOpen(false)
                  setSearchTerm('')
                  if (onChange) {
                    onChange(option)
                  }
                }}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SearchBuildDropdown;