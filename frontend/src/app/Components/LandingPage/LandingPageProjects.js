import React from 'react';
import LandingPage from '../../landingPage/page';

const LandingPageProjects = () => {
  return (
    <div className='text-black flex  gap-10 md:flex-row items-center justify-between  h-auto px-10 w-full'>
    
        <img src="/landingpageProjects.png" className="flex-2 w-full hidden md:block md:w-[40%]" />
        
        <div className="flex-1 flex flex-col h-auto w-full md:1/2 p-12 ">
            <div className='text-lg text-[#132577] font-medium'>
            Projects
            </div>
            <div className='text-2xl font-bold mt-2'>
            Our Amazing Project that 
            </div>
            <div className='text-2xl font-bold'>
            Has been Completed
            </div>
            <div className='text-xs font-normal mt-4'>
            Turpis cursus in hac habitasse platea dictumst quisque sagittis purus. Ligula ullamcorper malesuada proin libero nunc consequat.
            </div>
            <div className='text-xs font-normal mt-4'>
            Dignissim sodales ut eu sem integer vitae justo. Tincidunt tortor aliquam nulla facilisi cras.
            </div>
            <div className='flex text-xs font-semibold w-full mt-4 flex-row items-center'>
            <button type="button" className="text-md w-1/3 font-bold bg-[#132577] rounded mt-4 text-white p-3">
                Recent projects
            </button>
            
            </div>
           
        </div>

    </div>
    
  );
};

export default LandingPageProjects;
