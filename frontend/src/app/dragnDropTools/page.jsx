"use client"
import React, { useState, useEffect } from 'react';
import swal from 'sweetalert2';
import axios from 'axios';
import { useDrag, DndProvider, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';

const ItemTypes = {
  TOOL: 'tool',
};

const Tool = ({ name, onDrop }) => {
  const [, drag] = useDrag({
    type: ItemTypes.TOOL,
    item: { name },
  });

  return (
    <div ref={drag} style={{ cursor: 'move', marginBottom: '10px' }}>
      {name}
    </div>
  );
};

const DroppedTool = ({ name, onDrop }) => {
  const [, drag] = useDrag({
    type: ItemTypes.TOOL,
    item: { name },
  });

  return (
    <div ref={drag} style={{ cursor: 'move', marginBottom: '10px' }}>
      {name}
    </div>
  );
};

const ClusterSpace = ({ droppedTools, onDrop }) => {
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: ItemTypes.TOOL,
    drop: (item) => onDrop(item.name),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  });

  const isActive = isOver && canDrop;

  return (
    <div
      ref={drop}
      className='w-[75%] rounded p-[2%] min-h-60'
      style={{
        border: '2px dashed #000',
        backgroundImage: 'url("Dots.svg")',
        backgroundColor: isActive ? '#F3F3F3' : 'white',
      }}
    >
      {droppedTools.map((tool, index) => (
        <DroppedTool key={index} name={tool} onDrop={onDrop} />
      ))}
    </div>
  );
};

const DragAndDropPage = () => {
  const [tools, setTools] = useState([]);
  const [droppedTools, setDroppedTools] = useState([]);
  const [installationStatus, setInstallationStatus] = useState('');
  
  
  // Function to handle script file upload
  const handleScriptFileUpload = (e) => {
    const selectedFile = e.target.files[0]; // Get the selected file
    setScriptFile(selectedFile); // Update the state with the selected file
  };

  const fetchDataFromAPI = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/tools'); 
      const filteredTools = response.data.filter(tool => tool.installed == "false");
      const toolNames = filteredTools.map(tool => tool.tool_name);
  
      setTools(toolNames);
  
    } catch (error) {
      console.error('Error fetching data: ', error);
    }
  };
  
  // Call the fetchDataFromAPI function whenever you need to fetch the data
  useEffect(() => {
    fetchDataFromAPI();
  }, []);
  

  const handleDrop = async (toolName) => {
    console.log(toolName)
    if(toolName == "JupyterHub"){
      console.log(1)
      try {
        const response = await axios.get('http://127.0.0.1:5000/create-jupyterhub'); 
        swal.fire({text:response.data.message});
        // console.log(response.data.message)
    
      } catch (error) {
        swal.fire({text:error});
      }

    }
    if (droppedTools.includes(toolName)) {
      // Tool already dropped
      return;
    }
    // Update dropped tools
    setTools((prevTools) => prevTools.filter((tool) => tool !== toolName));
    setDroppedTools((prevTools) => [...prevTools, toolName]);
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure"  />
      <div className='flex  h-full flex-col gap-[5%] px-[5%] py-[2%] w-full text-black'>
        <div className='flex-1 flex items-center justify-start '>
          <div className='flex flex-1 items-center justify-start'>
            <img src="/ClsuterIcon.svg" className="flex w-28 md:block" />
            <div className='flex-2 h-auto '>
              <h1 className="text-lg md:text-xl font-semibold">Cluster Name</h1>
            </div>
            
          </div>
          
          <div className='flex h-full flex-2 items-center justify-start '>
            <button
              type="button"
              className="w-auto hover:bg-[#33469e] w-full font-bold bg-[#132577] rounded mt-4 text-white p-4 px-6"
              onMouseEnter={(e) => { e.target.style.cursor = 'pointer'; }} // Show hand cursor on hover
              onMouseLeave={(e) => { e.target.style.cursor = 'auto'; }}
            >
              Deploy Tool
            </button>
            
          </div>
          
        </div>
        <div>{installationStatus}</div>
        <DndProvider className="flex-2 h-full flex w-screen" backend={HTML5Backend}>
          <div className='flex h-full gap-[5%]'>
            <div className='border h-full flex-1 w-[30%] border-gray-400 rounded bg-gray-100 py-[2%] px-[2%] '>
              <h1 className="text-lg md:text-xl font-semibold">Tool List</h1>
              <ul className='mt-4 text-sm'>
                {tools.map((tool, index) => (
                  <li key={index}>
                    <Tool name={tool} onDrop={handleDrop} />
                  </li>
                ))}
              </ul>
            </div>
            
            <ClusterSpace className="flex flex-2 w-2/3" droppedTools={droppedTools} onDrop={handleDrop} />
          </div>
          
        </DndProvider>
      </div>
      {/* <Footer /> */}


    </div>
  );
};

export default DragAndDropPage;