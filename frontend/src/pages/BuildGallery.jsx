import React, { useState, useEffect } from 'react'
import SearchBuildDropdown from '../components/SearchBuildDropdown'
import { API_URL } from '../config'

export default function BuildGallery() {
  const [components, setComponents] = useState({
    purpose: [],
    case: [],
    cpu: [],
    gpu: [],
    ram: [],
    storage: [],
    cooler: [],
    psu: []
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const responses = await Promise.all([
          fetch(`${API_URL}/api/cases`),
          fetch(`${API_URL}/api/cpus`),
          fetch(`${API_URL}/api/gpus`),
          fetch(`${API_URL}/api/ram`),
          fetch(`${API_URL}/api/storage`),
          fetch(`${API_URL}/api/coolers`),
          fetch(`${API_URL}/api/psus`),
          fetch(`${API_URL}/api/motherboards`)
        ])

        const [cases, cpus, gpus, rams, storages, coolers, psus, motherboards] = await Promise.all(
          responses.map(res => res.json())
        )

        setComponents({
          purpose: ['1080p Gaming', '1440p Gaming', '4K Gaming', 'Programmera/Utveckla', 
                   'AI/Machine Learning', '3D Rendering', 'Video Redigering', 'Basic Användning'],
          case: cases.map(c => c.name),
          cpu: cpus.map(c => c.name),
          gpu: gpus.map(g => g.name),
          ram: rams.map(r => r.name),
          storage: storages.map(s => s.name),
          cooler: coolers.map(c => c.name),
          psu: psus.map(p => p.name)
        })
        setLoading(false)
      } catch (err) {
        console.error('Error fetching components:', err)
        setError('Failed to load components')
        setLoading(false)
      }
    }

    fetchComponents()
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Loading components...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg text-red-600">{error}</div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen">
      <div className="w-64 bg-white border-r border-gray-200 p-4 mt-40">
        <section role="search" className="flex flex-col gap-4">
          {/* Header */}
          <div className="flex flex-col gap-2">
            <h2 className="text-lg font-semibold">Build Filters</h2>
            <div className="text-sm text-gray-600">
              Showing 48 builds
            </div>
            <button 
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear filters
            </button>
          </div>

          {/* Search Input */}
          <div className="relative">
            <input
              type="search"
              placeholder="Search builds..."
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Searchable Dropdowns */}
          <SearchBuildDropdown
            label="Användningsområde" 
            placeholder="Alla användningsområden"
            options={components.purpose}
          />
          <SearchBuildDropdown 
            label="Chassi" 
            placeholder="Välj chassi"
            options={components.case}
          />
          <SearchBuildDropdown 
            label="CPU" 
            placeholder="Välj CPU"
            options={components.cpu}
          />
          <SearchBuildDropdown 
            label="GPU" 
            placeholder="Välj GPU"
            options={components.gpu}
          />
          <SearchBuildDropdown 
            label="RAM" 
            placeholder="Välj RAM"
            options={components.ram}
          />
          <SearchBuildDropdown 
            label="Lagring" 
            placeholder="Välj lagring"
            options={components.storage}
          />
          <SearchBuildDropdown 
            label="Kylare" 
            placeholder="Välj kylare"
            options={components.cooler}
          />
          <SearchBuildDropdown 
            label="PSU" 
            placeholder="Välj PSU"
            options={components.psu}
          />

          {/* Price Range */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">Pris</label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                placeholder="Min"
                className="w-full px-2 py-1 text-sm border rounded"
              />
              <span>-</span>
              <input
                type="number"
                placeholder="Max"
                className="w-full px-2 py-1 text-sm border rounded"
              />
            </div>
            {/* Price Range Bar */}
            <div className="h-1 bg-gray-200 rounded">
              <div className="h-full w-3/4 bg-blue-600 rounded"></div>
            </div>
          </div>
        </section>
      </div>

      <div className="flex-1 p-4 bg-gradient-to-b from-slate-400 to-slate-200">
        <h1>Main Content</h1>
        {/* Your gallery content will go here */}
      </div>
    </div>
  )
}
