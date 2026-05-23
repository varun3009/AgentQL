import { createRoot } from 'react-dom/client'
import App from './App.jsx'

import 'bootstrap/dist/css/bootstrap.min.css'
import './index.css'
import './App.css'

createRoot(document.getElementById('root')).render(
  <div className="container-fluid px-0" style={{height: "100vh"}}> 
    <App />
  </div>
)
