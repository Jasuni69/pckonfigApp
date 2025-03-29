import React, { useState, useEffect } from 'react'

const SearchBuildDropdown = ({ label, placeholder, options, onChange, value }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedOption, setSelectedOption] = useState(null)

  // Update selected option when value prop changes
  useEffect(() => {
    setSelectedOption(value);
  }, [value]);

  const filteredOptions = options.filter(option =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="flex flex-col gap-1 relative">
      <label className="text-sm font-medium">{label}</label>
      <button 
        className="flex items-center justify-between w-full px-3 py-2 text-sm border rounded-lg"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{selectedOption || placeholder}</span>
        <svg className="w-4 h-4" viewBox="0 0 32 32">
          <path d="M6 13l10 10l10-10"></path>
        </svg>
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 w-full mt-1 bg-white border rounded-lg shadow-lg z-50">
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