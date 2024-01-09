import React, { useState } from 'react';
import { FaFacebook, FaTwitter,FaLinkedin  } from "react-icons/fa";

const ServiceBox = ({ id, image,name, designation, learnMoreLink, onClick, isSelected }) => {
  return (
    <div
      onClick={() => onClick(id)}
      className={`flex flex-col gap-[5%] items-center text-start justify-center h-auto pb-5 w-[22%]  border border-gray-200 rounded-md shadow-md 
        ${isSelected ? 'bg-[#132577] text-white' : 'bg-white text-black'}`}
    >
      <img src={image} className="flex-1 h-auto w-full" />
      <div className='flex-2 p-4 text-center'>
        <div className='text-lg flex-1 font-bold'>{name}</div>
        <div className='text-xs flex-2 font-normal'>{designation}</div>
      </div>

      <div className='mt-4 flex-3 flex w-full items-center justify-center gap-[8%]'>
      <FaFacebook />
      <FaTwitter/>
      <FaLinkedin/>
      </div>
     
      
    </div>
  );
};

const CerifiedExperts = ({ title, pages }) => {
  const [selectedService, setSelectedService] = useState(0);

  const services = [
    {
      id: 0,
      image: 'E1.png',
      name: 'Sebastion Doe',
      designation: 'Software Engineer',
    },
    {
      id: 1,
      image: 'E2.png',
      name: 'Sebastion Doe',
      designation: 'Software Engineer',
    },
    {
      id: 2,
      image: 'E3.png',
      name: 'Sebastion Doe',
      designation: 'Software Engineer',
    },
  
  ];

  const handleServiceClick = (id) => {
    setSelectedService(id);
  };

  return (
    <div className='flex flex-col items-center justify-center w-full h-auto text-black px-10 my-4'>
      <div className='text-xl text-[#132577] font-medium'>Team</div>
      <div className='text-2xl font-bold mt-5'>Our Certified Experts</div>

      <div className='flex w-full items-center gap-[2%] justify-center flex-wrap mt-8'>
        {services.map((service) => (
          <ServiceBox
            key={service.id}
            onClick={handleServiceClick}
            isSelected={selectedService === service.id}
            {...service}
          />
        ))}
      </div>
    </div>
  );
};

export default CerifiedExperts;
