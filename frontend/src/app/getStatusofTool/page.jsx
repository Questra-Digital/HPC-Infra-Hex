"use client"
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from "next/navigation";
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';
import Link from 'next/link';
import API_BASE_URL from '../URL';

const getStatus = () => {
  const [status, setStat] = useState([]);
  const [pods, setPods] = useState([]);
  const searchParams = useSearchParams();
  const name = searchParams.get("name");
  const [allPodsRunning, setAllPodsRunning] = useState(false); // State to track if all pods are running
  
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/get-status/${name}`); 
        console.log("status", response.data.status);
        setStat(response.data.status);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    const getPods = async () => {
      if (name === "JupyterHub" || name === "BinderHub" || name === "Prometheus" || name === "Grafana") {
        try {
          let response;
          if (name === "JupyterHub") {
            response = await axios.get(`${API_BASE_URL}/get-pods/jhub`);
          } else if (name === "BinderHub") {
            response = await axios.get(`${API_BASE_URL}/get-pods/bhub`);
          }
          else if (name === "Prometheus") {
            response = await axios.get(`${API_BASE_URL}/get-pods/prom`);
          }
          else if (name === "Grafana") {
            response = await axios.get(`${API_BASE_URL}/get-pods/graf`);
          }
          
          if (response && response.data) { // Ensure response and response.data exist
            console.log("response: ", response.data);
            setPods(response.data);
            
            // Check if all pods are running
            let allRunning = true;
            for (const pod of response.data) { // Iterate over response.data
              if (pod.status !== "Running") {
                allRunning = false;
                break;
              }
            }
            setAllPodsRunning(allRunning);
          } else {
            console.error('Error: Pod data not available in API response');
          }
        } catch (error) {
          console.error('Error fetching pods:', error);
        }
      } else {
        console.error('Unsupported tool name:', name);
      }
    };

    fetchStatus();
    getPods();
  }, []);

  useEffect(() => {
    // Check if all pods are running when pods state changes
    if (pods.length > 0) {
      let allRunning = true;
      for (const pod of pods) {
        if (pod.status !== "Running") {
          allRunning = false;
          break;
        }
      }
      setAllPodsRunning(allRunning);
    } else {
      // If there are no pods, set allPodsRunning to false
      setAllPodsRunning(false);
    }
  }, [pods]);
  
  const startTool = async () => {
    try {
      let response;
      let endpoint;
  
      if (name === "JupyterHub") {
        endpoint = `${API_BASE_URL}/get-node-port/jhub`;
      } else if (name === "BinderHub") {
        endpoint = `${API_BASE_URL}/get-service-port/bhub/binder`;
      } 
      else if (name === "Prometheus") {
        endpoint = `${API_BASE_URL}/get-service-port/prom/prometheus-server-ext`;
      }
      else if (name === "Grafana") {
        endpoint = `${API_BASE_URL}/get-service-port/graf/grafana-ext`;
      }
      else {
        console.error('Unsupported tool name:', name);
        return;
      }
  
      response = await axios.get(endpoint);
  
      if (response && response.data && response.data.node_port) {
        const port = response.data.node_port;
        window.open(`http://192.168.56.10:${port}`);
      } else {
        console.error('Error: Invalid or missing port in API response');
      }
    } catch (error) {
      console.error('Error starting tool:', error);
    }
  };

  return (
    <div className="flex h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />
      <div className='w-full text-[#132577] px-[8%] flex-1 flex items-center justify-start '>
        <div className='flex flex-1 items-center justify-start'>
          <img src="/ClsuterIcon.svg" className="flex w-28 md:block" />
          <div className='flex-2 h-auto '>
            <h1 className="text-lg md:text-xl font-semibold"> {name}</h1>
          </div>
        </div>
        
        <div className='flex w-[30%] h-full flex-2  items-center gap-4 '>
          <button
            type="button"
            className="hover:bg-[#33469e] flex text-center font-bold bg-[#132577] rounded mt-4 text-white p-4 px-6"
            onMouseEnter={(e) => { e.target.style.cursor = 'pointer'; }} // Show hand cursor on hover
            onMouseLeave={(e) => { e.target.style.cursor = 'auto'; }}
            disabled={!allPodsRunning}
            onClick={startTool} 
          >
            Start {name}
          </button>

          <Link href={{
            pathname: '/toolQueue',
            query: { name: name },
          }}>
            <button
              type="button"
              className="hover:bg-[#33469e] flex w-full font-bold bg-[#132577] rounded mt-4 text-white p-4 px-6"
              onMouseEnter={(e) => { e.target.style.cursor = 'pointer'; }} // Show hand cursor on hover
              onMouseLeave={(e) => { e.target.style.cursor = 'auto'; }}
              // disabled={!allPodsRunning}
            >
              View Queue
            </button>
          </Link>
        </div>
      </div>

      <div className='flex h-full w-[80%] m-14 gap-16'>
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
     
      <Footer />
    </div>
  );
};

export default getStatus;
