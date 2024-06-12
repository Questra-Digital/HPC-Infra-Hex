"use client";
import React, { useEffect, useState, useMemo } from 'react';
import API_BASE_URL from '../../URL';
import axios from 'axios';
const MainNavbar = ({ title }) => {
  const [role, setRole] = useState(null);



const logout = async () => {
  try {
    // Retrieve user ID from session storage
    const userId = sessionStorage.getItem('user_id');

    // Send a request to the backend to logout the user
    const response = await axios.post(`${API_BASE_URL}/logout`, { user_id: userId });

    // Check if the logout request was successful
    if (response.status === 200) {
      // Clear session storage
      sessionStorage.clear();
      // Redirect to login page
      window.location.href = '/login';
    } else {
      throw new Error('Failed to logout');
    }
  } catch (error) {
    console.error('Logout error:', error);
    // Handle error
  }
};


  useEffect(() => {
    // Retrieve the user role from session storage
    const userRole = sessionStorage.getItem('user_role');
    setRole(userRole);
  }, []);

  // Define the pages for different roles with indexing
  const pagesConfig = {
    common: [
      { title: 'Home', link: '/landingPage', index: 1 },
      { title: 'Run Command', link: '/runCommand', index: 2 },
      { title: 'MyTools', link: '/myTools', index: 3 },
      { title: 'Login', link: '/login', index: 4 },
      { title: 'Logout',  index: 5, onClick: logout } // Add Logout link with onClick
    ],
    root: [
      { title: 'Cluster Consumption', link: '/clusterConsumptionDetail', index: 2 },
      { title: 'Drag & Drop Tools', link: '/dragnDropTools', index: 3 },
      { title: 'Add Users', link: '/addUser', index: 4 },
    ],
    admin: [
      { title: 'Cluster Consumption', link: '/clusterConsumptionDetail', index: 2 },
      { title: 'Drag & Drop Tools', link: '/dragnDropTools', index: 3 },
      { title: 'Add Users', link: '/addUser', index: 4 },
    ],
  };

  const pages = useMemo(() => {
    let combinedPages = [...pagesConfig.common];

    if (role === 'root') {
      combinedPages = [...pagesConfig.root, ...pagesConfig.common];
    } else if (role === 'admin') {
      combinedPages = [...pagesConfig.admin, ...pagesConfig.common];
    }

    // Remove duplicates by creating a new array with unique pages based on titles
    const uniquePages = Array.from(new Set(combinedPages.map(page => page.title)))
      .map(title => combinedPages.find(page => page.title === title));

    // Sort pages by index
    uniquePages.sort((a, b) => a.index - b.index);

    return uniquePages;
  }, [role]);

 
  return (
    <div className="bg-[#132577] flex flex-col items-center h-auto px-20 w-full py-4">
      <div className='flex flex-1 items-center justify-between w-full'>
        <div className="flex items-center justify-center">
          <img src="/logo.svg" className="h-24" alt="Logo" />
          <a href='/landingPage' className="text-xl md:text-2xl font-semibold ml-4">{title}</a>
        </div>
        <div className="text-xs flex">
          {pages.map(page => (
            <a
              key={page.link} // Using link as the key
              href={page.link}
              onClick={page.onClick ? (e) => { e.preventDefault(); page.onClick(); } : null}
              className="text-white ml-4 hover:text-gray-300 transition duration-300"
            >
              {page.title}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MainNavbar;
