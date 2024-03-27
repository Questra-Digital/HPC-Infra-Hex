"use client"
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';
import Link from 'next/link'

const MyTools = () => {
  const [tools, setTools] = useState([]);

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/tools'); 
        const filteredTools = response.data.filter(tool =>  (tool.installed  == "pending" || tool.installed == "true") );
        console.log(response.data);
        setTools(filteredTools);
      } catch (error) {
        console.error('Error fetching tools:', error);
      }
    };

    fetchTools();
  }, []);

 
  return (
    <div className="flex h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />
      <div className='mt-10 text-[#132577] text-xl font-bold'>
        My Tools
      </div>
      <div className="grid  h-full w-[75%] m-14 grid-cols-3 gap-4">
        {tools.map((tool, index) => (
          <Link href={{
            pathname: '/getStatusofTool',
            query: { name: `${tool.tool_name}` },
          }}>
          <div key={index} 
               className="border hover:bg-[#33469e] rounded-2xl bg-[#132577] text-white p-8 cursor-pointer"
               onMouseEnter={(e) => { e.target.style.cursor = 'pointer'; }} // Show hand cursor on hover
               onMouseLeave={(e) => { e.target.style.cursor = 'auto'; }}> {/* Reset cursor when not hovered */}
                <div className='flex items-center gap-6'>
                  <img src={tool.logo} alt={tool.tool_name} className="w-14 h-14 inline-block rounded-full" /> 
                  <div>
                      <h2 className="text-xl font-bold">{tool.tool_name}</h2>
                      <p className="mt-2 text-sm mr-4 font-normal">{tool.installed ? "Installed" : "Not Installed"}</p>
                  </div>
               </div>
            
          </div>
          </Link>
        ))}
      </div>
      <Footer className="flex-7" />
    </div>
  );
};

export default MyTools;
