import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Avatar,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  Event,
  Schedule,
  Star,
  TrendingUp,
  Notifications,
  Assignment,
} from '@mui/icons-material';
import { dashboardAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../../contexts/NotificationContext';

interface DashboardData {
  profile: {
    volunteer_id: string;
    name: string;
    total_hours: number;
    events_completed: number;
    rating: number;
    is_verified: boolean;
    skills_count: number;
  };
  statistics: {
    total_matches: number;
    pending_matches: number;
    accepted_matches: number;
    completed_matches: number;
    success_rate: number;
  };
  upcoming_events: Array<{
    event_id: string;
    title: string;
    date: string;
    time: string;
    location: any;
    match_id: string;
  }>;
  recent_matches: Array<{
    match_id: string;
    event_title: string;
    match_score: number;
    status: string;
    created_at: string;
  }>;
  skill_recommendations: Array<{
    skill: string;
    reason: string;
    demand: string;
  }>;
  notifications_count: number;
}

const VolunteerDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { showSuccess, showError } = useNotification();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await dashboardAPI.getVolunteerDashboard();
      setDashboardData(data);
    } catch (error) {
      showError('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading dashboard...</Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Unable to load dashboard data</Typography>
      </Box>
    );
  }

  const { profile, statistics, upcoming_events, recent_matches, skill_recommendations } = dashboardData;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {profile.name || user?.full_name}!
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Here's your volunteer activity overview
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CardContent>
              <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 2 }}>
                <Schedule />
              </Avatar>
              <Typography variant="h4" color="primary">
                {profile.total_hours}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Hours Volunteered
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CardContent>
              <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 2 }}>
                <Event />
              </Avatar>
              <Typography variant="h4" color="success.main">
                {profile.events_completed}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Events Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CardContent>
              <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 2 }}>
                <Star />
              </Avatar>
              <Typography variant="h4" color="warning.main">
                {profile.rating.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Rating
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CardContent>
              <Avatar sx={{ bgcolor: 'info.main', mx: 'auto', mb: 2 }}>
                <TrendingUp />
              </Avatar>
              <Typography variant="h4" color="info.main">
                {statistics.success_rate.toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Match Success Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Upcoming Events */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upcoming Events
              </Typography>
              {upcoming_events.length > 0 ? (
                <List>
                  {upcoming_events.map((event) => (
                    <ListItem key={event.event_id} divider>
                      <ListItemIcon>
                        <Event color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={event.title}
                        secondary={`${event.date} at ${event.time}`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No upcoming events scheduled
                </Typography>
              )}
              <Button 
                variant="outlined" 
                fullWidth 
                sx={{ mt: 2 }}
                onClick={() => window.location.href = '/events'}
              >
                Find More Events
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Matches */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Matches
              </Typography>
              {recent_matches.length > 0 ? (
                <List>
                  {recent_matches.map((match) => (
                    <ListItem key={match.match_id} divider>
                      <ListItemIcon>
                        <Assignment />
                      </ListItemIcon>
                      <ListItemText
                        primary={match.event_title}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip 
                              label={match.status} 
                              size="small" 
                              color={match.status === 'accepted' ? 'success' : 'default'}
                            />
                            <Typography variant="caption">
                              {(match.match_score * 100).toFixed(0)}% match
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No recent matches
                </Typography>
              )}
              <Button 
                variant="outlined" 
                fullWidth 
                sx={{ mt: 2 }}
                onClick={() => window.location.href = '/matching'}
              >
                View All Matches
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profile Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Profile Completion</Typography>
                  <Typography variant="body2">85%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={85} />
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                <Chip 
                  label={profile.is_verified ? "Verified" : "Unverified"} 
                  color={profile.is_verified ? "success" : "default"} 
                  size="small" 
                />
                <Chip 
                  label={`${profile.skills_count} Skills`} 
                  size="small" 
                />
              </Box>

              <Button 
                variant="outlined" 
                fullWidth
                onClick={() => window.location.href = '/profile'}
              >
                Update Profile
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Skill Recommendations */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommended Skills
              </Typography>
              {skill_recommendations.length > 0 ? (
                <List>
                  {skill_recommendations.map((rec, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={rec.skill}
                        secondary={
                          <>
                            <Typography variant="body2">{rec.reason}</Typography>
                            <Chip 
                              label={rec.demand} 
                              size="small" 
                              variant="outlined"
                              sx={{ mt: 1 }}
                            />
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No skill recommendations available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default VolunteerDashboard; 