import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/auth/Login'
import Register from './components/auth/Register'
import PasswordReset from './components/auth/PasswordReset'
import ProtectedRoute from './components/auth/ProtectedRoute'
import FileConverter from './components/FileConverter'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/password-reset" element={<PasswordReset />} />
        <Route
          path="/converter"
          element={
            <ProtectedRoute>
              <FileConverter />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/converter" replace />} />
      </Routes>
    </Router>
  )
}

export default App
