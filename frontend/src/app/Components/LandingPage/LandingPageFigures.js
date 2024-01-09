import React, { useState } from 'react';

const ServiceBox = ({ id, number, description, learnMoreLink, onClick, isSelected }) => {
  return (
    <div
      onClick={() => onClick(id)}
      className={`flex gap-[0%] flex-col items-center text-start justify-center h-full w-[22%] p-4 m-4  border border-gray-200 rounded-md shadow-md 
        ${isSelected ? 'bg-[#132577] text-white' : 'bg-white text-black'}`}
    >
      <div className='text-xl flex-1 font-bold'>{number}</div>
      <div className='text-sm flex-2 font-normal'>{description}</div>
    </div>
  );
};

const LandingPageFigures = ({ title, pages }) => {
  const [selectedService, setSelectedService] = useState(0);

  const figures = [
    {
      id: 0,
      number: '783',
      description: 'WorldWide Customers',
    },
    {
      id: 1,
      number: '102',
      description: 'Products Done',
    },
    {
      id: 2,
      number: '242',
      description: 'IT Products',
    },
    {
      id: 3,
      number: '508',
      description: 'Projects Spend',
    },
   
  ];
  const handleServiceClick = (id) => {
    setSelectedService(id);
  };

  return (
    <div className='flex flex-row items-center justify-center w-full h-auto text-black px-10'>
      <div className='w-full flex '>
        {figures.map((figure) => (
          <ServiceBox
            key={figure.id}
            onClick={handleServiceClick}
            isSelected={selectedService === figure.id}
            {...figure}
          />
        ))}
      </div>
    </div>
  );
};

export default LandingPageFigures;;
