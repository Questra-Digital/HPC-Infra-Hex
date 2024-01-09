// app/login.js
import React from 'react';

const Navbar = ({title}) => {
  return (
      <div className="bg-[#132577] flex items-center h-auto justify-center w-full ">
        <div className='flex-1 h-auto w-1/3 flex ml-[10%]'>
            <img src="/logo.svg"  className="h-24" />
        </div>
        <div className='flex-2 h-auto w-2/3 '>
            <h1 className="text-xl md:text-2xl font-semibold">{title}</h1>
        </div>      
      </div>
  );
};

export default Navbar;
