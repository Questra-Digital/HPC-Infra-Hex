"use client"
import React, { useState } from 'react';
import Axios from 'axios';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';

const AddCluster = () => {
  const [command, setCommand] = useState('');
  const [commandResponse, setCommandResponse] = useState('');
  const [vmware, setVmWare] = useState('');
  
  const handleCommand = (com) => {
    setCommand(com);
  };

  const handleCommandResponse = (com) => {
    setCommandResponse(com);
  };

  const handleEnterPress = async (e) => {
    if (e.key === 'Enter') {
      try {
        const response = await Axios.post(`http://127.0.0.1:5000/run-command/${vmware}`, { command });
        setCommandResponse(JSON.stringify(response.data));
      } catch (error) {
        setCommandResponse(JSON.stringify(error));
      }
    }
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure"  />

      <div className='mt-10 flex-1 text-[#132577] text-xl font-bold'>
        Run Command On VmWares
      </div>

      <div className=" text-black  flex mb-4 flex-col flex-1 w-full px-[15%] pt-[2%] pb-[0%]">
          <label className="mb-2">Select VmWare:</label>
          <select onChange={(e) => {setVmWare(e.target.value)}} className="bg-gray-300 p-[2%] text-black rounded">
            <option value="master">master</option>
          </select>
      </div>

      <div className='flex items-center justify-center gap-[5%] text-black text-sm w-full px-[15%] pt-[0%] pb-[2%]'>
        <input
          type="text"
          placeholder="Enter Command here"
          value={command}
          onChange={(e) => handleCommand(e.target.value)}
          onKeyDown={handleEnterPress}
          className="w-full bg-gray-300 rounded text-black p-8"
        />
      </div>

      <div className='flex items-center justify-center gap-[5%] text-black text-sm w-full px-[15%] pb-[5%]'>
        <textarea
          type="text"
          placeholder="Command Response Here"
          value={commandResponse}
          onChange={(e) => handleCommandResponse(e.target.value)}
          className="w-full h-[400px] bg-gray-200 rounded text-black p-8"
        />
      </div>

      <Footer className="flex-7" />
    </div>
  );
};

export default AddCluster;
