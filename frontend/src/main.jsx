import React from "react";
import ReactDOM from "react-dom/client"; // For React 18+
import "./index.css"; // Tailwind's compiled CSS file
import App from "./App"; // Main app component

const root = ReactDOM.createRoot(document.getElementById("root")); // Mount to 'root' div
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
