"use client"
import React, { useState } from 'react';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';

const VersionControl = () => {
  const [versions, setVersions] = useState([
    { version: 'V1.0', type:"Major", status: 'published', lastUpdated: '2024-01-09' },
    { version: 'V1.1', type:"Minor", status: 'unpublished', lastUpdated: '2024-01-09' },
    { version: 'V2.0', type:"Major", status: 'unpublished', lastUpdated: '2024-01-09' },
    { version: 'V2.1', type:"Minor", status: 'unpublished', lastUpdated: '2024-01-09' },
    // Add more versions as needed
  ]);

  const handlePublish = (index) => {
    const updatedVersions = [...versions];
    updatedVersions[index].status = 'published';
    setVersions(updatedVersions);
  };

  const handleDelete = (index) => {
    const updatedVersions = [...versions];
    updatedVersions.splice(index, 1);
    setVersions(updatedVersions);
  };

  const pages = [
    { title: 'Home', link: '/' },
    { title: 'About Us', link: '/about' },
    { title: 'Portfolio', link: '/portfolio' },
    { title: 'Expertise', link: '/expertise' },
    { title: 'Clients', link: '/clients' },
    { title: 'Services', link: '/services' },
    { title: 'Contact', link: '/contact' },
  ];

  return (
    <div className="h-screen flex flex-col gap-[10%] items-center text-white w-screen">
      <MainNavbar className="" title="HPC MLOPs Infrastructure" pages={pages} />

      <div className="text-sm flex flex-col px-[10%] w-full justify-center gap-4">
        {versions.map((version, index) => (
          <div key={index} className="flex items-center justify-between rounded-md bg-[#132577] border p-8">
            <div>Version: {version.version}</div>
            <div>Type: {version.type}</div>
            <div>Last Updated: {version.lastUpdated}</div>
              <div className='flex gap-[2%]'>
                <button className="flex-1 mx-5" onClick={() => handlePublish(index)}>Publish</button>
                <button className='flex-2 mx-5' onClick={() => handleDelete(index)}>Delete</button>
              </div>
          </div>
        ))}
      </div>

      <Footer className="flex-7" />
    </div>
  );
};

export default VersionControl;
