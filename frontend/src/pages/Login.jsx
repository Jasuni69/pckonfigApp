import React from 'react'

const Login = () => {
  return (
    <div className="wrapper bg-gradient-to-b from-slate-400 to-slate-200 min-h-screen flex items-center justify-center">
        <div className="bg-slate-300 border-2 border-slate-600 rounded-lg p-8 shadow-lg max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">Logga in</h2>
            <form className="space-y-4">
                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                    <input type="email" id="email" className="w-full p-2 rounded border border-slate-400" placeholder="Email" />
                </div>
                <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700">Lösenord</label>
                    <input type="password" id="password" className="w-full p-2 rounded border border-slate-400" placeholder="Lösenord" />
                </div>
                <button type="submit" className="w-full bg-slate-300 text-black hover:text-gray-700 hover:scale-105 border-2 hover:bg-slate-400 border-slate-600 rounded-lg p-1 shadow-lg">Logga in</button>
            </form>
        </div>
    </div>
  )
}

export default Login;

