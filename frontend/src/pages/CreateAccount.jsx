import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_URL } from '../config';

const CreateAccount = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Account created successfully:', data);
        navigate('/login'); 
      } else {
        setError(data.detail || 'Ett fel uppstod vid registrering');
      }
    } catch (error) {
      console.error('Error during registration:', error);
      setError('Ett fel uppstod vid anslutning till servern');
    }
  };

  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200">
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Skapa Konto</h1>
        <div className="bg-slate-300 border-2 border-slate-600 rounded-lg p-8 shadow-lg max-w-md w-full mx-4">
          <form onSubmit={handleSubmit}>
            {error && (
              <div className="mb-4 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}
            <div className="mb-4">
              <input 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="w-full p-2 rounded border border-slate-400"
                required
              />
            </div>
            <div className="mb-4">
              <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Lösenord"
                className="w-full p-2 rounded border border-slate-400"
                required
              />
            </div>
            <button 
              type="submit" 
              className="w-full bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg"
            >
              Skapa Konto
            </button>
          </form>
          
          <div className="mt-8 bg-slate-200 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Fördelar med ett konto:</h2>
            <ul className="space-y-3">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Spara dina PC-byggen och återkom till dem senare</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Få personliga rekommendationer från vår AI för din datorbygge</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateAccount;