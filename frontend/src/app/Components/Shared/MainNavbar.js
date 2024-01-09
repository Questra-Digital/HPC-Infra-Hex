import React from 'react';

const MainNavbar = ({ title, pages }) => {
  return (
    <div className="bg-[#132577] flex flex-col items-center h-auto px-10 w-full py-4">
        <div className='flex flex-1  items-center justify-between w-full'>
            <div className="flex items-center justify-center">
                <img src="/logo.svg" className="h-24" alt="Logo" />
                <h1 className="text-xl md:text-2xl font-semibold ml-4">{title}</h1>
            </div>
            <div className="flex">
                {pages.map((page, index) => (
                <a
                    key={index}
                    href={page.link}
                    className="text-white ml-4 hover:text-gray-300 transition duration-300"
                >
                    {page.title}
                </a>
                ))}
            </div>
        </div>

    </div>
  );
};

export default MainNavbar;
