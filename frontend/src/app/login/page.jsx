// app/login.js
"use client"
import React from 'react';
import MainNavbar from '../Components/Shared/MainNavbar';
import axios from 'axios';
import API_BASE_URL from '../URL';
import Link from 'next/link';
import { useRouter } from 'next/navigation';


const User_Login = async (username, password,router) => {
  try {
    // Make a POST request to the login endpoint
    const response = await axios.post(`${API_BASE_URL}/login`, { username, password });
    console.log(JSON.stringify(response.data.role));

    // Check if login was successful
    if (response && response.status === 200) {
      sessionStorage.setItem("user_role", response.data.role);
      sessionStorage.setItem("user_id", response.data.user_id);
      router.push('/landingPage');
     
      if(response.data.role == 'admin'){
        
        
      }else if(response.data.role == 'root'){

      }else{

      }
    } 
    else {
      // Handle failed login
      console.error('Error: Login failed');
    }
  } catch (error) {
    console.error('Error login user:', error);
  }
};


const Login = () => {
  const router = useRouter(); // Initialize useRouter

  const handleSubmit = (event) => {
    event.preventDefault();
    const username = event.target.elements.username.value;
    const password = event.target.elements.password.value;
    User_Login(username, password,router);
  };

  return (
   <div className="bg-[#132577] w-full h-screen flex flex-col items-center text-white">
      {/* <MainNavbar className="w-full flex-1" title="HPC MLOPs Infrastructure" /> */}
      <div className="h-full flex flex-col gap-20 md:flex-row items-center  w-[70%]">
        <form className="flex-1" onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Username:</label>
            <input name="username" type="text" className="w-full p-4 text-black rounded border border-white" />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Password:</label>
            <input name="password" type="password" className="w-full p-4 text-black rounded border border-white" />
          </div>
          <div className="mt-8">
            <button type="submit" className="w-full bg-white font-bold text-[#132577] p-4 rounded">Login</button>
          </div>
        </form>

        {/* Big SVG on the right side */}
        <img src="/service icon.svg" className="flex-2 w-full hidden md:block md:w-1/3" />
      </div>
    </div>
  );
};

export default Login;
