"use client"
import React, { useState } from 'react';
import Axios from 'axios';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';

const AddCluster = () => {
  const [command, setCommand] = useState('');
  const [commandResponse, setCommandResponse] = useState('');
  
  const pages = [
    { title: 'Home', link: '/' },
    { title: 'About Us', link: '/about' },
    { title: 'Portfolio', link: '/portfolio' },
    { title: 'Expertise', link: '/expertise' },
    { title: 'Clients', link: '/clients' },
    { title: 'Services', link: '/services' },
    { title: 'Contact', link: '/contact' },
  ]; 

  const handleCommand = (com) => {
    setCommand(com);
  };

  const handleCommandResponse = (com) => {
    setCommandResponse(com);
  };

  const handleEnterPress = async (e) => {
    if (e.key === 'Enter') {
      try {
        const response = await Axios.post('http://127.0.0.1:5000/run-command/master', { command });
        setCommandResponse(JSON.stringify(response.data.output));
      } catch (error) {
        setCommandResponse(JSON.stringify(error));
      }
    }
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" pages={pages} />

      <div className='mt-10 flex-1 text-[#132577] text-xl font-bold'>
        Run Command On VmWares
      </div>

      <div className='flex items-center justify-center gap-[5%] text-black text-sm w-full px-[15%] pt-[5%] pb-[2%]'>
        <input
          type="text"
          placeholder="Enter Command here"
          value={command}
          onChange={(e) => handleCommand(e.target.value)}
          onKeyDown={handleEnterPress}
          className="w-full bg-gray-300 rounded text-black p-4"
        />
      </div>

      <div className='flex items-center justify-center gap-[5%] text-black text-sm w-full px-[15%] pb-[5%]'>
        <textarea
          type="text"
          placeholder="Command Response Here"
          value={commandResponse}
          onChange={(e) => handleCommandResponse(e.target.value)}
          className="w-full h-60 bg-gray-200 rounded text-black p-4"
        />
      </div>

      <Footer className="flex-7" />
    </div>
  );
};

export default AddCluster;
