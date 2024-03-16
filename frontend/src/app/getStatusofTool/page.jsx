"use client"
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from "next/navigation";
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';



const getStatus = () => {
  const [status,setStat] = useState ([]);
  const [pods,setPods] = useState ([]);
  const searchParams = useSearchParams();
  const name = searchParams.get("name");

  useEffect(() => {
    const fetchStatus = async () => {

      try {
        const response = await axios.get('http://127.0.0.1:5000/get-status'); 
        console.log("sttaus" , response.data);
        setStat(response.data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }


    };

    const getPods = async () => {
      if(name == "JupyterHub"){
        try {
          const response = await axios.get('http://127.0.0.1:5000/get-pods/jhub'); 
          console.log("podss" , response.data.pods[0].name);
          setPods(response.data.pods);
        } catch (error) {
          console.error('Error fetching pods:', error);
        }
      }
    };

    fetchStatus();
    getPods();
  }, []);


  
  return (
    <div className="flex  h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />.
      <div className='mt-10 text-[#132577] text-xl font-bold'>
        {name}
      </div>
      <div className='flex h-[60%] w-[80%] m-14 gap-16'>
        <div className='p-10 items-center text-center h-full w-full rounded-2xl bg-[#132577] text-white'>
          <h className="text-2xl font-bold"> Status of Tool</h>
        </div>
        <div className='p-10 items-center text-center h-full w-full rounded-2xl bg-[#132577] text-white'>
          <h className="text-2xl font-bold">Pods of Tool</h>
          {pods.map((pod, index) => (
          <div key={index} className='text-start pt-6 px-4' >
            <h2 className="text-md font-semibold">{pod.name}</h2>
            <p className="text-sm">{pod.status}</p>
          </div>
        ))}
          
          
        </div>
      </div>     
     
      {/* <Footer /> */}
    </div>
  );
};


export default getStatus;
