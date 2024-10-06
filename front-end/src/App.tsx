import { useState } from 'react'
import { Sky } from './components/Sky'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Sky />
    </>

  )
}

export default App