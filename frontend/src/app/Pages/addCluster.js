import React, { useState } from 'react';
import Navbar from '../Components/navbar';
import Axios from 'axios';
import { FaTrash } from 'react-icons/fa';

const AddCluster = () => {
  const [boxes, setBoxes] = useState([]);
  const [boxVersion, setBoxVersion] = useState('20230729.0.0');
  const [memory, setMemory] = useState('');
  const [cpus, setCpus] = useState('');
  const [numBoxes, setNumBoxes] = useState(1);

  const handleBoxNameChange = (index, name) => {
    const updatedBoxes = [...boxes];
    updatedBoxes[index].name = name;
    setBoxes(updatedBoxes);
  };

  const handleBoxIpChange = (index, ip) => {
    const updatedBoxes = [...boxes];
    updatedBoxes[index].ip = ip;
    setBoxes(updatedBoxes);
  };

  const handleAddBox = () => {
    setBoxes([...boxes, { name: '', ip: '' }]);
  };

  const handleRemoveBox = (index) => {
    const updatedBoxes = [...boxes];
    updatedBoxes.splice(index, 1);
    setBoxes(updatedBoxes);
  };

  const handleSave = async () => {
    try {
      const payload = {
        nums_vms: numBoxes,
        vm_box: 'ubuntu/jammy64',
        vm_box_version: boxVersion,
        vm_memory: memory,
        vm_Cpu: cpus,
        boxes,
      };

      // Make Axios POST request
      console.log(payload);
      const response = await Axios.post('http://127.0.0.1:5000/generate_vagrantfile', payload);

      // Handle the response if needed
      console.log(response.data); // Log the response data to the console
    } catch (error) {
      console.error('Error making Axios request:', error);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center text-white w-screen">
        <Navbar title={"Add Cluster To Your Resources"} />
        <div className=" overflow-y-auto h-full flex flex-col md:flex-row items-start justify-center w-full ">
            <div className="bg-[#132577] flex gap-[2%] flex-col flex-1  w-2/3 p-[5%] py-[8%] md:py-[3%] my-[10%]  md:my-[3%] mx-[15%] rounded-lg ">
            
                <div className='flex flex-col md:flex-row w-auto gap-[5%] '>
                    <div className="flex mb-4 flex-col flex-1 w-full md:w-1/2">
                        <label className="mb-2">Select Vagrant Box:</label>
                        <select className="p-2 text-black rounded">
                        <option value="ubuntu/jammy64">ubuntu/jammy64</option>
                        </select>
                    </div>

                    <div className="flex mb-4 flex-col flex-2 w-full md:w-1/2">
                        <label className="mb-2">VM Box Version:</label>
                        <input readOnly type="text" value={boxVersion} onChange={(e) => setBoxVersion(e.target.value)} className="rounded text-black p-2" />
                    </div>
                </div>

                <div className='flex flex-col md:flex-row w-auto gap-[5%] '>
                    <div className="flex mb-2 flex-col w-full md:w-1/2">
                        <label className="mb-2">Memory:</label>
                        <input type="text" value={memory} onChange={(e) => setMemory(e.target.value)} className="rounded text-black p-2" />
                    </div>

                    <div className="flex mb-4 flex-col w-auto md:w-1/2">
                        <label className="mb-2">CPUs:</label>
                        <input type="text" value={cpus} onChange={(e) => setCpus(e.target.value)} className="rounded text-black p-2" />
                    </div>
                </div>

                {boxes.map((box, index) => (
                    <div key={index} className="flex flex-col md:flex-row w-auto gap-[5%]">
                        <div className='flex mb-4 flex-col w-full md:w-1/2'>
                            <label className="mb-2">{`VM Box ${index + 1} Name:`}</label>
                            <input
                                type="text"
                                value={box.name}
                                onChange={(e) => handleBoxNameChange(index, e.target.value)}
                                className="rounded p-2 text-black"
                            />
                        </div>

                        <div className='flex mb-4 flex-col w-auto md:w-1/2'>
                            <label className="mb-2">{`VM Box ${index + 1} IP Address:`}</label>
                            <input
                                type="text"
                                value={box.ip}
                                onChange={(e) => handleBoxIpChange(index, e.target.value)}
                                className="rounded text-black p-2"
                            />
                        </div>
                    
                        <button
                            type="button"
                            onClick={() => handleRemoveBox(index)}
                            className="flex mt-2 rounded text-white p-2 flex items-center justify-center"
                        >
                            <FaTrash />
                        </button>
                    </div>
                ))}
                
                <div className='flex flex-col md:flex-row w-auto gap-[5%] '>
                    <button type="button" onClick={handleAddBox} className="w-auto md:w-1/2  rounded font-bold mt-4 bg-[#15E89C] text-white p-2">
                        Add Box
                    </button>

                    <button type="button" onClick={handleSave} className="w-auto md:w-1/2 font-bold rounded mt-4 bg-white text-[#132577] p-2">
                        Save
                    </button>
                </div>
            
            </div>
        </div>
    </div>
  );
};

export default AddCluster;
