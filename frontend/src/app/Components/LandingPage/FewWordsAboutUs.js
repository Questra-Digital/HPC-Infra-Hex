import React from 'react';

const FewWordsAboutUs = () => {
  return (
    <div className='text-black flex  gap-20 md:flex-row items-center justify-between  h-auto px-10 w-full py-4'>
    
        <div className="flex-1 flex flex-col h-auto w-full md:1/2 p-12 ">
            <div className='text-lg text-[#132577] font-medium'>
            Few Words About Us
            </div>
            <div className='text-2xl font-bold mt-2'>
            We Are Leaders in It 
            </div>
            <div className='text-2xl font-bold'>
            Solutions
            </div>
            <div className='text-xs font-normal mt-4'>
            Aliquam a diam gravida, pretium justo non, facilisis eros. Integer posuere semper condimentum. Praesent tortor dui, auctor a condimentum vitae, aliquam at quam. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse consequat lacus a sapien pretium, sit amet finibus ex.
            </div>
            <div className='flex text-xs font-semibold w-full mt-4 flex-row items-center'>
            <ul className='flex-1 flex gap-[5%] w-full'>
                <li className='list-circle'>Quisque metus felis in dictum</li>
                <li className='list-circle'>Mauris sollicitudin nunc quis at</li>
            </ul>
            
            </div>
           
        </div>

        {/* Big SVG on the right side */}
        <img src="/fewaboutus.png" className="flex-2 w-full hidden md:block md:w-[35%]" />

    </div>
    
  );
};

export default FewWordsAboutUs;
