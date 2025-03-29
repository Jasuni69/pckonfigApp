import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_URL } from '../config';

const BuildDetail = () => {
  const { id } = useParams();
  const [build, setBuild] = useState(null);
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [newRating, setNewRating] = useState(5);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchBuildDetails = async () => {
      try {
        // Fetch the build details
        const buildResponse = await fetch(`${API_URL}/api/builds/public/${id}`);
        if (!buildResponse.ok) {
          throw new Error(`Error fetching build: ${buildResponse.status}`);
        }
        const buildData = await buildResponse.json();
        setBuild(buildData);

        // Fetch ratings for this build
        const ratingsResponse = await fetch(`${API_URL}/api/builds/public/${id}/ratings`);
        if (!ratingsResponse.ok) {
          throw new Error(`Error fetching ratings: ${ratingsResponse.status}`);
        }
        const ratingsData = await ratingsResponse.json();
        setRatings(ratingsData);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching build details:', err);
        setError('Failed to load build details');
        setLoading(false);
      }
    };

    fetchBuildDetails();
  }, [id]);

  const handleSubmitRating = async (e) => {
    e.preventDefault();
    
    if (newRating < 1 || newRating > 5) {
      alert('Rating must be between 1 and 5');
      return;
    }

    try {
      setSubmitting(true);
      
      // Get token from localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        alert('You must be logged in to leave a review');
        return;
      }
      
      const response = await fetch(`${API_URL}/api/builds/public/${id}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          rating: newRating,
          comment: newComment
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error submitting rating: ${response.status}`);
      }
      
      // Refresh ratings
      const ratingsResponse = await fetch(`${API_URL}/api/builds/public/${id}/ratings`);
      const ratingsData = await ratingsResponse.json();
      setRatings(ratingsData);
      
      // Refresh build details to update avg_rating
      const buildResponse = await fetch(`${API_URL}/api/builds/public/${id}`);
      const buildData = await buildResponse.json();
      setBuild(buildData);
      
      // Clear form
      setNewComment('');
      setNewRating(5);
      setSubmitting(false);
    } catch (err) {
      console.error('Error submitting rating:', err);
      alert('Failed to submit rating');
      setSubmitting(false);
    }
  };

  // Calculate total price based on component prices
  const calculateTotalPrice = () => {
    if (!build || !build.build) return 0;
    
    const { build: buildData } = build;
    return [
      buildData.cpu?.price || 0,
      buildData.gpu?.price || 0,
      buildData.ram?.price || 0,
      buildData.storage?.price || 0,
      buildData.case?.price || 0,
      buildData.psu?.price || 0,
      buildData.cooler?.price || 0,
      buildData.motherboard?.price || 0
    ].reduce((sum, price) => sum + price, 0);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Loading build details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg text-red-600">{error}</div>
      </div>
    );
  }

  if (!build) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Build not found</div>
      </div>
    );
  }

  const { build: buildData } = build;
  const totalPrice = calculateTotalPrice();

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          {/* Build Header */}
          <div className="px-6 py-8 border-b border-gray-200">
            <h1 className="text-3xl font-bold text-gray-900">{buildData.name}</h1>
            <p className="mt-2 text-sm text-gray-600">{buildData.purpose}</p>
            
            <div className="mt-4 flex items-center">
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg 
                    key={star} 
                    fill={star <= Math.round(build.avg_rating) ? "var(--review-star-color, #FFB800)" : "var(--review-star-disabled-color, #E5E5E5)"} 
                    height="20" 
                    width="20" 
                    className="mr-1" 
                    viewBox="0 0 24 24">
                    <path d="M8.9 9H2a1 1 0 0 0-.6 1.8l5.6 4-2.2 6.7a1 1 0 0 0 1.6 1l5.6-4.1 5.6 4.1a1 1 0 0 0 1.6-1L17 14.8l5.6-4A1 1 0 0 0 22 9h-6.9l-2.15-6.6a1 1 0 0 0-1.9 0z"></path>
                  </svg>
                ))}
              </div>
              <span className="ml-2 text-gray-600">
                {build.avg_rating.toFixed(1)} ({build.rating_count} reviews)
              </span>
            </div>
          </div>

          {/* Build Images */}
          <div className="px-6 py-6 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                {/* Main image - replace with actual image when available */}
                <div className="bg-gray-200 rounded-lg aspect-[4/3] overflow-hidden">
                  <img 
                    src="/placeholder-image.jpg" 
                    alt={`${buildData.name}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {/* Additional images - replace with actual images */}
                {[1, 2, 3, 4].map((img) => (
                  <div key={img} className="bg-gray-200 rounded-lg aspect-square overflow-hidden">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={`${buildData.name} detail ${img}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Component Details */}
          <div className="px-6 py-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Components</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {buildData.cpu && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.cpu.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">CPU</h3>
                    <p>{buildData.cpu.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.cpu.cores} cores
                      {buildData.cpu.threads && `, ${buildData.cpu.threads} threads`}
                      {buildData.cpu.base_clock && `, ${buildData.cpu.base_clock} GHz`}
                    </p>
                    <p className="font-medium mt-1">{buildData.cpu.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.gpu && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.gpu.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">GPU</h3>
                    <p>{buildData.gpu.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.gpu.memory && `${buildData.gpu.memory} memory`}
                    </p>
                    <p className="font-medium mt-1">{buildData.gpu.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.motherboard && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.motherboard.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">Motherboard</h3>
                    <p>{buildData.motherboard.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.motherboard.socket && `${buildData.motherboard.socket}`}
                      {buildData.motherboard.form_factor && `, ${buildData.motherboard.form_factor}`}
                    </p>
                    <p className="font-medium mt-1">{buildData.motherboard.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.ram && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.ram.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">RAM</h3>
                    <p>{buildData.ram.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.ram.capacity && `${buildData.ram.capacity}GB`} 
                      {buildData.ram.speed && `, ${buildData.ram.speed} MHz`}
                    </p>
                    <p className="font-medium mt-1">{buildData.ram.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.storage && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.storage.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">Storage</h3>
                    <p>{buildData.storage.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.storage.capacity && `${buildData.storage.capacity}GB`}
                      {buildData.storage.type && `, ${buildData.storage.type}`}
                    </p>
                    <p className="font-medium mt-1">{buildData.storage.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.case && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.case.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">Case</h3>
                    <p>{buildData.case.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.case.form_factor && `${buildData.case.form_factor}`}
                      {buildData.case.color && `, ${buildData.case.color}`}
                    </p>
                    <p className="font-medium mt-1">{buildData.case.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.psu && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.psu.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">Power Supply</h3>
                    <p>{buildData.psu.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.psu.wattage && `${buildData.psu.wattage}W`}
                      {buildData.psu.efficiency && `, ${buildData.psu.efficiency}`}
                    </p>
                    <p className="font-medium mt-1">{buildData.psu.price} kr</p>
                  </div>
                </div>
              )}
              
              {buildData.cooler && (
                <div className="flex items-start">
                  <div className="w-24 h-24 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 mr-4">
                    <img 
                      src="/placeholder-image.jpg" 
                      alt={buildData.cooler.name}
                      className="w-full h-full object-contain p-2"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium">Cooler</h3>
                    <p>{buildData.cooler.name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildData.cooler.type && `${buildData.cooler.type}`}
                    </p>
                    <p className="font-medium mt-1">{buildData.cooler.price} kr</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold">Total Price</h3>
                <p className="text-2xl font-bold">{totalPrice.toLocaleString()} kr</p>
              </div>
            </div>
          </div>

          {/* Reviews and Comments */}
          <div className="px-6 py-6">
            <h2 className="text-xl font-semibold mb-4">Reviews ({ratings.length})</h2>
            
            {/* Add review form */}
            <div className="mb-8 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Add Your Review</h3>
              <form onSubmit={handleSubmitRating}>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Rating</label>
                  <div className="flex items-center">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setNewRating(star)}
                        className="mr-1 focus:outline-none"
                      >
                        <svg 
                          fill={star <= newRating ? "var(--review-star-color, #FFB800)" : "var(--review-star-disabled-color, #E5E5E5)"} 
                          height="24" 
                          width="24" 
                          viewBox="0 0 24 24">
                          <path d="M8.9 9H2a1 1 0 0 0-.6 1.8l5.6 4-2.2 6.7a1 1 0 0 0 1.6 1l5.6-4.1 5.6 4.1a1 1 0 0 0 1.6-1L17 14.8l5.6-4A1 1 0 0 0 22 9h-6.9l-2.15-6.6a1 1 0 0 0-1.9 0z"></path>
                        </svg>
                      </button>
                    ))}
                    <span className="ml-2">{newRating} of 5 stars</span>
                  </div>
                </div>
                
                <div className="mb-4">
                  <label htmlFor="comment" className="block text-sm font-medium mb-2">
                    Comment (optional)
                  </label>
                  <textarea
                    id="comment"
                    rows="4"
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Share your thoughts about this build..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                  ></textarea>
                </div>
                
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {submitting ? 'Submitting...' : 'Submit Review'}
                </button>
              </form>
            </div>
            
            {/* Reviews list */}
            {ratings.length > 0 ? (
              <div className="space-y-4">
                {ratings.map((rating) => (
                  <div key={rating.id} className="p-4 border rounded-lg">
                    <div className="flex items-center mb-2">
                      <div className="flex">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <svg 
                            key={star} 
                            fill={star <= rating.rating ? "var(--review-star-color, #FFB800)" : "var(--review-star-disabled-color, #E5E5E5)"} 
                            height="16" 
                            width="16" 
                            className="mr-0.5" 
                            viewBox="0 0 24 24">
                            <path d="M8.9 9H2a1 1 0 0 0-.6 1.8l5.6 4-2.2 6.7a1 1 0 0 0 1.6 1l5.6-4.1 5.6 4.1a1 1 0 0 0 1.6-1L17 14.8l5.6-4A1 1 0 0 0 22 9h-6.9l-2.15-6.6a1 1 0 0 0-1.9 0z"></path>
                          </svg>
                        ))}
                      </div>
                      <span className="ml-2 text-sm text-gray-500">
                        User #{rating.user_id} • {new Date(rating.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {rating.comment && (
                      <p className="text-gray-700">{rating.comment}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No reviews yet. Be the first to review!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BuildDetail;