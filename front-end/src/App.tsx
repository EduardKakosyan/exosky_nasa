import { CSky } from './components/CSky'
import { Home } from './routes/home'
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/earth" element={<CSky imgSrc='sky_image.png'/>} />
        <Route path="/55" element={<CSky imgSrc='55_Cancri_e.png'/>} />
        <Route path="/wasp" element={<CSky imgSrc='WASP-12b.png'/>} />
        <Route path="/trappist" element={<CSky imgSrc='TRAPPIST-1e.png'/>} />
        <Route path="/kepler" element={<CSky imgSrc='Kepler-186f.png'/>} />
        <Route path='/hd' element={<CSky imgSrc='hd.png'/>} />
      </Routes>
    </Router>
  );
}

export default App