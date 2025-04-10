import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_URL } from '../config';

/**
 * BuildDetail - Displays comprehensive information about a specific PC build
 * Shows components, pricing, user ratings and comments for a public build
 */
const BuildDetail = () => {
  // ===== STATE MANAGEMENT =====
  const { id } = useParams();
  const [build, setBuild] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comment, setComment] = useState('');
  const [rating, setRating] = useState(0);
  const [commentSubmitting, setCommentSubmitting] = useState(false);

  // ===== DATA FETCHING =====
  useEffect(() => {
    const fetchBuild = async () => {
      try {
        const response = await fetch(`${API_URL}/api/builds/public/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch build details');
        }
        const data = await response.json();
        console.log("Fetched build data:", data);
        setBuild(data);
      } catch (err) {
        console.error('Error fetching build:', err);
          setError('Could not load build details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchBuild();
    }
  }, [id]);

  // ===== EVENT HANDLERS =====
  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!rating) {
      alert('Betygsätt först');
      return;
    }

    setCommentSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Du måste vara inloggad för att lämna en kommentar');
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
        throw new Error('Misslyckades att skicka kommentar');
      }

      setComment('');
      setRating(0);
      alert('Din kommentar har skickats!');
      
      window.location.reload();
    } catch (err) {
      console.error('Error submitting comment:', err);
      alert('Kunde inte skicka din kommentar. Vänligen försök igen senare.');
    } finally {
      setCommentSubmitting(false);
    }
  };

  // ===== LOADING STATE UI =====
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 py-8 mt-28">
        <div className="container mx-auto px-4">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* SKELETON: Header */}
            <div className="bg-gray-800 p-6">
              <div className="h-8 bg-gray-700 rounded animate-pulse w-1/3 mb-3"></div>
              <div className="flex items-center mt-2">
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-5 w-5 bg-gray-700 rounded animate-pulse"></div>
                  ))}
                </div>
                <div className="h-4 bg-gray-700 rounded animate-pulse w-24 ml-2"></div>
              </div>
              <div className="h-4 bg-gray-700 rounded animate-pulse w-1/2 mt-2"></div>
            </div>
            
            {/* SKELETON: Content */}
            <div className="p-6 flex flex-col md:flex-row gap-8">
              {/* SKELETON: Image */}
              <div className="md:w-1/3">
                <div className="w-full h-64 bg-gray-200 rounded-lg animate-pulse"></div>
              </div>
              
              {/* SKELETON: Components List */}
              <div className="md:w-2/3">
                <div className="h-6 bg-gray-200 rounded animate-pulse w-1/4 mb-4"></div>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                    <div key={i} className="flex justify-between items-center border-b pb-2">
                      <div className="h-5 bg-gray-200 rounded animate-pulse w-1/2"></div>
                      <div className="h-5 bg-gray-200 rounded animate-pulse w-16"></div>
                    </div>
                  ))}
                  <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                    <div className="h-6 bg-gray-200 rounded animate-pulse w-16"></div>
                    <div className="h-6 bg-gray-200 rounded animate-pulse w-20"></div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* SKELETON: Comments */}
            <div className="p-6 bg-gray-50 border-t">
              <div className="h-6 bg-gray-200 rounded animate-pulse w-1/4 mb-4"></div>
              <div className="space-y-3">
                <div className="h-10 bg-gray-200 rounded animate-pulse w-1/3"></div>
                <div className="h-32 bg-gray-200 rounded animate-pulse w-full"></div>
                <div className="h-10 bg-gray-200 rounded animate-pulse w-1/4"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ===== ERROR STATE UI =====
  if (error) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  // ===== EMPTY STATE UI =====
  if (!build) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-xl">Build not found</div>
      </div>
    );
  }

  // ===== DATA PROCESSING =====
  const buildData = build.build;
  
  // Calculate total price from all components
  const totalPrice = [
    buildData.cpu?.price || 0,
    buildData.gpu?.price || 0,
    buildData.motherboard?.price || 0,
    buildData.ram?.price || 0,
    buildData.storage?.price || 0,
    buildData.psu?.price || 0,
    buildData.case?.price || 0,
    buildData.cooler?.price || 0
  ].reduce((sum, price) => sum + price, 0);

  // ===== MAIN RENDER =====
  return (
    <div className="min-h-screen bg-slate-100 py-8 mt-28">
      <div className="container mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* ===== HEADER SECTION ===== */}
          <div className="bg-gray-800 text-white p-6">
            <h1 className="text-2xl font-bold">{buildData.name}</h1>
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
            <p className="mt-2 text-gray-300">Användningsområde: {buildData.purpose || 'Ej specificerat'}</p>
          </div>
          
          {/* ===== BUILD DETAILS SECTION ===== */}
          <div className="p-6 flex flex-col md:flex-row gap-8">
            {/* Build Image */}
            <div className="md:w-1/3">
              <img 
                src="/placeholder-image.jpg" 
                alt={`${buildData.name} Preview`} 
                className="w-full h-auto rounded-lg shadow-md"
              />
            </div>
            
            {/* ===== COMPONENTS LIST ===== */}
            <div className="md:w-2/3">
              <h2 className="text-xl font-semibold mb-4">Components</h2>
              <div className="space-y-4">
                {/* CPU item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">CPU: </span>
                    <span>{buildData.cpu ? buildData.cpu.name : 'No CPU selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.cpu?.price ? `${buildData.cpu.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* GPU item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">GPU: </span>
                    <span>{buildData.gpu ? buildData.gpu.name : 'No GPU selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.gpu?.price ? `${buildData.gpu.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* Motherboard item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">Motherboard: </span>
                    <span>{buildData.motherboard ? buildData.motherboard.name : 'No Motherboard selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.motherboard?.price ? `${buildData.motherboard.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* RAM item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">RAM: </span>
                    <span>{buildData.ram ? buildData.ram.name : 'No RAM selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.ram?.price ? `${buildData.ram.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* Storage item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">Storage: </span>
                    <span>{buildData.storage ? buildData.storage.name : 'No Storage selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.storage?.price ? `${buildData.storage.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* PSU item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">PSU: </span>
                    <span>{buildData.psu ? buildData.psu.name : 'No PSU selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.psu?.price ? `${buildData.psu.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* Case item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">Case: </span>
                    <span>{buildData.case ? buildData.case.name : 'No Case selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.case?.price ? `${buildData.case.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* Cooler item */}
                <div className="flex justify-between items-center border-b pb-2">
                  <div>
                    <span className="font-medium capitalize">Cooler: </span>
                    <span>{buildData.cooler ? buildData.cooler.name : 'No Cooler selected'}</span>
                  </div>
                  <div className="font-semibold">
                    {buildData.cooler?.price ? `${buildData.cooler.price} kr` : 'N/A'}
                  </div>
                </div>
                
                {/* ===== PRICE SUMMARY ===== */}
                <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                  <span className="text-lg font-bold">Total</span>
                  <span className="text-lg font-bold">{totalPrice} kr</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* ===== COMMENTS SECTION ===== */}
          <div className="p-6 bg-gray-50 border-t">
            <h2 className="text-xl font-semibold mb-4">Leave a Comment</h2>
            {/* ===== COMMENT FORM ===== */}
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
            
            {/* ===== REVIEWS LIST ===== */}
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
