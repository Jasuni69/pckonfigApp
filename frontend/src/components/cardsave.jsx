import { useState } from 'react';

const Card = ({ title }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
   
    return (
      <>
        <div className="bg-white rounded-lg shadow-md p-6 cursor-pointer" onClick={() => setIsModalOpen(true)}>
          Välj {title}
        </div>
   
        {isModalOpen && (
          <div className="fixed inset-0 flex justify-center items-center z-50" onClick={() => setIsModalOpen(false)}>
            <div className="m-auto bg-white p-8 rounded-lg w-3/4 h-3/4 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h1 className="text-2xl font-bold">{title}</h1>
            <p>Details about {title}</p>
            <button onClick={() => setIsModalOpen(false)}>Close</button>
            </div>
          </div>
        )}
      </>
    );
   };

   export default Card;