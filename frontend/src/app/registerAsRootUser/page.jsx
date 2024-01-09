"use client"
import React, { useState } from 'react';
import Footer from '../Components/Footer';
import MainNavbar from '../Components/Shared/MainNavbar';

const RegisterAsRootUser = () => {
    const pages = [
        { title: 'Home', link: '/' },
        { title: 'About Us', link: '/about' },
        { title: 'Portfolio', link: '/portfolio' },
        { title: 'Expertise', link: '/expertise' },
        { title: 'Clients', link: '/clients' },
        { title: 'Services', link: '/services' },
        { title: 'Contact', link: '/contact' },
      ];    

  return (
    <div className="h-screen flex flex-col gap-[10%] items-center  text-white w-screen">
        <div className='flex-1 w-full h-auto  flex flex-col text-white bg-[#132577]'>
            <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure" pages={pages}/>
            <div className='p-10 py-5 flex-2  w-full text-center flex items-center justify-center'>
                <div className='flex-1 text-lg font-bold'>Register as a root user of  an organization</div>
            </div>
            <div className='flex w-full flex-col px-[15%] items-center justify-center'>
                
                <div className='flex text-xs flex-col w-full py-4 px-[5%] items-center justify-center border border-gray-200 rounded'>
                    <div className='text-lg my-2 font-bold' >Personal Information</div>
                    <div className="mt-6 flex-1 gap-[3%] flex w-full">
                        <div className="flex-1 w-1/3 mb-0">
                            <label className="block font-semibold mb-2">Name:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-2 w-1/3 mb-4">
                            <label className="block font-semibold mb-2">Email:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-1 w-1/3 mb-4">
                            <label className="block font-semibold mb-2">Password:</label>
                            <input type="password" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                    </div>
                    <div className="mt-4 flex-2 flex w-full">
                        <div className="flex-2 w-1/3 mb-4">
                            <label className="block font-semibold mb-2">Contact:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        
                    </div>
            
                </div>

                <div className='flex text-xs flex-col w-full mx-[15%] py-4 px-[5%] my-[8%] items-center justify-center border border-gray-200 rounded'>
                    <div className='text-lg my-5 font-bold' >Organizational Information</div>
                    <div className="mt-6 flex-1 gap-[5%] flex w-full">
                        <div className="flex-1 w-1/3 mb-4">
                            <label className="block font-semibold mb-2">Name of Organization:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-2 w-1/3 mb-4">
                            <label className="block font-semibold mb-2">Type of Organization:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-1 w-1/3 mb-4">
                            <label className="block  font-semibold mb-2">Date of Establishment:</label>
                            <input type="date" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                    </div>
                    <div className="mt-4 flex-1 gap-[5%] flex w-full">
                        <div className="flex-1 w-1/4 mb-4">
                            <label className="block font-semibold mb-2">Sector:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-2 w-1/4 mb-4">
                            <label className="block  font-semibold mb-2">City:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-1 w-1/4 mb-4">
                            <label className="block  font-semibold mb-2">Postal Code:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                        <div className="flex-2 w-1/4 mb-4">
                            <label className="block font-semibold mb-2">State:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                    </div>
                    <div className="mt-4 flex-1 gap-[5%] flex w-full">
                        <div className="flex-1 w-1/3 mb-4">
                            <label className="block  font-semibold mb-2">Address:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                       
                        <div className="flex-1 w-1/3 mb-4">
                            <label className="block  font-semibold mb-2">Contact:</label>
                            <input type="text" className="text-black w-full px-4 py-2 rounded border border-white" />
                        </div>
                    </div>
            
                </div>

                <div className="w-full items-center text-center py-[8%]">
                    <button className="w-full bg-white font-bold text-[#132577] px-4 py-3 rounded">Register</button>
                </div>
                
            </div>
        </div>

        <Footer className="flex-7"/>
    </div>
   
  );
};

export default RegisterAsRootUser;
