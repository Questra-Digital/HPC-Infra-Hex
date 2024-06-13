"use client"
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';
import Link from 'next/link';
import API_BASE_URL from '../URL';
import { FaTrashAlt } from 'react-icons/fa';
import Swal from 'sweetalert2';

const MyTools = () => {
  const [tools, setTools] = useState([]);
  const [role, setRole] = useState(null);

  useEffect(() => {
    const userRole = sessionStorage.getItem('user_role');
    setRole(userRole);

    const fetchTools = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/tools`); 
        const filteredTools = response.data.filter(tool => (tool.installed === "pending" || tool.installed === "true"));
        setTools(filteredTools);
      } catch (error) {
        console.error('Error fetching tools:', error);
      }
    };

    fetchTools();
  }, []);

  const handleUninstall = async (toolId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/uninstall-tool/${toolId}`);
      if (response.status === 200) {
        setTools(prevTools => prevTools.filter(tool => tool._id !== toolId));
        Swal.fire({
          icon: 'success',
          title: 'Uninstalled!',
          text: 'Tool has been uninstalled successfully.',
        });
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error!',
          text: 'Failed to uninstall the tool.',
        });
      }
    } catch (error) {
      console.error('Error uninstalling tool:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error!',
        text: 'Failed to uninstall the tool.',
      });
    }
  };

  return (
    <div className="flex h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />
      <div className='mt-10 text-[#132577] text-xl font-bold'>
        My Tools
      </div>
      <div className="grid h-full w-[75%] m-14 grid-cols-3 gap-4">
        {tools.map((tool, index) => (
          <div key={index} className="relative border hover:bg-[#33469e] rounded-2xl bg-[#132577] text-white p-8">
            <Link href={{
              pathname: role === 'admin' || role === 'root' ? '/getStatusofTool' : '/toolQueue',
              query: { name: `${tool.tool_name}`, id: tool._id },
            }}>
              <div 
                className="cursor-pointer"
                onMouseEnter={(e) => { e.target.style.cursor = 'pointer'; }} // Show hand cursor on hover
                onMouseLeave={(e) => { e.target.style.cursor = 'auto'; }} // Reset cursor when not hovered
              >
                <div className='flex items-center gap-6'>
                  <img src={tool.logo} alt={tool.tool_name} className="w-14 h-14 inline-block rounded-full" /> 
                  <div>
                    <h2 className="text-xl font-bold">{tool.tool_name}</h2>
                    <p className="mt-2 text-sm mr-4 font-normal">{tool.installed ? "Installed" : "Not Installed"}</p>
                  </div>
                </div>
              </div>
            </Link>
            {(role === 'admin' || role === 'root') && (
              <button 
                className="absolute top-4 right-4 text-red-600"
                onClick={() => handleUninstall(tool._id)}
              >
                <FaTrashAlt size={20} />
              </button>
            )}
          </div>
        ))}
      </div>
      <Footer className="flex-7" />
    </div>
  );
};

export default MyTools;
