import { useState, useEffect } from "react";
import { X } from "lucide-react";

const Card = ({ title, className = "", onSelect, options }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [choices, setChoices] = useState([]);
  const [search, setSearch] = useState("");

  const purposeOptions = [
    { name: "1080p Gaming", price: "0" },
    { name: "1440p Gaming", price: "0" },
    { name: "4K Gaming", price: "0" },
    { name: "Programmera/Utveckla", price: "0" },
    { name: "AI/Machine Learning", price: "0" },
    { name: "3D Rendering", price: "0" },
    { name: "Video Redigering", price: "0" },
    { name: "Basic Användning", price: "0" },
  ];

  useEffect(() => {
    if (options === "purpose") {
      setChoices(purposeOptions);
    } else {
      fetch(`http://13.53.243.200:8000/${options}`)
        .then((response) => response.json())
        .then((data) => setChoices(data))
        .catch((error) => console.error(`Error fetching ${options}:`, error));
    }
  }, [options]);

  const filteredChoices = search
    ? choices.filter((opt) =>
        opt.name.toLowerCase().includes(search.toLowerCase())
      )
    : choices;

  const handleSelect = (option) => {
    setSelected(option); // Only store one selection per category
    onSelect(title, option); // Pass the category title and selected option to parent
    setIsOpen(false);
    setSearch("");
  };

  return (
    <>
      {/* Clickable Card */}
      <div
        className={`bg-slate-200 rounded-lg shadow-md p-6 cursor-pointer ${className}`}
        onClick={() => setIsOpen(true)}
      >
        {selected ? `${title}: ${selected.name}` : `Välj ${title}`}
      </div>

      {isOpen && (
        <div className="fixed inset-0 flex" onClick={() => setIsOpen(false)}>
          <div
            className="m-auto bg-slate-400 p-8 rounded-lg border-2 border-slate-800 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex gap-4 items-start justify-between mb-4">
              <h2 className="text-black">{title}</h2>
              <button
                className="bg-slate-300 rounded-lg p-1 border-2 border-slate-800 shadow-lg -mt-4 -mr-4 hover:bg-slate-400 hover:scale-80 scale-75"
                onClick={() => setIsOpen(false)}
              >
                <X className="text-black" />
              </button>
            </div>

            {/* Search Bar */}
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full p-2 rounded border border-gray-500"
              placeholder="Sök..."
            />

            {/* Filtered Dropdown List */}
            {filteredChoices.length > 0 ? (
              <ul className="bg-white border border-gray-300 mt-2 rounded shadow-lg max-h-40 overflow-y-auto">
                {filteredChoices.map((option, index) => (
                  <li
                    key={index}
                    onClick={() => handleSelect(option)}
                    className="p-2 cursor-pointer hover:bg-gray-200"
                  >
                    {option.name} {option.price !== "0" ? `- ${option.price}kr` : ""}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-600 mt-2">Inga resultat hittades.</p>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default Card;
