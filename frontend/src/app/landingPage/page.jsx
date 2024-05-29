"use client"
import React, { useState } from 'react';
import LandingPageHeader from '../Components/LandingPage/LandingPageHeader';
import Services from '../Components/LandingPage/Services';
import LandingPageFigures from '../Components/LandingPage/LandingPageFigures';
import FewWordsAboutUs from '../Components/LandingPage/FewWordsAboutUs';
import LandingPageProjects from '../Components/LandingPage/LandingPageProjects';
import CerifiedExperts from '../Components/LandingPage/CertifiedExperts';
import Footer from '../Components/Footer';
import MainNavbar from '../Components/Shared/MainNavbar';

const LandingPage = () => {

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

export default LandingPage;
