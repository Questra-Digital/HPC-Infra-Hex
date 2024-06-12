"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'next/navigation';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';
import API_BASE_URL from '../URL';
import { FiEdit3 } from 'react-icons/fi'; // Importing an edit icon
import Swal from 'sweetalert2'; // Import SweetAlert

const ToolsQueue = () => {
  const [runningQueue, setRunningQueue] = useState([]);
  const [waitingQueue, setWaitingQueue] = useState([]);
  const [queueLimit, setQueueLimit] = useState(null); // State to store the queue limit
  const [isEditing, setIsEditing] = useState(false); // State to manage edit mode
  const [newQueueLimit, setNewQueueLimit] = useState(null); // State to store the new queue limit input
  const [role, setRole] = useState(null); // State to store user role
  const searchParams = useSearchParams();
  const name = searchParams.get("name");
  const id = searchParams.get("id");
  const [queueKey, setQueueKey] = useState(0);
  useEffect(() => {
    // Retrieve the user role from session storage
    const userRole = sessionStorage.getItem('user_role');
    setRole(userRole);

    const fetchToolIdAndQueues = async () => {
      try {
        // Fetch the tool ID based on the tool name
       
       

        // Fetch the queue limit using the tool ID
        const queueLimitResponse = await axios.get(`${API_BASE_URL}/get-queue-limit/${id}`);
        setQueueLimit(queueLimitResponse.data.queue_limit);
        setNewQueueLimit(queueLimitResponse.data.queue_limit); // Set the newQueueLimit to the initial queueLimit

        // Fetch the running queue using the tool ID
        const runningQueueResponse = await axios.post(`${API_BASE_URL}/queue`, { tool_id: id });
        console.log("runningQueueResponse", runningQueueResponse.data.queue);
        setRunningQueue(runningQueueResponse.data.queue);

        // Fetch the waiting queue using the tool ID
        const waitingQueueResponse = await axios.post(`${API_BASE_URL}/waiting-list`, { tool_id: id });
        setWaitingQueue(waitingQueueResponse.data.waiting_list);
      } catch (error) {
        console.error('Error fetching tool ID or queues:', error);
      }
    };

    fetchToolIdAndQueues();
  }, [name,queueKey]);

  const handleQueueLimitChange = (e) => {
    setNewQueueLimit(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      updateQueueLimit();
    }
  };

  const updateQueueLimit = async () => {
    try {
      
      const toolId = id;

      await axios.post(`${API_BASE_URL}/set-queue-limit`, {
        tool_id: toolId,
        queue_limit: newQueueLimit
      });
      setQueueLimit(newQueueLimit);
      setIsEditing(false);
      // Show success message
      Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: 'Queue limit updated successfully!',
      });
    } catch (error) {
      console.error('Error updating queue limit:', error);
      // Show error message
      Swal.fire({
        icon: 'error',
        title: 'Error!',
        text: 'Failed to update queue limit.',
      });
    }
  };

  const handleBlur = async () => {
    // if (newQueueLimit !== queueLimit) {
    //   updateQueueLimit();
    // } else {
      setIsEditing(false); // Exit edit mode if no changes were made
    // }
  };



  const handleUseTool = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/add-to-queue`, {
        user_id: sessionStorage.getItem('user_id'),
        tool_id: id,
      });
      // Update running queue based on the response
      setRunningQueue(response.data.Queue || []);
      
      // Update waiting queue based on the response
      setWaitingQueue(response.data.waiting || []);
      setQueueKey(prevKey => prevKey + 1);
      // Show success message
      Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: response.data.user_status ? response.data.user_status.message : 'Added to queue successfully!',
      });
    } catch (error) {
      console.error('Error adding to queue:', error);
      // Show error message
      Swal.fire({
        icon: 'error',
        title: 'Error!',
        text: 'Failed to add to queue.',
      });
    }
  };

  useEffect(() => {
    console.log(waitingQueue)
  },
  [runningQueue]);
  return (
    <div className="flex h-screen flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" />
      <div className='mt-10 flex-1 text-[#132577] text-xl font-bold'>
        Tools Queue - {name}
      </div>
      
      {queueLimit !== null && (
        <div className="flex items-center justify-center bg-[#132577] text-white w-[18%] p-4 my-5 rounded-lg">
          {isEditing ? (
            <div className="flex items-center">
              <span className="text-md font-semibold">Queue Limit:</span>
              <input
                type="number"
                value={newQueueLimit}
                onChange={handleQueueLimitChange}
                onKeyPress={handleKeyPress}
                onBlur={handleBlur}
                className="text-white font-semibold bg-[#132577] w-20 p-2 ml-2 rounded border-none outline-none focus:ring-0"
              />
            </div>
          ) : (
            <div className="flex items-center">
              <span className="text-md font-semibold">Queue Limit: {queueLimit}</span>
              {(role === 'admin' || role === 'root') && (
                <button onClick={() => setIsEditing(true)} className="ml-2">
                  <FiEdit3 className="text-white" />
                </button>
              )}
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-center bg-[#132577] text-white w-[18%] p-4  rounded-lg">
        <button className="text-md font-semibold" onClick={handleUseTool}>
          Use Tool
        </button>
      </div>
      <div className="bg-[#132577] m-[5%] py-[0%] px-[5%] h-[100%] flex flex-col gap-10 md:flex-row items-center w-[80%]">
        <div className='flex flex-col p-10 items-center text-center h-full w-full rounded-2xl bg-white text-[#132577]'>
          <h2 className="text-2xl font-bold">Running Queue</h2>
          <div className='pt-6 px-4 overflow-auto text-xs text-start w-full'>
            {runningQueue.map((user, index) => (
              <div key={index} className='p-2 border-b border-gray-300'>
                <h3 className="text-md font-semibold">{user}</h3>
              </div>
            ))}
          </div>
        </div>
        <div className='flex flex-col p-10 items-center text-center h-full w-full rounded-2xl bg-white text-[#132577]'>
          <h2 className="text-2xl font-bold">Waiting Queue</h2>
          <div className='pt-6 px-4 overflow-auto text-xs text-start w-full'>
            {waitingQueue.map((user, index) => (
              <div key={index} className='p-2 border-b border-gray-300'>
                <h3 className="text-md font-semibold">{user}</h3>
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* <Footer /> */}
    </div>
  );
};

export default ToolsQueue;
