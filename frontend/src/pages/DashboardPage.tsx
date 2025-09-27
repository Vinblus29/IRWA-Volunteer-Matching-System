import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Alert,
  Fab,
} from "@mui/material";
import {
  Psychology,
  AutoAwesome,
  TrendingUp,
  School,
  Work,
  People,
  Event,
  Assessment,
  Add,
  Star,
  CheckCircle,
  Warning,
  Info,
} from "@mui/icons-material";
import { useAuth } from "../contexts/AuthContext";
import { useNotification } from "../contexts/NotificationContext";
import { volunteersAPI, eventsAPI, matchingAPI } from "../services/api";
import { useNavigate } from "react-router-dom";

interface DashboardStats {
  total_volunteers: number;
  active_volunteers: number;
  verified_volunteers: number;
  average_rating: number;
  total_hours_volunteered: number;
  top_skills: Array<{ skill: string; count: number }>;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [recentEvents, setRecentEvents] = useState<any[]>([]);
  const [recentMatches, setRecentMatches] = useState<any[]>([]);
  const { user } = useAuth();
  const { showSuccess, showError } = useNotification();
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [volunteerStats, events, matches] = await Promise.all([
        volunteersAPI.getStats(),
        eventsAPI.getEvents({ limit: 5 }),
        matchingAPI.getMatches({ limit: 5 })
      ]);
      
      setStats(volunteerStats);
      setRecentEvents(events);
      setRecentMatches(matches);
    } catch (error) {
      showError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleNavigateToSkillProfiler = () => {
    navigate("/skill-profiler");
  };

  const handleNavigateToProfile = () => {
    navigate("/profile");
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading dashboard...</Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome to the Intelligent Volunteer Matching System
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        AI-powered volunteer matching with advanced skill profiling and intelligent recommendations.
      </Typography>

      {/* Quick Actions */}
      <Paper sx={{ p: 3, mb: 3, background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", color: "white" }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Psychology />}
              onClick={handleNavigateToSkillProfiler}
              sx={{ bgcolor: "rgba(255,255,255,0.2)", "&:hover": { bgcolor: "rgba(255,255,255,0.3)" } }}
            >
              AI Skill Profiler
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Work />}
              onClick={handleNavigateToProfile}
              sx={{ bgcolor: "rgba(255,255,255,0.2)", "&:hover": { bgcolor: "rgba(255,255,255,0.3)" } }}
            >
              My Profile
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Event />}
              sx={{ bgcolor: "rgba(255,255,255,0.2)", "&:hover": { bgcolor: "rgba(255,255,255,0.3)" } }}
            >
              Browse Events
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Assessment />}
              sx={{ bgcolor: "rgba(255,255,255,0.2)", "&:hover": { bgcolor: "rgba(255,255,255,0.3)" } }}
            >
              My Matches
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {/* System Stats */}
        {stats && (
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="primary">
                        {stats.total_volunteers}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Volunteers
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="success.main">
                        {stats.verified_volunteers}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Verified
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="warning.main">
                        {stats.average_rating.toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Rating
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="info.main">
                        {stats.total_hours_volunteered}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Hours Volunteered
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* AI Features */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Features
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Psychology color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Skill Profiler"
                    secondary="AI-powered skill analysis and matching"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AutoAwesome color="secondary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Smart Matching"
                    secondary="Intelligent volunteer-event matching"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <TrendingUp color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Gap Analysis"
                    secondary="Skill development recommendations"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <School color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Learning Paths"
                    secondary="Personalized skill development"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Skills */}
        {stats && stats.top_skills.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Skills
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                  {stats.top_skills.slice(0, 10).map((skill, index) => (
                    <Chip
                      key={index}
                      label={`${skill.skill} (${skill.count})`}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Event color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="New Event Created"
                    secondary="Community Cleanup Drive"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <People color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Volunteer Matched"
                    secondary="John Doe  Food Bank Event"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Assessment color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Skill Analysis Complete"
                    secondary="5 new skills identified"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Status */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Alert severity="success" icon={<CheckCircle />}>
                Frontend: Online
              </Alert>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Alert severity="info" icon={<Info />}>
                Backend: Port 8000
              </Alert>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Alert severity="warning" icon={<Warning />}>
                Database: MongoDB Atlas
              </Alert>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{
          position: "fixed",
          bottom: 16,
          right: 16,
        }}
        onClick={handleNavigateToSkillProfiler}
      >
        <Psychology />
      </Fab>
    </Box>
  );
};

export default DashboardPage;
