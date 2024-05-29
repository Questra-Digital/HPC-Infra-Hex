// app/login.js
"use client"
import React from 'react';
import MainNavbar from '../Components/Shared/MainNavbar';

const Login = () => {
  return (
    <div className="bg-[#132577] h-screen flex flex-col items-center text-white">
      <MainNavbar className="w-full flex-1" title="HPC MLOPs Infrastructure" />
      <div className="h-full flex flex-col gap-20 md:flex-row items-center justify-center w-full md:py-4 md:px-24 lg:px-32">
        <form className="flex-1 w-full md:w-1/2 p-12 md:px-0 mb-4 md:mb-0 md:mr-4">
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Username:</label>
            <input type="text" className="w-full px-4 py-2 rounded border border-white" />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Password:</label>
            <input type="password" className="w-full px-4 py-2 rounded border border-white" />
          </div>
          <div className="mt-8">
            <button className="w-full bg-white font-bold text-[#132577] px-4 py-3 rounded">Login</button>
          </div>
          
        </form>

        {/* Big SVG on the right side */}
        <img src="/service icon.svg" className="flex-2 w-full hidden md:block md:w-1/3" />
      </div>
    </div>
  );
};

export default Login;
