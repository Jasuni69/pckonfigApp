import React, { useState, useEffect } from 'react'
import SearchBuildDropdown from '../components/SearchBuildDropdown'
import { API_URL } from '../config'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'

const BuildGallery = () => {
  // ===== STATE MANAGEMENT =====
  // Component data state
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
  
  // Component lookup maps for efficient data access
  const [componentMaps, setComponentMaps] = useState({
    cpuMap: {},
    gpuMap: {},
    ramMap: {},
    storageMap: {},
    caseMap: {}
  })

  // Filter criteria state
  const [filters, setFilters] = useState({
    purpose: null,
    cpu_id: null,
    gpu_id: null,
    case_id: null,
    ram_id: null,
    storage_id: null,
    cooler_id: null,
    psu_id: null,
    min_price: null,
    max_price: null,
    skip: 0,
    limit: 20
  })

  // ===== DATA FETCHING =====
  // Fetch builds based on current filter criteria
  const fetchPublishedBuilds = async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setLoading(true);
      }
      
      // Build query parameters from active filters
      const queryParams = new URLSearchParams();
      if (filters.purpose) queryParams.append('purpose', filters.purpose);
      if (filters.cpu_id) queryParams.append('cpu_id', filters.cpu_id);
      if (filters.gpu_id) queryParams.append('gpu_id', filters.gpu_id);
      if (filters.case_id) queryParams.append('case_id', filters.case_id);
      if (filters.ram_id) queryParams.append('ram_id', filters.ram_id);
      if (filters.storage_id) queryParams.append('storage_id', filters.storage_id);
      if (filters.cooler_id) queryParams.append('cooler_id', filters.cooler_id);
      if (filters.psu_id) queryParams.append('psu_id', filters.psu_id);
      if (filters.min_price) queryParams.append('min_price', filters.min_price);
      if (filters.max_price) queryParams.append('max_price', filters.max_price);
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

  // Initial data loading - fetch all component data and builds
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

        // Create lookup maps for efficient component access by ID
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
        
        // Fetch builds after components are loaded
        fetchPublishedBuilds(true);
      } catch (err) {
        console.error('Error fetching components:', err)
        setError('Failed to load components')
        setLoading(false)
      }
    }

    fetchComponents()
  }, [])

  // Refresh builds when filters change
  useEffect(() => {
    // Skip the initial render when components aren't loaded yet
    if (Object.keys(componentMaps.cpuMap).length > 0) {
      console.log("Filters changed, fetching builds:", filters);
      fetchPublishedBuilds(false);
    }
  }, [filters, componentMaps.cpuMap]);

  // ===== EVENT HANDLERS =====
  // Update filter state when a filter value changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value,
      skip: 0 // Reset pagination when changing filters
    }));
  };

  // Reset all filters to default values
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
      min_price: null,
      max_price: null,
      skip: 0,
      limit: 20
    });
  };

  // ===== LOADING STATE UI =====
  if (loading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-slate-800 text-center mb-12">
            Bygggalleri
          </h1>

          {/* Search and Filters */}
          <div className="mb-8 flex gap-4 justify-center">
            <input 
              type="text"
              placeholder="Sök byggen..."
              className="px-4 py-2 rounded-lg border border-slate-300 w-full max-w-md"
            />
          </div>

          {/* Builds Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-xl shadow-lg overflow-hidden">
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
      </Layout>
    )
  }

  // ===== ERROR STATE UI =====
  if (error) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-slate-800 text-center mb-12">
            Bygggalleri
          </h1>

          {/* Search and Filters */}
          <div className="mb-8 flex gap-4 justify-center">
            <input 
              type="text"
              placeholder="Sök byggen..."
              className="px-4 py-2 rounded-lg border border-slate-300 w-full max-w-md"
            />
          </div>

          {/* Builds Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {publishedBuilds.map(build => (
              <Link 
                key={build.id}
                to={`/build/${build.id}`}
                className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="aspect-video relative">
                  <img 
                    src="/placeholder-image.jpg" 
                    alt={build.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-4">
                    <div className="text-white">
                      <h3 className="text-xl font-bold">{build.name}</h3>
                      <p className="text-sm opacity-90">
                        {build.cpu?.name} | {build.gpu?.name}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-slate-800 text-center mb-12">
          Bygggalleri
        </h1>

        {/* Search and Filters */}
        <div className="mb-8 flex gap-4 justify-center">
          <input 
            type="text"
            placeholder="Sök byggen..."
            className="px-4 py-2 rounded-lg border border-slate-300 w-full max-w-md"
          />
        </div>

        {/* Builds Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {publishedBuilds.map(build => (
            <Link 
              key={build.id}
              to={`/build/${build.id}`}
              className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              <div className="aspect-video relative">
                <img 
                  src="/placeholder-image.jpg" 
                  alt={build.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-4">
                  <div className="text-white">
                    <h3 className="text-xl font-bold">{build.name}</h3>
                    <p className="text-sm opacity-90">
                      {build.cpu?.name} | {build.gpu?.name}
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </Layout>
  )
}

export default BuildGallery
