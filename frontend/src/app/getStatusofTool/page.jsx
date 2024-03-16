"use client"
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';

const getStatus = () => {
  const [status,setStat] = useState ();
  const [pods,setPods] = useState ();

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/get-status'); 
        setStat(response.data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    const getPods = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/get-pods/jhub'); 
        setPods(response.data);
      } catch (error) {
        console.error('Error fetching pods:', error);
      }
    }

    fetchStatus();
    getPods();
  }, []);


  
  return (
    <div className="flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />
      <div className='mt-10 text-[#132577] text-xl font-bold'>
        Status of Tool
      </div>
      <div className='grid h-full w-[75%] m-14 grid-cols-2 gap-4'>
        <div className='rounded-2xl bg-[#132577] text-white'>
          {status}
        </div>
        <div className='rounded-2xl bg-[#132577] text-white'>
        {pods}
        </div>
      </div>
     
     
      {/* <Footer /> */}
    </div>
  );
};

export default getStatus;
