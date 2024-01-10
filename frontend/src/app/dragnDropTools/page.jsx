"use client"
import React, { useState, useEffect } from 'react';
import Navbar from '../Components/navbar';
import { useDrag, DndProvider, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import Modal from 'react-modal'; // Import react-modal
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
  const [modalIsOpen, setModalIsOpen] = useState(false); // State for modal visibility
  const [toolName, setToolName] = useState(''); // State for tool_name input
  const [scriptId, setScriptId] = useState(''); // State for script_id input
  const [scriptFile, setScriptFile] = useState(null); // State to store the selected script file

  // Function to handle script file upload
  const handleScriptFileUpload = (e) => {
    const selectedFile = e.target.files[0]; // Get the selected file
    setScriptFile(selectedFile); // Update the state with the selected file
  };

  const fetchDataFromAPI = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get-all-playbooks');
      if (response.ok) {
        const data = await response.json();
        if (data.result === 'success') {
          // Extract the tool names from the playbooks data
          const allTools = data.playbooks;
  
          // Split the tools into two arrays based on the is_installed field
          const installedTools = allTools.filter((tool) => tool.is_installed);
          const nonInstalledTools = allTools.filter((tool) => !tool.is_installed);
  
          setTools(nonInstalledTools.map((playbook) => playbook.tool_name));
          setDroppedTools(installedTools.map((playbook) => playbook.tool_name));
        } else {
          console.error('API response: ', data);
        }
      } else {
        console.error('API request failed with status: ', response.status);
      }
    } catch (error) {
      console.error('Error fetching data: ', error);
    }
  };
  
  // Call the fetchDataFromAPI function whenever you need to fetch the data
  useEffect(() => {
    fetchDataFromAPI();
  }, []);
  

  const handleDrop = async (toolName) => {
    if (droppedTools.includes(toolName)) {
      // Tool already dropped
      return;
    }

    // Set installation status
    setInstallationStatus(`Tool installation started for ${toolName}`);

    try {
      // Make the API call to start installation
      const response = await fetch(`http://127.0.0.1:5000/install-playbook/${toolName}`);
      if (response.ok) {
        // Assuming the API responds with a success message
        const data = await response.json();
        if (data.result === 'success') {
          // Installation successful
          setInstallationStatus(`Tool installation completed for ${toolName}`);
        } else {
          // Installation failed
          setInstallationStatus(`Tool installation failed for ${toolName}`);
          console.error('API response: ', data);
        }
      } else {
        // API request failed
        setInstallationStatus(`Tool installation failed for ${toolName}`);
        console.error('API request failed with status: ', response.status);
      }
    } catch (error) {
      // Error during API call
      setInstallationStatus(`Tool installation failed for ${toolName}`);
      console.error('Error during API call: ', error);
    }

    // Update dropped tools
    setTools((prevTools) => prevTools.filter((tool) => tool !== toolName));
    setDroppedTools((prevTools) => [...prevTools, toolName]);
  };

  const openModal = () => {
    // Open the modal
    setModalIsOpen(true);
  };

  const closeModal = () => {
    // Close the modal and clear input values
    setModalIsOpen(false);
    setToolName('');
    setScriptId('');
  };

  const handleUpload = async () => {
    try {
      // Create a FormData object to send the data
      const formData = new FormData();
      formData.append('file', scriptFile); // Add the uploaded file
      formData.append('script_id', scriptId); // Add the scriptId
      formData.append('tool_name', toolName); // Add the toolName
  
      // Send a POST request to the API endpoint
      const response = await fetch('http://127.0.0.1:5000/upload-playbook', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        // Successful upload
        closeModal(); // Close the modal
        fetchDataFromAPI();
        // Optionally, you can perform other actions here, such as updating the tool list
      } else {
        // Handle the API error
        const data = await response.json();
        console.error('API response: ', data);
        // You can display an error message to the user
      }
    } catch (error) {
      console.error('Error during API call: ', error);
      // Handle the error and display an error message to the user
    }
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
      <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure"  />
      <div className='flex  flex-col gap-[5%] px-[5%] py-[2%] w-full text-black'>
        <div className='flex-1 flex items-center justify-start '>
          <div className='flex flex-1 items-center justify-start'>
            <img src="/ClsuterIcon.svg" className="flex w-28 md:block" />
            <div className='flex-2 h-auto '>
              <h1 className="text-lg md:text-xl font-semibold">Cluster Name</h1>
            </div>
            
          </div>
          
          <div className='flex flex-2 items-center justify-start '>
            <button
              type="button"
              className="w-auto w-full font-bold bg-[#132577] rounded mt-4 text-white p-3"
              onClick={openModal}
            >
              Upload Tool Configuration
            </button>
            
          </div>
          
        </div>
        <div>{installationStatus}</div>
        <DndProvider className="flex-2 flex w-screen" backend={HTML5Backend}>
          <div className='flex gap-[5%]'>
            <div className='border flex-1 w-[30%] border-gray-400 rounded bg-gray-100 py-[2%] px-[2%] '>
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
      <Footer />

      {/* Modal for uploading tool configuration */}
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Upload Tool Configuration Modal"
        className="custom-modal"
        overlayClassName="custom-modal-overlay"
      >
        <h2 className="modal-title">Upload Tool Configuration</h2>
        <div className="form-group">
          <label htmlFor="toolName">Tool Name:</label>
          <input
            type="text"
            id="toolName"
            className="form-control"
            value={toolName}
            onChange={(e) => setToolName(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="scriptId">Script ID:</label>
          <input
            type="text"
            id="scriptId"
            className="form-control"
            value={scriptId}
            onChange={(e) => setScriptId(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="scriptFile">Upload Script:</label>
          <input
            type="file"
            id="scriptFile"
            className="form-control"
            accept=".yml"
            onChange={handleScriptFileUpload} // Call the function to handle file upload
          />
        </div>
        <div className="button-group">
          <button className="btn btn-cancel" onClick={closeModal}>
            Cancel
          </button>
          <button className="btn btn-upload" onClick={handleUpload}>
            Upload
          </button>
        </div>
      </Modal>


    </div>
  );
};

export default DragAndDropPage;
