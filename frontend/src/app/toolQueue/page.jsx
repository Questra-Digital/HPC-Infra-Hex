"use client"
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'next/navigation';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';
import API_BASE_URL from '../URL';
import Link from 'next/link'

const ToolsQueue = () => {
  const [runningQueue, setRunningQueue] = useState([]);
  const [waitingQueue, setWaitingQueue] = useState([]);
  const searchParams = useSearchParams();
  const name = searchParams.get("name");

  useEffect(() => {
    const fetchQueues = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/get-queues/${name}`);
        setRunningQueue(response.data.runningQueue);
        setWaitingQueue(response.data.waitingQueue);
      } catch (error) {
        console.error('Error fetching queues:', error);
      }
    };

    fetchQueues();
  }, [name]);

  return (
    <div className="flex h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />
      <div className='mt-10 flex-1 text-[#132577] text-xl font-bold'>
        Tools Queue - {name}
      </div>
      <div className="bg-[#132577] m-[5%] py-[0%] px-[5%] h-[100%] flex flex-col gap-10 md:flex-row items-center w-[80%]">
        <div className='flex flex-col p-10 items-center text-center h-full w-full rounded-2xl bg-white text-[#132577]'>
          <h2 className="text-2xl font-bold">Running Queue</h2>
          <div className='pt-6 px-4 overflow-auto text-xs text-start w-full'>
            {runningQueue.map((user, index) => (
              <div key={index} className='p-2 border-b border-gray-300'>
                <h3 className="text-md font-semibold">{user.username}</h3>
              </div>
            ))}
          </div>
        </div>
        <div className='flex flex-col p-10 items-center text-center h-full w-full rounded-2xl bg-white text-[#132577]'>
          <h2 className="text-2xl font-bold">Waiting Queue</h2>
          <div className='pt-6 px-4 overflow-auto text-xs text-start w-full'>
            {waitingQueue.map((user, index) => (
              <div key={index} className='p-2 border-b border-gray-300'>
                <h3 className="text-md font-semibold">{user.username}</h3>
              </div>
            ))}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default ToolsQueue;
