"use client";
import React, { useEffect, useState } from 'react';

const MainNavbar = ({ title }) => {
  const [role, setRole] = useState(null);

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
    ],
    root: [
      // { title: 'Register (Root)', link: '/registerAsRootUser', index: 0 },
      { title: 'Cluster Consumption', link: '/clusterConsumptionDetail', index: 2},
      { title: 'Drag & Drop Tools', link: '/dragnDropTools', index: 3 },
      { title: 'Add Users', link: '/addUser', index: 4},
    ],
    admin: [
      { title: 'Cluster Consumption', link: '/clusterConsumptionDetail', index: 2 },
      { title: 'Drag & Drop Tools', link: '/dragnDropTools', index: 3},
      { title: 'Add Users', link: '/addUser', index: 4},
    ],
  };

  // Combine the common pages with role-specific pages and sort them by index
  let pages = [...pagesConfig.common];
  if (role === 'root') {
    pages = [...pagesConfig.root, ...pagesConfig.common];
  } else if (role === 'admin') {
    pages = [...pagesConfig.admin, ...pagesConfig.common];
  }

  // Remove duplicates by creating a new array with unique pages based on titles
  pages = Array.from(new Set(pages.map(page => page.title)))
    .map(title => pages.find(page => page.title === title));

  // Sort pages by index
  pages.sort((a, b) => a.index - b.index);

  return (
    <div className="bg-[#132577] flex flex-col items-center h-auto px-20 w-full py-4">
      <div className='flex flex-1 items-center justify-between w-full'>
        <div className="flex items-center justify-center">
          <img src="/logo.svg" className="h-24" alt="Logo" />
          <a href='/landingPage' className="text-xl md:text-2xl font-semibold ml-4">{title}</a>
        </div>
        <div className="text-xs flex">
          {pages.map((page, index) => (
            <a
              key={index}
              href={page.link}
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
