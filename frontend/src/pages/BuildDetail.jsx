import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_URL } from '../config';

const BuildDetail = () => {
  const { id } = useParams();
  const [build, setBuild] = useState(null);
  const [components, setComponents] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comment, setComment] = useState('');
  const [rating, setRating] = useState(0);
  const [commentSubmitting, setCommentSubmitting] = useState(false);

  useEffect(() => {
    // Fetch build details
    const fetchBuild = async () => {
      try {
        const response = await fetch(`${API_URL}/api/builds/public/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch build details');
        }
        const data = await response.json();
        setBuild(data);
        
        // Fetch component details
        await fetchComponents(data.build);
      } catch (err) {
        console.error('Error fetching build:', err);
        setError('Could not load build details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    // Fetch component details for the build
    const fetchComponents = async (buildData) => {
      try {
        const componentTypes = [
          { type: 'cpu', id: buildData.cpu_id },
          { type: 'gpu', id: buildData.gpu_id },
          { type: 'motherboard', id: buildData.motherboard_id },
          { type: 'ram', id: buildData.ram_id },
          { type: 'storage', id: buildData.storage_id },
          { type: 'psu', id: buildData.psu_id },
          { type: 'case', id: buildData.case_id },
          { type: 'cooler', id: buildData.cooler_id }
        ];

        // Create promises for all component API calls
        const promises = componentTypes.map(async ({ type, id }) => {
          if (id) {
            const endpoint = type === 'ram' ? 'ram' : `${type}s`; // Handle special case for 'ram'
            const response = await fetch(`${API_URL}/api/${endpoint}`);
            if (!response.ok) {
              throw new Error(`Failed to fetch ${type} details`);
            }
            const components = await response.json();
            return { type, component: components.find(c => c.id === id) };
          }
          return { type, component: null };
        });

        // Wait for all API calls to complete
        const results = await Promise.all(promises);
        
        // Convert results array to an object
        const componentsObject = results.reduce((acc, { type, component }) => {
          acc[type] = component;
          return acc;
        }, {});
        
        setComponents(componentsObject);
      } catch (err) {
        console.error('Error fetching components:', err);
        setError('Could not load component details. Please try again later.');
      }
    };

    if (id) {
      fetchBuild();
    }
  }, [id]);

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!rating) {
      alert('Please select a rating before submitting');
      return;
    }

    setCommentSubmitting(true);
    try {
      // Get token from localStorage (assuming you store it there)
      const token = localStorage.getItem('token');
      if (!token) {
        alert('You must be logged in to leave a comment');
        return;
      }

      const response = await fetch(`${API_URL}/api/builds/public/${id}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          rating,
          comment
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit comment');
      }

      // Reset form
      setComment('');
      setRating(0);
      alert('Your comment has been submitted!');
      
      // Reload build to show updated ratings
      window.location.reload();
    } catch (err) {
      console.error('Error submitting comment:', err);
      alert('Could not submit your comment. Please try again later.');
    } finally {
      setCommentSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-xl">Loading build details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  if (!build) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-xl">Build not found</div>
      </div>
    );
  }

  // Calculate total price
  const totalPrice = Object.values(components)
    .filter(component => component && component.price)
    .reduce((sum, component) => sum + component.price, 0);

  return (
    <div className="min-h-screen bg-slate-100 py-8 mt-28">
      <div className="container mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Build Header */}
          <div className="bg-gray-800 text-white p-6">
            <h1 className="text-2xl font-bold">{build.build.name}</h1>
            <div className="mt-2 flex items-center">
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg 
                    key={star} 
                    fill={star <= Math.round(build.avg_rating || 0) ? "#FFB800" : "#E5E5E5"} 
                    height="20" 
                    width="20" 
                    className="mr-1" 
                    viewBox="0 0 24 24">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                  </svg>
                ))}
              </div>
              <span className="ml-2">
                {build.avg_rating ? build.avg_rating.toFixed(1) : 'No ratings'} ({build.rating_count || 0} reviews)
              </span>
            </div>
            <p className="mt-2 text-gray-300">Purpose: {build.build.purpose || 'Not specified'}</p>
          </div>
          
          {/* Build Content */}
          <div className="p-6 flex flex-col md:flex-row gap-8">
            {/* Build Image */}
            <div className="md:w-1/3">
              <img 
                src="/placeholder-image.jpg" 
                alt={`${build.build.name} Preview`} 
                className="w-full h-auto rounded-lg shadow-md"
              />
            </div>
            
            {/* Components List */}
            <div className="md:w-2/3">
              <h2 className="text-xl font-semibold mb-4">Components</h2>
              <div className="space-y-4">
                {Object.entries(components).map(([type, component]) => (
                  component && (
                    <div key={type} className="flex justify-between items-center border-b pb-2">
                      <div>
                        <span className="font-medium capitalize">{type}: </span>
                        <span>{component.name}</span>
                      </div>
                      <div className="font-semibold">
                        {component.price ? `${component.price} kr` : 'N/A'}
                      </div>
                    </div>
                  )
                ))}
                
                {/* Total Price */}
                <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                  <span className="text-lg font-bold">Total</span>
                  <span className="text-lg font-bold">{totalPrice} kr</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Comments Section */}
          <div className="p-6 bg-gray-50 border-t">
            <h2 className="text-xl font-semibold mb-4">Leave a Comment</h2>
            <form onSubmit={handleCommentSubmit} className="space-y-4">
              <div>
                <label className="block mb-2">Rating</label>
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button 
                      key={star} 
                      type="button"
                      onClick={() => setRating(star)}
                      className="mr-1 focus:outline-none"
                    >
                      <svg 
                        fill={star <= rating ? "#FFB800" : "#E5E5E5"} 
                        height="30" 
                        width="30" 
                        viewBox="0 0 24 24">
                        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                      </svg>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block mb-2" htmlFor="comment">Your Comment</label>
                <textarea 
                  id="comment"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="w-full p-2 border rounded-lg focus:ring focus:ring-blue-300"
                  rows="4"
                  placeholder="Share your thoughts on this build..."
                />
              </div>
              <button 
                type="submit" 
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                disabled={commentSubmitting}
              >
                {commentSubmitting ? 'Submitting...' : 'Submit Comment'}
              </button>
            </form>
            
            {/* Existing Comments */}
            <div className="mt-8">
              <h2 className="text-xl font-semibold mb-4">Comments</h2>
              {build.ratings && build.ratings.length > 0 ? (
                <div className="space-y-4">
                  {build.ratings.map((rating) => (
                    <div key={rating.id} className="bg-white p-4 rounded-lg shadow">
                      <div className="flex items-center mb-2">
                        <div className="flex mr-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <svg 
                              key={star} 
                              fill={star <= rating.rating ? "#FFB800" : "#E5E5E5"} 
                              height="16" 
                              width="16" 
                              className="mr-0.5" 
                              viewBox="0 0 24 24">
                              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                            </svg>
                          ))}
                        </div>
                        <span className="text-sm text-gray-600">
                          {new Date(rating.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p>{rating.comment}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No comments yet. Be the first to leave a review!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuildDetail;
