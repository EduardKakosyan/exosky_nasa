import { useState } from 'react'
import { CSky } from './components/CSky'
import { HomeBackground } from './layout/home-background'

function App() {

  return (
    <main className='flex flex-1 flex-col h-screen w-screen'>
      {/* <Sky /> */}
      {/* <CSky /> */} 
      <div className='flex-1'>
        <HomeBackground />
      </div>
    </main>
      
  )
}

export default App
