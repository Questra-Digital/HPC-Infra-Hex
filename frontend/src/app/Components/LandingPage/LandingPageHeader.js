import React from 'react';

const LandingPageHeader = ({ title, pages }) => {
  return (
    <div className="bg-[#132577] flex flex-col items-center h-auto px-10 w-full py-4">

        {/* Header Body */}
        <div className='flex flex-2 h-auto flex-col gap-20 md:flex-row items-center justify-between w-full '>
       
            <div className="flex-1 flex flex-col h-auto w-full md:1/2 p-12 md:px-24">
                <div className='flex flex-1 text-2xl font-bold'>
                Software solution providers that help brands thrive and stand out
                </div>
                <div className='flex flex-2 text-sm font-normal mt-4'>
                Since 2014, we have been exploring the world of design and development offering our expertise in web and mobile. It is perfect fusion of innovation, development and execution at one place.
                </div>
                <button type="button" className="w-1/3 font-bold bg-white rounded mt-4 text-[#132577] p-3">
                Explore More
                </button>
            </div>

            {/* Big SVG on the right side */}
            <img src="/service icon.svg" className="flex-2 w-full hidden md:block md:w-[30%]" />
    
        </div>
    
    </div>
  );
};

export default LandingPageHeader;
