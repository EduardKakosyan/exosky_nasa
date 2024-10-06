import { CSky } from './components/CSky'
import { Home } from './routes/home'
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/view" element={<CSky />} />
      </Routes>
    </Router>
  );
}

export default App