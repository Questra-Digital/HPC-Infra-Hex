"use client"
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import MainNavbar from '../Components/Shared/MainNavbar';
import Footer from '../Components/Footer';

const ClusterConsumptionDetails = () => {


  const chartData = [
    { name: 'Project 1', consumption: 10 },
    { name: 'Project 2', consumption: 50 },
    { name: 'Project 3', consumption: 100 },
    { name: 'Project 4', consumption: 25 },
    { name: 'Project 5', consumption: 75},
    { name: 'Project 6', consumption: 30 },
    { name: 'Project 7', consumption: 90 },
  ];

  return (
    <div className="h-screen flex flex-col gap-[10%] items-center text-white w-screen">
      <div className='flex-1 w-full h-auto  flex flex-col'>
        <MainNavbar className="flex-1" title="HPC MLOPs Infrastructure"  />
        <div className='text-black p-10 py-[5%] w-full text-center flex flex-col items-center justify-center'>
          <div className='flex-1 text-[#132577] text-xl font-bold'>
            Cluster Name: Resources Consumption
          </div>
          <div className='flex-2 text-sm px-[30%]'>
            The chart shows the no. of resources being assigned to each project, and colored areas show how much consumption has been made by each project.
          </div>

          {/* Bar Chart */}
          <div className="mt-[6%]" style={{ width: '55%', height: 600}}>
            <ResponsiveContainer>
              <BarChart
                data={chartData}
                margin={{ }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="consumption" fill="#132577" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <Footer className="flex-7" />
    </div>
  );
};

export default ClusterConsumptionDetails;
