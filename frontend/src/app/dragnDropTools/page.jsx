"use client"
import React, { useState } from 'react';
import Navbar from '../Components/navbar';
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
  
  const [tools, setTools] = useState(['Docker', 'Kubernetes', 'Other Tool']);
  const [droppedTools, setDroppedTools] = useState([]);
  const pages = [
    { title: 'Home', link: '/' },
    { title: 'About Us', link: '/about' },
    { title: 'Portfolio', link: '/portfolio' },
    { title: 'Expertise', link: '/expertise' },
    { title: 'Clients', link: '/clients' },
    { title: 'Services', link: '/services' },
    { title: 'Contact', link: '/contact' },
  ]; 

  const handleDrop = (toolName) => {
    if (droppedTools.includes(toolName)) {
      // setDroppedTools((prevTools) => prevTools.filter((tool) => tool !== toolName));
      // setTools((prevTools) => [...prevTools, toolName]);
    } else {
      setTools((prevTools) => prevTools.filter((tool) => tool !== toolName));
      setDroppedTools((prevTools) => [...prevTools, toolName]);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" pages={pages} />
      <div className='flex  flex-col gap-[5%] px-[5%] py-[2%] w-full text-black'>
       
        <div className='flex-1 flex items-center justify-start '>
          <div className='flex flex-1 items-center justify-start'>
            <img src="/ClsuterIcon.svg" className="flex w-28 md:block" />
            <div className='flex-2 h-auto '>
              <h1 className="text-lg md:text-xl font-semibold">Cluster Name</h1>
            </div> 
          </div>
          <div className='flex flex-2 items-center justify-start '>
            <button type="button" className="w-auto w-full font-bold bg-[#132577] rounded mt-4 text-white p-3">
                Deploy Tools
            </button>
          </div>
            
        </div>

        <DndProvider className="flex-2 flex w-screen" backend={HTML5Backend}>
          <div className='flex gap-[5%]'>
            <div className='border flex-1 w-[30%] border-gray-400 rounded bg-gray-100 py-[2%] px-[2%] '>
              <h1 className="text-lg md:text-xl font-semibold">Tool List</h1>
              <ul className='mt-4 text-sm'>
              {tools.map((tool, index) => (
                <li>
                  <Tool key={index} name={tool} onDrop={handleDrop} />
                </li>
              ))}
              </ul>
              
            </div>
            <ClusterSpace className="flex flex-2 w-2/3" droppedTools={droppedTools} onDrop={handleDrop} />
          </div>
      </DndProvider>
      </div>
     <Footer/>
    </div>
   
  );
};

export default DragAndDropPage;
