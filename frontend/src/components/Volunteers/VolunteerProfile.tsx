import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Rating,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Fab,
} from '@mui/material';
import {
  Edit,
  LocationOn,
  Schedule,
  Star,
  Phone,
  Email,
  Language,
  Verified,
  Add,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../../contexts/NotificationContext';
import { volunteersAPI } from '../../services/api';

interface VolunteerProfileData {
  id: string;
  profile: {
    full_name: string;
    bio: string;
    phone: string;
    date_of_birth: string;
    languages: string[];
  };
  skills: Array<{
    name: string;
    level: string;
    years_experience: number;
    certifications: string[];
  }>;
  availability: Array<{
    day: string;
    start_time: string;
    end_time: string;
  }>;
  location: {
    city: string;
    state: string;
    postal_code: string;
  };
  rating: number;
  total_hours_volunteered: number;
  events_completed: number;
  is_verified: boolean;
  preferences: {
    preferred_event_types: string[];
    commitment_level: string;
    travel_radius_km: number;
  };
}

const VolunteerProfile: React.FC = () => {
  const [profile, setProfile] = useState<VolunteerProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editField, setEditField] = useState<string>('');
  const { user } = useAuth();
  const { showSuccess, showError } = useNotification();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await volunteersAPI.getMyProfile();
      setProfile(data);
    } catch (error) {
      showError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = async (field: string, value: any) => {
    try {
      const updateData = { [field]: value };
      await volunteersAPI.updateProfile(updateData);
      showSuccess('Profile updated successfully');
      loadProfile();
    } catch (error) {
      showError('Failed to update profile');
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading profile...</Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          No Profile Found
        </Typography>
        <Typography color="text.secondary" gutterBottom>
          It looks like you haven't created a volunteer profile yet.
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }}>
          Create Profile
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item>
            <Avatar
              sx={{
                width: 100,
                height: 100,
                fontSize: '2rem',
                backgroundColor: 'rgba(255,255,255,0.2)',
              }}
            >
              {profile.profile.full_name.charAt(0)}
            </Avatar>
          </Grid>
          <Grid item xs>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="h4" component="h1">
                {profile.profile.full_name}
              </Typography>
              {profile.is_verified && (
                <Verified color="inherit" />
              )}
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Rating value={profile.rating} readOnly size="small" />
              <Typography variant="body2">
                {profile.rating.toFixed(1)} rating
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 3 }}>
              <Box>
                <Typography variant="h6">{profile.total_hours_volunteered}</Typography>
                <Typography variant="caption">Hours Volunteered</Typography>
              </Box>
              <Box>
                <Typography variant="h6">{profile.events_completed}</Typography>
                <Typography variant="caption">Events Completed</Typography>
              </Box>
              <Box>
                <Typography variant="h6">{profile.skills.length}</Typography>
                <Typography variant="caption">Skills</Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              startIcon={<Edit />}
              onClick={() => {
                setEditField('profile');
                setEditDialogOpen(true);
              }}
              sx={{ color: 'white', borderColor: 'white' }}
            >
              Edit Profile
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {/* About Section */}
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                About
              </Typography>
              <Typography variant="body1" paragraph>
                {profile.profile.bio || 'No bio provided yet.'}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <LocationOn color="action" />
                    <Typography variant="body2">
                      {profile.location.city}, {profile.location.state}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Phone color="action" />
                    <Typography variant="body2">
                      {profile.profile.phone || 'Not provided'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Language color="action" />
                    <Typography variant="body2">
                      {profile.profile.languages.join(', ') || 'Not specified'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Skills Section */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Skills & Expertise
                </Typography>
                <Button
                  size="small"
                  startIcon={<Add />}
                  onClick={() => {
                    setEditField('skills');
                    setEditDialogOpen(true);
                  }}
                >
                  Add Skill
                </Button>
              </Box>
              
              <Grid container spacing={1}>
                {profile.skills.map((skill, index) => (
                  <Grid item key={index}>
                    <Chip
                      label={`${skill.name} (${skill.level})`}
                      variant="outlined"
                      size="small"
                      sx={{ mb: 1 }}
                    />
                  </Grid>
                ))}
              </Grid>

              {profile.skills.length === 0 && (
                <Typography color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  No skills added yet. Add your skills to get better matches!
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Preferences Section */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Preferences
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Preferred Event Types
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {profile.preferences.preferred_event_types.map((type, index) => (
                    <Chip key={index} label={type} size="small" />
                  ))}
                </Box>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Commitment Level
                </Typography>
                <Chip 
                  label={profile.preferences.commitment_level} 
                  color={
                    profile.preferences.commitment_level === 'high' ? 'success' :
                    profile.preferences.commitment_level === 'medium' ? 'warning' : 'default'
                  }
                />
              </Box>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Travel Radius
                </Typography>
                <Typography variant="body2">
                  Up to {profile.preferences.travel_radius_km} km
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Availability */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Availability
                </Typography>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => {
                    setEditField('availability');
                    setEditDialogOpen(true);
                  }}
                >
                  Edit
                </Button>
              </Box>
              
              <List dense>
                {profile.availability.map((slot, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemIcon>
                      <Schedule color="action" />
                    </ListItemIcon>
                    <ListItemText
                      primary={slot.day.charAt(0).toUpperCase() + slot.day.slice(1)}
                      secondary={`${slot.start_time} - ${slot.end_time}`}
                    />
                  </ListItem>
                ))}
              </List>

              {profile.availability.length === 0 && (
                <Typography color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  No availability set
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Profile Completion */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profile Completion
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Progress</Typography>
                  <Typography variant="body2">85%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={85} />
              </Box>

              <Typography variant="body2" color="text.secondary">
                Complete your profile to get better volunteer matches and increase your visibility to organizations.
              </Typography>

              <Button variant="outlined" fullWidth sx={{ mt: 2 }}>
                Complete Profile
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={() => {
          setEditField('profile');
          setEditDialogOpen(true);
        }}
      >
        <Edit />
      </Fab>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit {editField}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            This would open the appropriate edit form for {editField}.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VolunteerProfile; 