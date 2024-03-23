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
  const [allPodsRunning, setAllPodsRunning] = useState(false); // State to track if all pods are running
  


  useEffect(() => {
    const fetchStatus = async () => {

      try {
        const response = await axios.get('http://127.0.0.1:5000/get-status/JupyterHub'); 
        console.log("sttaus" , response.data.status);
        setStat(response.data.status);
      } catch (error) {
        console.error('Error fetching status:', error);
      }


    };


    const getPods = async () => {
      if(name == "JupyterHub"){
        try {
          const response = await axios.get('http://127.0.0.1:5000/get-pods/jhub'); 
          // console.log("podss" , response.data.pods[0].name);
          setPods(response.data.pods);
          const areAllPodsRunning = response.data.pods.every(pod => pod.status === "Running");
          setAllPodsRunning(areAllPodsRunning);
        } catch (error) {
          console.error('Error fetching pods:', error);
        }
      }
    };

    fetchStatus();
    getPods();
  }, []);

  useEffect(() => {
    // Check if all pods are running when pods state changes
    if (pods.length > 0) {
      const areAllPodsRunning = pods.every(pod => pod.status === "Running");
      setAllPodsRunning(areAllPodsRunning);
    }
  }, [pods]);

  const startTool = async () => {
    try {
      // Send API call to backend to start the tool
      const response = await axios.get('http://127.0.0.1:5000/get-node-port/jhub', {
        // Add any data needed for starting the tool
      });

      console.log(response.data.node_port);
      
      // Handle the response to open the new page
      const port = response.data.node_port; // Assuming the response contains the port
      window.open(`http://192.168.56.10:${port}`);
    } catch (error) {
      console.error('Error starting tool:', error);
    }
  };

 
  
  return (
    <div className="flex h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />.
      <div className='w-full  text-[#132577] px-[8%] flex-1 flex items-center justify-start '>
        <div className='flex flex-1 items-center justify-start'>
          <img src="/ClsuterIcon.svg" className="flex w-28 md:block" />
          <div className='flex-2 h-auto '>
            <h1 className="text-lg md:text-xl font-semibold"> {name}</h1>
          </div>
          
        </div>
        
        <div className='flex h-full flex-2 items-center justify-start '>
          <button
            type="button"
            className="w-auto hover:bg-[#33469e] w-full font-bold bg-[#132577] rounded mt-4 text-white p-4 px-6"
            onMouseEnter={(e) => { e.target.style.cursor = 'pointer'; }} // Show hand cursor on hover
            onMouseLeave={(e) => { e.target.style.cursor = 'auto'; }}
            disabled={!allPodsRunning}
            onClick={startTool} 
          >
            Start {name}
          </button>
          
        </div>
          
      </div>

      <div className='flex h-[60%] w-[80%] m-14 gap-16'>
        <div className='flex flex-col p-10 items-center text-center h-full w-full rounded-2xl bg-[#132577] text-white'>
          <h className="text-2xl font-bold"> Status of Tool</h>
          <div className=' pt-6 px-4 overflow-hidden text-xs text-start'>
            {status}
          </div>
          
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
