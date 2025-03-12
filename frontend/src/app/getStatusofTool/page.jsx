"use client";
import React, { useState, useEffect, Suspense } from 'react';
import axios from 'axios';
import { useSearchParams } from "next/navigation";
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';
import Link from 'next/link';
import API_BASE_URL from '../URL';

const FetchSearchParams = ({ setName, setIds }) => {
  const searchParams = useSearchParams();
  const name = searchParams.get("name");
  const id = searchParams.get("id");

  useEffect(() => {
    setName(name);
    setIds(id);
  }, [name, id, setName, setIds]);

  return null; // This component does not render any visible UI
};

const GetStatus = () => {
  const [status, setStat] = useState([]);
  const [pods, setPods] = useState([]);
  const [name, setName] = useState(null);
  const [ids, setIds] = useState(null);
  const [allPodsRunning, setAllPodsRunning] = useState(false);

  useEffect(() => {
    if (name) {
      const fetchStatus = async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/get-status/${name}`);
          setStat(response.data.status);
        } catch (error) {
          console.error('Error fetching status:', error);
        }
      };

      const getPods = async () => {
        try {
          let response;
          if (name === "JupyterHub") {
            response = await axios.get(`${API_BASE_URL}/get-pods/jhub`);
          } else if (name === "BinderHub") {
            response = await axios.get(`${API_BASE_URL}/get-pods/bhub`);
          } else if (name === "Prometheus") {
            response = await axios.get(`${API_BASE_URL}/get-pods/prom`);
          } else if (name === "Grafana") {
            response = await axios.get(`${API_BASE_URL}/get-pods/graf`);
          } else if (name === "MariaDB") {
            response = await axios.get(`${API_BASE_URL}/get-pods/mariadb`);
          } else if (name === "Wordpress") {
            response = await axios.get(`${API_BASE_URL}/get-pods/wordpress`);
          } else if (name === "Apache") {
            response = await axios.get(`${API_BASE_URL}/get-pods/apache`);
          } else if (name === "RabbitMQ") {
            response = await axios.get(`${API_BASE_URL}/get-pods/rabbitmq`);
          } else if (name === "ArgoCD") {
            response = await axios.get(`${API_BASE_URL}/get-pods/argocd`);
          } else if (name === "Jenkins") {
            response = await axios.get(`${API_BASE_URL}/get-pods/jenkins`);
          } else if (name === "Zipkin") {
            response = await axios.get(`${API_BASE_URL}/get-pods/zipkin`);
          } 
          else {
            console.error('Unsupported tool name:', name);
            return;
          }

          if (response && response.data) {
            setPods(response.data);
            const allRunning = response.data.every(pod => pod.status === "Running");
            setAllPodsRunning(allRunning);
          } else {
            console.error('Error: Pod data not available in API response');
          }
        } catch (error) {
          console.error('Error fetching pods:', error);
        }
      };

      fetchStatus();
      getPods();
    }
  }, [name]);

  const startTool = async () => {
    try {
      let endpoint;
      if (name === "JupyterHub") {
        endpoint = `${API_BASE_URL}/get-node-port/jhub`;
      } else if (name === "BinderHub") {
        endpoint = `${API_BASE_URL}/get-service-port/bhub/binder`;
      } else if (name === "Prometheus") {
        endpoint = `${API_BASE_URL}/get-service-port/prom/prometheus-server-ext`;
      } else if (name === "Grafana") {
        endpoint = `${API_BASE_URL}/get-service-port/graf/grafana-ext`;
      } else if (name === "MariaDB") {
        endpoint = `${API_BASE_URL}/get-service-port/mariadb/mariadb`;
      } else if (name === "Wordpress") {
        endpoint = `${API_BASE_URL}/get-service-port/wordpress/wordpress`;
      } else if (name === "Apache") {
        endpoint = `${API_BASE_URL}/get-service-port/apache/apache`;
      } else if (name === "RabbitMQ") {
        endpoint = `${API_BASE_URL}/get-service-port/rabbitmq/rabbitmq`;
      } else if (name === "ArgoCD") {
        endpoint = `${API_BASE_URL}/get-service-port/argocd/argocd-argo-cd-server`;
      } else if (name === "Jenkins") {
        endpoint = `${API_BASE_URL}/get-service-port/jenkins/jenkins`;
      } else if (name === "Milvus") {
        endpoint = `${API_BASE_URL}/get-service-port/milvus/milvus`;
      } else if (name === "Zipkin") {
        endpoint = `${API_BASE_URL}/get-service-port/zipkin/zipkin`;
      }
      else {
        console.error('Unsupported tool name:', name);
        return;
      }

      const response = await axios.get(endpoint);
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
      <Suspense fallback={<div>Loading...</div>}>
        <FetchSearchParams setName={setName} setIds={setIds} />
      </Suspense>

      <div className='w-full text-[#132577] px-[8%] flex-1 flex items-center justify-start'>
        <div className='flex flex-1 items-center justify-start'>
          <img src="/ClsuterIcon.svg" className="flex w-28 md:block" alt="Cluster Icon" />
          <div className='flex-2 h-auto'>
            <h1 className="text-lg md:text-xl font-semibold">{name}</h1>
          </div>
        </div>
        
        <div className='flex w-[30%] h-full flex-2 items-center gap-4'>
          <button
            type="button"
            className="hover:bg-[#33469e] flex text-center font-bold bg-[#132577] rounded mt-4 text-white p-4 px-6"
            disabled={!allPodsRunning}
            onClick={startTool}
          >
            Start {name}
          </button>

          <Link href={{
            pathname: '/toolQueue',
            query: { name: name, id: ids },
          }}>
            <button
              type="button"
              className="hover:bg-[#33469e] flex w-full font-bold bg-[#132577] rounded mt-4 text-white p-4 px-6"
            >
              View Queue
            </button>
          </Link>
        </div>
      </div>

      <div className='flex h-full w-[80%] m-14 gap-16'>
        <div className='flex flex-col p-10 items-center text-center h-full w-full rounded-2xl bg-[#132577] text-white'>
          <h1 className="text-2xl font-bold">Status of Tool</h1>
          <div className='pt-6 px-4 overflow-hidden text-xs text-start'>
            {status}
          </div>
        </div>
        <div className='p-10 items-center text-center h-full w-full rounded-2xl bg-[#132577] text-white'>
          <h1 className="text-2xl font-bold">Pods of Tool</h1>
          {pods.map((pod, index) => (
            <div key={index} className='text-start pt-6 px-4'>
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

export default GetStatus;
