import React, { useState, useEffect } from 'react'
import SearchBuildDropdown from '../components/SearchBuildDropdown'
import { API_URL } from '../config'
import { Link } from 'react-router-dom'

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
  const [publishedBuilds, setPublishedBuilds] = useState([])
  const [totalBuilds, setTotalBuilds] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // State for component maps to look up details by ID
  const [componentMaps, setComponentMaps] = useState({
    cpuMap: {},
    gpuMap: {},
    ramMap: {},
    storageMap: {},
    caseMap: {}
  })

  // State for filters
  const [filters, setFilters] = useState({
    purpose: null,
    cpu_id: null,
    gpu_id: null,
    case_id: null,
    ram_id: null,
    storage_id: null,
    cooler_id: null,
    psu_id: null,
    skip: 0,
    limit: 20
  })

  // Fetch components and builds
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

        // Create component maps for looking up details
        const cpuMap = Object.fromEntries(cpus.map(cpu => [cpu.id, cpu]));
        const gpuMap = Object.fromEntries(gpus.map(gpu => [gpu.id, gpu]));
        const ramMap = Object.fromEntries(rams.map(ram => [ram.id, ram]));
        const storageMap = Object.fromEntries(storages.map(storage => [storage.id, storage]));
        const caseMap = Object.fromEntries(cases.map(c => [c.id, c]));

        setComponentMaps({ cpuMap, gpuMap, ramMap, storageMap, caseMap });

        setComponents({
          purpose: ['1080p Gaming', '1440p Gaming', '4K Gaming', 'Programmera/Utveckla', 
                   'AI/Machine Learning', '3D Rendering', 'Video Redigering', 'Basic Användning'],
          case: cases,
          cpu: cpus,
          gpu: gpus,
          ram: rams,
          storage: storages,
          cooler: coolers,
          psu: psus
        })
        
        // Fetch published builds after components are loaded
        fetchPublishedBuilds();
      } catch (err) {
        console.error('Error fetching components:', err)
        setError('Failed to load components')
        setLoading(false)
      }
    }

    fetchComponents()
  }, [])

  // Function to fetch published builds with current filters
  const fetchPublishedBuilds = async () => {
    try {
      setLoading(true);
      // Build query parameters from filters
      const queryParams = new URLSearchParams();
      if (filters.purpose) queryParams.append('purpose', filters.purpose);
      if (filters.cpu_id) queryParams.append('cpu_id', filters.cpu_id);
      if (filters.gpu_id) queryParams.append('gpu_id', filters.gpu_id);
      if (filters.case_id) queryParams.append('case_id', filters.case_id);
      if (filters.ram_id) queryParams.append('ram_id', filters.ram_id);
      if (filters.storage_id) queryParams.append('storage_id', filters.storage_id);
      if (filters.cooler_id) queryParams.append('cooler_id', filters.cooler_id);
      if (filters.psu_id) queryParams.append('psu_id', filters.psu_id);
      queryParams.append('skip', filters.skip);
      queryParams.append('limit', filters.limit);
      
      console.log("Fetching with filters:", filters);
      console.log("Query params:", queryParams.toString());
      
      const response = await fetch(`${API_URL}/api/builds/public?${queryParams}`);
      const data = await response.json();
      
      setPublishedBuilds(data.builds);
      setTotalBuilds(data.total);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching published builds:', err);
      setError('Failed to load builds');
      setLoading(false);
    }
  };

  // Add a useEffect to fetch builds when filters change
  useEffect(() => {
    // Skip the initial render when components aren't loaded yet
    if (Object.keys(componentMaps.cpuMap).length > 0) {
      console.log("Filters changed, fetching builds:", filters);
      fetchPublishedBuilds();
    }
  }, [filters, componentMaps.cpuMap]); // Add componentMaps.cpuMap as a dependency to ensure it's loaded

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value,
      skip: 0 // Reset pagination when changing filters
    }));
    // Removed fetchPublishedBuilds() call - now handled by useEffect
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      purpose: null,
      cpu_id: null,
      gpu_id: null,
      case_id: null,
      ram_id: null,
      storage_id: null,
      cooler_id: null,
      psu_id: null,
      skip: 0,
      limit: 20
    });
    // Removed fetchPublishedBuilds() call - now handled by useEffect
  };

  if (loading) {
    return (
      <div className="flex min-h-screen">
        <div className="w-64 bg-white border-r border-gray-200 p-4 mt-40">
          {/* Skeleton sidebar */}
          <div className="flex flex-col gap-4">
            <div className="h-6 bg-gray-200 rounded animate-pulse w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3"></div>
            <div className="h-8 bg-gray-200 rounded animate-pulse w-full mt-2"></div>
            
            {/* Skeleton dropdowns */}
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex flex-col gap-1">
                <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3"></div>
                <div className="h-8 bg-gray-200 rounded animate-pulse w-full"></div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 p-4 bg-gradient-to-b from-slate-400 to-slate-200 mt-28">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-48 mb-6"></div>
          
          {/* Skeleton cards grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="h-48 bg-gray-200 animate-pulse"></div>
                <div className="p-4">
                  <div className="h-5 bg-gray-200 rounded animate-pulse w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-full mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3 mb-2"></div>
                  <div className="h-5 bg-gray-200 rounded animate-pulse w-1/4 mt-3"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
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
              Showing {publishedBuilds.length} of {totalBuilds} builds
            </div>
            <button 
              className="text-sm text-blue-600 hover:text-blue-800"
              onClick={clearFilters}
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
            onChange={(value) => handleFilterChange('purpose', value)}
            value={filters.purpose}
          />
          <SearchBuildDropdown 
            label="Chassi" 
            placeholder="Välj chassi"
            options={components.case.map(c => c.name)}
            onChange={(value) => {
              const selectedCase = components.case.find(c => c.name === value);
              handleFilterChange('case_id', selectedCase ? selectedCase.id : null);
            }}
            value={filters.case_id ? components.case.find(c => c.id === filters.case_id)?.name : null}
          />
          <SearchBuildDropdown 
            label="CPU" 
            placeholder="Välj CPU"
            options={components.cpu.map(c => c.name)}
            onChange={(value) => {
              const selectedCpu = components.cpu.find(c => c.name === value);
              handleFilterChange('cpu_id', selectedCpu ? selectedCpu.id : null);
            }}
            value={filters.cpu_id ? components.cpu.find(c => c.id === filters.cpu_id)?.name : null}
          />
          <SearchBuildDropdown 
            label="GPU" 
            placeholder="Välj GPU"
            options={components.gpu.map(g => g.name)}
            onChange={(value) => {
              const selectedGpu = components.gpu.find(g => g.name === value);
              handleFilterChange('gpu_id', selectedGpu ? selectedGpu.id : null);
            }}
            value={filters.gpu_id ? components.gpu.find(g => g.id === filters.gpu_id)?.name : null}
          />
          <SearchBuildDropdown 
            label="RAM" 
            placeholder="Välj RAM"
            options={components.ram.map(r => r.name)}
            onChange={(value) => {
              const selectedRam = components.ram.find(r => r.name === value);
              handleFilterChange('ram_id', selectedRam ? selectedRam.id : null);
            }}
            value={filters.ram_id ? components.ram.find(r => r.id === filters.ram_id)?.name : null}
          />
          <SearchBuildDropdown 
            label="Lagring" 
            placeholder="Välj lagring"
            options={components.storage.map(s => s.name)}
            onChange={(value) => {
              const selectedStorage = components.storage.find(s => s.name === value);
              handleFilterChange('storage_id', selectedStorage ? selectedStorage.id : null);
            }}
            value={filters.storage_id ? components.storage.find(s => s.id === filters.storage_id)?.name : null}
          />
          <SearchBuildDropdown 
            label="Kylare" 
            placeholder="Välj kylare"
            options={components.cooler.map(c => c.name)}
            onChange={(value) => {
              const selectedCooler = components.cooler.find(c => c.name === value);
              handleFilterChange('cooler_id', selectedCooler ? selectedCooler.id : null);
            }}
            value={filters.cooler_id ? components.cooler.find(c => c.id === filters.cooler_id)?.name : null}
          />
          <SearchBuildDropdown 
            label="PSU" 
            placeholder="Välj PSU"
            options={components.psu.map(p => p.name)}
            onChange={(value) => {
              const selectedPsu = components.psu.find(p => p.name === value);
              handleFilterChange('psu_id', selectedPsu ? selectedPsu.id : null);
            }}
            value={filters.psu_id ? components.psu.find(p => p.id === filters.psu_id)?.name : null}
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

      <div className="flex-1 p-4 bg-gradient-to-b from-slate-400 to-slate-200 mt-28">
        <h1 className="text-2xl font-bold mb-6">Build Gallery</h1>
        
        {/* Display builds grid */}
        {loading ? (
          <div className="space-y-4">
            <div className="h-8 bg-gray-200 rounded animate-pulse w-48 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="bg-white rounded-lg shadow-md overflow-hidden">
                  <div className="h-48 bg-gray-200 animate-pulse"></div>
                  <div className="p-4">
                    <div className="h-5 bg-gray-200 rounded animate-pulse w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3 mb-2"></div>
                    <div className="h-5 bg-gray-200 rounded animate-pulse w-1/4 mt-3"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {publishedBuilds.length > 0 ? (
              publishedBuilds.map((publishedBuild) => {
                // Get the associated saved build
                const build = publishedBuild.build;
                
                // Calculate approximate total price
                const totalPrice = [
                  build.cpu?.price || 0,
                  build.gpu?.price || 0,
                  build.ram?.price || 0,
                  build.storage?.price || 0,
                  build.motherboard?.price || 0,
                  build.psu?.price || 0,
                  build.case?.price || 0,
                  build.cooler?.price || 0
                ].reduce((sum, price) => sum + price, 0);
                
                return (
                  <div key={publishedBuild.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                    <Link to={`/build/${publishedBuild.id}`} className="block">
                      <div className="relative h-48 bg-gray-100">
                        <img 
                          src="/placeholder-image.jpg" 
                          alt={`${build.name} Preview`} 
                          className="w-full h-full object-cover"
                        />
                      </div>
                      
                      <div className="p-4">
                        <h3 className="font-semibold text-lg">{build.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {/* Display key components */}
                          {build.cpu ? build.cpu.name : 'No CPU'} | {build.gpu ? build.gpu.name : 'No GPU'} | {build.ram ? build.ram.name : 'No RAM'} | {build.storage ? build.storage.name : 'No Storage'}
                        </p>
                        
                        {publishedBuild.avg_rating > 0 && (
                          <div className="flex items-center mt-2">
                            <div className="flex">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <svg 
                                  key={star} 
                                  fill={star <= Math.round(publishedBuild.avg_rating) ? "var(--review-star-color, #FFB800)" : "var(--review-star-disabled-color, #E5E5E5)"} 
                                  height="12" 
                                  width="12" 
                                  className="mr-0.5" 
                                  viewBox="0 0 24 24">
                                  <path d="M8.9 9H2a1 1 0 0 0-.6 1.8l5.6 4-2.2 6.7a1 1 0 0 0 1.6 1l5.6-4.1 5.6 4.1a1 1 0 0 0 1.6-1L17 14.8l5.6-4A1 1 0 0 0 22 9h-6.9l-2.15-6.6a1 1 0 0 0-1.9 0z"></path>
                                </svg>
                              ))}
                            </div>
                            <span className="text-xs text-gray-600 ml-2">
                              ({publishedBuild.rating_count || 0} reviews)
                            </span>
                          </div>
                        )}
                        
                        <div className="mt-3">
                          <span className="font-bold text-lg">{totalPrice} kr</span>
                        </div>
                      </div>
                    </Link>
                  </div>
                );
              })
            ) : (
              <div className="col-span-3 text-center py-8 text-gray-500">
                No builds found. Try adjusting your filters.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
