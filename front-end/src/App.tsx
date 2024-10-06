import { CSky } from './components/CSky'
import { Home } from './routes/home'
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/earth" element={<CSky imgSrc='sky_image.jpg'/>} />
        <Route path="/55" element={<CSky imgSrc='55_Cancri_e.png'/>} />
        <Route path="/wasp" element={<CSky imgSrc='WASP-12b.png'/>} />
      </Routes>
    </Router>
  );
}

export default App