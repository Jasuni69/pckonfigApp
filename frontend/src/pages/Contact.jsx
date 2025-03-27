import React from "react";

const Contact = () => {
  const handleSubmit = (e) => {
    e.preventDefault();
    // Just show an alert for now
    alert('Tack för ditt meddelande! Vi återkommer till dig så snart som möjligt.');
    // Reset the form
    e.target.reset();
  };

  return (
    <div className="wrapper bg-gradient-to-b from-slate-300 to-slate-200">
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">Kontakta Oss</h1>
        <p className="text-lg text-gray-600 mb-8 text-center">
          Har du frågor eller feedback? Skicka oss ett meddelande så återkommer vi till dig!
        </p>
      
        <form 
          className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md"
          onSubmit={handleSubmit}
        >
          {/* Name Field */}
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Ditt Namn
            </label>
            <input
              type="text"
              id="name"
              name="name"
              placeholder="Ange ditt namn"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              required
            />
          </div>
          
          {/* Email Field */}
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Din E-post
            </label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="Ange din e-postadress"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              required
            />
          </div>
          
          {/* Message Field */}
          <div className="mb-6">
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">
              Ditt Meddelande
            </label>
            <textarea
              id="message"
              name="message"
              placeholder="Skriv ditt meddelande här"
              rows="5"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              required
            ></textarea>
          </div>
          
          {/* Submit Button */}
          <div>
            <button
              type="submit"
              className="w-full text-black bg-slate-400 hover:text-gray-700 hover:scale-105 border-2 cursor-pointer border-slate-600 rounded-lg p-2 shadow-lg"
            >
              Skicka Meddelande
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Contact;
