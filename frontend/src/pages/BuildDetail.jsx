import React from 'react';
import { useParams } from 'react-router-dom';

const BuildDetail = () => {
  console.log("Minimal BuildDetail rendering");
  const { id } = useParams();
  
  return (
    <div style={{padding: "50px", backgroundColor: "red", color: "white", minHeight: "100vh"}}>
      <h1>BUILD DETAIL TEST PAGE</h1>
      <p>Build ID: {id}</p>
    </div>
  );
};

export default BuildDetail;