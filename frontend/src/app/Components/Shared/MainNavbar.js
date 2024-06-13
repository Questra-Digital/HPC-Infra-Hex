"use client";
import React, { useEffect, useState, useMemo } from 'react';
import API_BASE_URL from '../../URL';
import axios from 'axios';

const MainNavbar = ({ title }) => {
  const [role, setRole] = useState(null);

  const logout = async () => {
    try {
      const userId = sessionStorage.getItem('user_id');
      const response = await axios.post(`${API_BASE_URL}/logout`, { user_id: userId });

      if (response.status === 200) {
        sessionStorage.clear();
        window.location.href = '/login';
      } else {
        throw new Error('Failed to logout');
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  useEffect(() => {
    const userRole = sessionStorage.getItem('user_role');
    setRole(userRole);
  }, []);

  const pagesConfig = {
    common: [
      { title: 'Home', link: '/landingPage', index: 1 },
      { title: 'Run Command', link: '/runCommand', index: 2 },
      { title: 'MyTools', link: '/myTools', index: 3 },
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
    let combinedPages = [];

    if (role) {
      combinedPages = [...pagesConfig.common, { title: 'Logout', index: 5, onClick: logout }];
      if (role === 'root') {
        combinedPages = [...pagesConfig.root, ...combinedPages];
      } else if (role === 'admin') {
        combinedPages = [...pagesConfig.admin, ...combinedPages];
      }
    } else {
      combinedPages = [...pagesConfig.common, { title: 'Login', link: '/login', index: 4 }];
    }

    const uniquePages = Array.from(new Set(combinedPages.map(page => page.title)))
      .map(title => combinedPages.find(page => page.title === title));

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
              key={page.title}
              href={page.link || '#'}
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
