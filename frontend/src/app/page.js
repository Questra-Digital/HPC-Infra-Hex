"use client"
import Image from 'next/image'
import Login from './Pages/login'
import AddCluster from './Pages/addCluster'
import DragAndDropPage from './Pages/dragnDropTools'

export default function Home() {
  return (
  <div className=''>
    {/* <Login/> */}
    {/* <AddCluster/> */}
    <DragAndDropPage/>
  </div>
  )
}
