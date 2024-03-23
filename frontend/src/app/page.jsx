"use client"
import React, { useState } from 'react';
import LandingPageHeader from '../app/Components/LandingPage/LandingPageHeader';
import Services from '../app/Components/LandingPage/Services';
import LandingPageFigures from '../app/Components/LandingPage/LandingPageFigures';
import FewWordsAboutUs from '../app/Components/LandingPage/FewWordsAboutUs';
import LandingPageProjects from '../app/Components/LandingPage/LandingPageProjects';
import CerifiedExperts from '../app/Components/LandingPage/CertifiedExperts';
import Footer from '../app/Components/Footer';
import MainNavbar from '../app/Components/Shared/MainNavbar';

const Home = () => {

  return (
    <div className="h-screen flex flex-col gap-[10%] items-center text-white w-screen">
        <div className='flex-1'>
            <MainNavbar className="" title="HPC MLOPs Infrastructure" />
            <LandingPageHeader className=""  />
        </div>
        <Services className="flex-2"/>
        <LandingPageFigures className="flex-3"/>
        <FewWordsAboutUs className="flex-4" />
        <LandingPageProjects className="flex-5"/>
        <CerifiedExperts className="flex-6"/>
        <Footer className="flex-7"/>
    </div>
   
  );
};

export default Home;
