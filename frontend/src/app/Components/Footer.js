import React, { useState } from 'react';

const Footer = () => {

    const services = ["Web Hosting","Domains","Premium Hosting", "Private Server", "E-mail Hosting"];
    const followUs = ["Facebook","Twitter","Instagram", "Linkedin", "Discord"];

  return (
    <div className='bg-[#132577] text-xs gap-[5%] flex items-center justify-center w-full h-[20rem] fixed bottom-0 p-10 my-4'>
        <div className='flex-1 text-start flex h-auto'>
         Digital experience is always embedded in a physical experience.Turpis cursus in hac habitasse platea dictumst quisque sagittis purus. Ligula ullamcorper malesuada proin libero nunc consequat.Turpis cursus in hac habitasse platea dictumst quisque sagittis purus. Ligula ullamcorper malesuada proin libero nunc consequat.
        </div>
        <div className='flex-2 flex flex-col w-1/6 h-auto'> 
            <div className='text-sm font-semibold'>Services</div>
            <div className='mt-10 flex h-auto'>
                <ol className='flex-1 flex flex-col h-full w-full'>
                {services.map((service,index) => (
                    <li key={index} className='mt-2'>{service}</li>
                ))}
                </ol>
            </div>
            
        </div>
        <div className='flex-3 flex flex-col w-1/6 h-auto'> 
            <div className='text-sm font-semibold'>Follow Us</div>
            <div className='mt-10 flex h-auto'>
                <ol className='flex-1 flex flex-col h-full w-full'>
                {followUs.map((follow,index) => (
                    <li key={index} className='mt-2'>{follow}</li>
                ))}
                </ol>
            </div>
            
        </div>
        <div className='flex-4 flex flex-col w-1/6 h-auto'>
        <div className='text-sm font-semibold'>Contact Us</div>
            <div className='mt-10 flex h-auto'>
                <ol className='flex-1 flex flex-col h-full w-full'>
                {followUs.map((follow,index) => (
                    <li key={index} className='mt-2'>{follow}</li>
                ))}
                </ol>
            </div>
        </div>
    </div>
  );
};

export default Footer;
