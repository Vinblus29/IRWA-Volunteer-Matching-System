import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { CssBaseline, Box, AppBar, Toolbar, Typography, Button, Container } from "@mui/material";
import { AuthProvider } from "./contexts/AuthContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import EventManagementPage from "./pages/EventManagementPage";
import SkillProfiler from "./components/SkillProfiler";
import EventMatcher from "./components/EventMatcher";
import { AvailabilityTracker } from "./components/AvailabilityTracker";
import { OrganizationManagement } from "./components/OrganizationManagement";
import { AdminDashboard } from "./components/AdminDashboard";
import { NotificationDisplay } from "./components/NotificationDisplay";
import VolunteerProfile from "./components/Volunteers/VolunteerProfile";
import "./App.css";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <NotificationProvider>
          <Router>
            <Box sx={{ flexGrow: 1 }}>
              <AppBar position="static">
                <Toolbar>
                  <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                    Intelligent Volunteer Matching System
                  </Typography>
                  <Button color="inherit" href="/login">
                    Login
                  </Button>
                  <Button color="inherit" href="/register">
                    Register
                  </Button>
                </Toolbar>
              </AppBar>
              
              <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <DashboardPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/skill-profiler"
                    element={
                      <ProtectedRoute>
                        <SkillProfiler />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/event-matcher"
                    element={
                      <ProtectedRoute>
                        <EventMatcher />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/availability-tracker"
                    element={
                      <ProtectedRoute>
                        <AvailabilityTracker />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/event-management"
                    element={
                      <ProtectedRoute>
                        <EventManagementPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/organization-management"
                    element={
                      <ProtectedRoute>
                        <OrganizationManagement />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/admin-dashboard"
                    element={
                      <ProtectedRoute>
                        <AdminDashboard />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/notifications"
                    element={
                      <ProtectedRoute>
                        <NotificationDisplay />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <VolunteerProfile />
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </Container>
            </Box>
          </Router>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
