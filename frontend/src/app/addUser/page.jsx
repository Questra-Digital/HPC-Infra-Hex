"use client"
import React, { useState } from 'react';
import MainNavbar from '../Components/Shared/MainNavbar';
import axios from 'axios';
import API_BASE_URL from '../URL';
import Swal from 'sweetalert2'; // Import SweetAlert

const AddUserToOrganization = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    role: 'simple user'
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/add-user`, formData);
      console.log('User added:', response.data);
      Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: 'User Added successfully!',
      });
    } catch (error) {
      console.error('Error adding user:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error!',
        text: 'Failed to add User.',
      });
    }
  };

  return (
    <div className="w-full h-screen flex flex-col items-center text-white">
      <MainNavbar className="w-full flex-1" title="HPC MLOPs Infrastructure" />
      <div className='mt-10 flex-1 text-[#132577] text-xl font-bold'>
        Add Admin or Users to Organization
      </div>
      <div className="bg-[#132577] rounded border m-[2%] py-[3%] px-[5%] h-[100%] flex flex-col gap-20 md:flex-row items-center w-[85%]">
        <form className="flex-1" onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Username:</label>
            <input 
              name="username" 
              type="text" 
              value={formData.username} 
              onChange={handleChange} 
              className="w-full p-4 text-black rounded border border-white" 
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Password:</label>
            <input 
              name="password" 
              type="password" 
              value={formData.password} 
              onChange={handleChange} 
              className="w-full p-4 text-black rounded border border-white" 
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Email:</label>
            <input 
              name="email" 
              type="email" 
              value={formData.email} 
              onChange={handleChange} 
              className="w-full p-4 text-black rounded border border-white" 
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Role:</label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input 
                  type="radio" 
                  name="role" 
                  value="simple user" 
                  checked={formData.role === 'simple user'} 
                  onChange={handleChange} 
                  className="mr-2" 
                />
                Simple User
              </label>
              {
                (sessionStorage.getItem('user_role') === 'root') && (
                <label className="flex items-center">
                <input 
                  type="radio" 
                  name="role" 
                  value="admin" 
                  checked={formData.role === 'admin'} 
                  onChange={handleChange} 
                  className="mr-2" 
                />
                Admin
              </label>
              )
              }
              
            </div>
          </div>
          <div className="mt-8">
            <button type="submit" className="w-full bg-white font-bold text-[#132577] p-4 rounded">Add User</button>
          </div>
        </form>

        {/* Big SVG on the right side */}
        <img src="/service icon.svg" className="flex-2 w-full hidden md:block md:w-1/3" />
      </div>
    </div>
  );
};

export default AddUserToOrganization;
