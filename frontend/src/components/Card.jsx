import { useState } from 'react';
import { X } from 'lucide-react';

const Card = ({ title, className = "", onSelect, options }) => {
 const [isOpen, setIsOpen] = useState(false);
 const [selected, setSelected] = useState("");

 const defaultOptions = [
   { name: "Placeholder 1", price: "999" },
   { name: "Placeholder 2", price: "1499" },
   { name: "Placeholder 3", price: "1999" },
 ];

 const purposeOptions = [
   { name: "1080p Gaming", price: "0" },
   { name: "1440p Gaming", price: "0" },
   { name: "4K Gaming", price: "0" },
   { name: "Programmera/Utveckla", price: "0" },
   { name: "AI/Machine Learning", price: "0" },
   { name: "3D Rendering", price: "0" },
   { name: "Video Redigering", price: "0" },
   { name: "Basic Användning", price: "0" }
 ];

 const choices = options === 'purpose' ? purposeOptions : defaultOptions;

 const handleSelect = (e) => {
   const selectedOption = choices.find(opt => opt.name === e.target.value);
   if (selectedOption) {
     setSelected(e.target.value);
     onSelect(selectedOption);
     setIsOpen(false);
   }
 };

 return (
   <>
     <div className={`bg-slate-200 rounded-lg shadow-md p-6 cursor-pointer ${className}`} 
          onClick={() => setIsOpen(true)}>
       Välj {title}
     </div>

     {isOpen && (
       <div className="fixed inset-0 flex" onClick={() => setIsOpen(false)}>
         <div className="m-auto bg-slate-400 p-8 rounded-lg border-2 border-slate-800 shadow-lg" onClick={e => e.stopPropagation()}>
           <div className="flex gap-4 items-start justify-between mb-4">
             <h2 className="text-black">{title}</h2>
             <button className="bg-slate-300 rounded-lg p-1 border-2 border-slate-800 shadow-lg -mt-4 -mr-4 hover:bg-slate-400 hover:scale-80 scale-75" onClick={() => setIsOpen(false)}><X className="text-black" /></button>
           </div>

           <select 
             value={selected} 
             onChange={handleSelect}
             className="w-full p-2 rounded"
           >
             <option value="">Välj</option>
             {choices.map((option, index) => (
               <option key={index} value={option.name}>
                 {option.name} {option.price !== "0" ? `- ${option.price}kr` : ''}
               </option>
             ))}
           </select>
         </div>
       </div>
     )}
   </>
 );
};

export default Card;