import React, { useState } from 'react';

const ServiceBox = ({ id, heading, description, learnMoreLink, onClick, isSelected }) => {
  return (
    <div
      onClick={() => onClick(id)}
      className={`flex flex-col items-start text-start justify-center h-full w-[22%] p-8 m-4  border border-gray-200 rounded-md shadow-md 
        ${isSelected ? 'bg-[#132577] text-white' : 'bg-white text-black'}`}
    >
      <div className='text-lg flex-1 font-bold'>{heading}</div>
      <div className='text-xs flex-2 font-normal'>{description}</div>
      <a href={learnMoreLink} className='text-start flex-3 text-sm flex mt-4 underline'>
        Learn More
      </a>
    </div>
  );
};

const Services = ({ title, pages }) => {
  const [selectedService, setSelectedService] = useState(0);

  const services = [
    {
      id: 0,
      heading: 'Software Development',
      description: 'Posuere morbi leo urna molestie at elementum eu egestas.',
      learnMoreLink: '/service1',
    },
    {
      id: 1,
      heading: 'AI Programmer & Technical',
      description: 'Posuere morbi leo urna molestie at elementum eu egestas.',
      learnMoreLink: '/service2',
    },
    {
      id: 2,
      heading: 'System Application Development',
      description: 'Posuere morbi leo urna molestie at elementum eu egestas.',
      learnMoreLink: '/service2',
    },
    {
      id: 3,
      heading: 'Server and Network Solutions',
      description: 'Posuere morbi leo urna molestie at elementum eu egestas.',
      learnMoreLink: '/service2',
    },
    // Add more service objects for additional services
  ];

  const handleServiceClick = (id) => {
    setSelectedService(id);
  };

  return (
    <div className='flex flex-col items-center justify-center w-full h-auto text-black px-10 my-4'>
      <div className='text-xl text-[#132577] font-medium'>Services</div>
      <div className='text-2xl font-bold mt-5'>We provide All-in-One Solution</div>
      <div className='text-2xl font-bold'>for Every IT job</div>

      <div className='flex flex-wrap mt-8'>
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

export default Services;
