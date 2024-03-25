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

const Tool = ({ tool, onDrop }) => {
  const [, drag] = useDrag({
    type: ItemTypes.TOOL,
    item: { tool },
  });

  return (
    <div  className="flex items-center" ref={drag} style={{ cursor: 'move', marginBottom: '10px' }}>
      <img src={tool.logo} alt={tool.tool_name} className="w-10 h-10 mr-2 rounded-full" />
      {tool.tool_name}
    </div>
  );
};

const DroppedTool = ({ tool, onDrop }) => {
  const [, drag] = useDrag({
    type: ItemTypes.TOOL,
    item: { tool },
  });

  return (
    <div className="flex items-center" ref={drag} style={{ cursor: 'move', marginBottom: '10px' }}>
      <img src={tool.logo} alt={tool.tool_name} className="w-10 h-10 mr-2 rounded-full" />
      {tool.tool_name}
    </div>
  );
};

const ClusterSpace = ({ droppedTools, onDrop }) => {
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: ItemTypes.TOOL,
    drop: (item) => onDrop(item.tool),
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
        <DroppedTool key={index} tool={tool} onDrop={onDrop} />
      ))}
    </div>
  );
};

const DragAndDropPage = () => {
  const [tools, setTools] = useState([]);
  const [droppedTools, setDroppedTools] = useState([]);
  const [installationStatus, setInstallationStatus] = useState('');
  
  useEffect(() => {
    fetchDataFromAPI();
  }, []);

  const fetchDataFromAPI = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/tools'); 
      const filteredTools = response.data.filter(tool => tool.installed === "false"); // assuming 'installed' is a boolean
      setTools(filteredTools);
    } catch (error) {
      console.error('Error fetching data: ', error);
    }
  };
  
  const handleDrop = async (tool) => {
    if (droppedTools.some((droppedTool) => droppedTool.tool_name === tool.tool_name)) {
      // Tool already dropped
      return;
    }
    setTools((prevTools) => prevTools.filter((prevTool) => prevTool.tool_name !== tool.tool_name));
    setDroppedTools((prevTools) => [...prevTools, tool]);
  };

  const deployTools = async () => {
    try {
      await Promise.all(droppedTools.map(async (tool) => {
        try {
          const response = await axios.get(`http://127.0.0.1:5000/installtool/${tool.tool_name}`);
          swal.fire({ text: response.data.message });
        } catch (error) {
          swal.fire({ text: error.message });
        }
      }));
    } catch (error) {
      swal.fire({ text: error.message });
    }
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure"  />
      <div className='flex h-full flex-col gap-[5%] px-[5%] py-[2%] w-full text-black'>
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
              onClick={deployTools}
            >
              Deploy Tool
            </button>
          </div>
        </div>
        <div>{installationStatus}</div>
        <DndProvider className="flex-2 h-full flex w-screen" backend={HTML5Backend}>
          <div className='flex h-[600px] gap-[5%]'>
            <div className='border h-full flex-1 w-[30%] border-gray-400 rounded bg-gray-100 py-[2%] px-[2%] '>
              <h1 className="text-lg md:text-xl font-semibold">Tool List</h1>
              <ul className='mt-4 text-sm'>
                {tools.map((tool, index) => (
                  <li key={index}>
                    <Tool tool={tool} onDrop={handleDrop} />
                  </li>
                ))}
              </ul>
            </div>
            <ClusterSpace className="flex flex-2 w-2/3" droppedTools={droppedTools} onDrop={handleDrop} />
          </div>
        </DndProvider>
      </div>
      <Footer />
    </div>
  );
};

export default DragAndDropPage;
