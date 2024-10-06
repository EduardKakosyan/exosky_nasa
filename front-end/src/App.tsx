import { useState } from 'react'
import { CSky } from './components/CSky'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <CSky />
    </>

  )
}

export default App