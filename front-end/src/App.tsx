import { SkyInteractive } from './components/sky-interactive'
import { Home } from './routes/home'
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/earth" element={<SkyInteractive imgSrc='sky_image.png'/>} />
        <Route path="/55" element={<SkyInteractive imgSrc='55_Cancri_e.png'/>} />
        <Route path="/wasp" element={<SkyInteractive imgSrc='WASP-12b.png'/>} />
        <Route path="/trappist" element={<SkyInteractive imgSrc='TRAPPIST-1e.png'/>} />
        <Route path="/kepler" element={<SkyInteractive imgSrc='Kepler-186f.png'/>} />
        <Route path='/hd' element={<SkyInteractive imgSrc='hd.png'/>} />
      </Routes>
    </Router>
  );
}

export default App