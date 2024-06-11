"use client";
import React, { useEffect, useState } from 'react';

const LoginNavbar = ({ title }) => {


  return (
    <div className="bg-[#132577] flex flex-col items-center h-auto px-20 w-full py-4">
      <div className='flex flex-1 items-center justify-between w-full'>
        <div className="flex items-center justify-center">
          <img src="/logo.svg" className="h-24" alt="Logo" />
          <a href='/landingPage' className="text-xl md:text-2xl font-semibold ml-4">{title}</a>
        </div>
        
      </div>
    </div>
  );
};

export default LoginNavbar;
