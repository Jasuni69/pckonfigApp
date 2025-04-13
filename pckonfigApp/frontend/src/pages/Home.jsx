          <div className="relative h-80 bg-gradient-to-r from-slate-700 to-slate-900 overflow-hidden">
            {/* Featured build info */}
            <div className="absolute inset-0 flex flex-col justify-end p-8 text-white bg-gradient-to-t from-black/70 to-transparent">
              {/* Add a background color as fallback */}
              <div className="absolute inset-0 bg-slate-800">
                {/* Show placeholder image */}
                <img 
                  src="/placeholder-image.jpg" 
                  alt={build.name} 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex justify-between items-end relative z-10">
                <div>
                  <h2 className="text-3xl font-bold mb-2">{build.name}</h2>
                  <p className="text-lg mb-1">
                    {build.cpu ? build.cpu.name : 'No CPU'} | {build.gpu ? build.gpu.name : 'No GPU'}
                  </p>
                  <p className="text-sm text-slate-300 mb-4">
                    {build.ram ? build.ram.name : 'No RAM'} | {build.storage ? build.storage.name : 'No Storage'}
                  </p>
                </div>
              </div>
            </div>
          </div> 