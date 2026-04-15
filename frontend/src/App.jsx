import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext.jsx";

// Import components and pages
import Header from "./components/Header.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import Leaderboard from "./pages/Leaderboard.jsx";
import Modules from "./pages/Modules.jsx";
import ModulePython from "./pages/ModulePython.jsx";
import ModuleLevel from "./pages/ModuleLevel.jsx";
import ModuleJava from "./pages/ModuleJava.jsx";
import ModuleCustom from "./pages/ModuleCustom.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import MentorDashboard from "./pages/MentorDashboard.jsx";
import MentorTools from "./pages/MentorTools.jsx";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import Analytics from "./pages/Analytics.jsx";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/modules" element={<ProtectedRoute><Modules /></ProtectedRoute>} />
            <Route path="/modules/python" element={<ProtectedRoute><ModulePython /></ProtectedRoute>} />
            <Route path="/modules/python/:level" element={<ProtectedRoute><ModuleLevel moduleName="python" /></ProtectedRoute>} />
            <Route path="/modules/java" element={<ProtectedRoute><ModuleJava /></ProtectedRoute>} />
            <Route path="/modules/java/:level" element={<ProtectedRoute><ModuleLevel moduleName="java" /></ProtectedRoute>} />
            <Route path="/modules/custom/:moduleId" element={<ProtectedRoute><ModuleCustom /></ProtectedRoute>} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/mentor" element={<ProtectedRoute><MentorDashboard /></ProtectedRoute>} />
            <Route path="/mentor/tools" element={<ProtectedRoute><MentorTools /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

