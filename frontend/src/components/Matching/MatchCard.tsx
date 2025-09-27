import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  Avatar,
  Divider,
  LinearProgress,
  IconButton,
  Collapse,
  Rating,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  LocationOn,
  Schedule,
  Star,
  ExpandMore,
  ExpandLess,
  ThumbUp,
  ThumbDown,
  Info,
  Psychology,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useNotification } from '../../contexts/NotificationContext';
import { matchingAPI } from '../../services/api';

interface MatchCardProps {
  match: {
    match_id: string;
    volunteer_id?: string;
    volunteer_name?: string;
    event_id?: string;
    event_title?: string;
    match_score: number;
    skill_score: number;
    location_score?: number;
    availability_score?: number;
    interest_score?: number;
    commitment_score?: number;
    explanation: string;
    status: 'pending' | 'accepted' | 'declined' | 'completed';
    created_at: string;
    event_date?: string;
    event_location?: {
      city: string;
      state: string;
    };
    volunteer_skills?: Array<{
      name: string;
      level: string;
    }>;
    volunteer_rating?: number;
    event_category?: string;
    provides_training?: boolean;
    is_urgent?: boolean;
  };
  userRole: 'volunteer' | 'organization';
  onMatchUpdate?: () => void;
}

const MatchCard: React.FC<MatchCardProps> = ({ 
  match, 
  userRole,
  onMatchUpdate 
}) => {
  const [expanded, setExpanded] = useState(false);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [actionType, setActionType] = useState<'accept' | 'decline'>('accept');
  const [declineReason, setDeclineReason] = useState('');
  const [loading, setLoading] = useState(false);
  const { showSuccess, showError } = useNotification();

  const getStatusColor = (status: string) => {
    const colors: Record<string, any> = {
      'pending': 'warning',
      'accepted': 'success',
      'declined': 'error',
      'completed': 'info',
    };
    return colors[status] || 'default';
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const handleAction = async (action: 'accept' | 'decline') => {
    setLoading(true);
    try {
      if (action === 'accept') {
        await matchingAPI.acceptMatch(match.match_id);
        showSuccess('Match accepted successfully!');
      } else {
        await matchingAPI.declineMatch(match.match_id, declineReason);
        showSuccess('Match declined');
      }
      setActionDialogOpen(false);
      if (onMatchUpdate) onMatchUpdate();
    } catch (error) {
      showError(`Failed to ${action} match`);
    } finally {
      setLoading(false);
    }
  };

  const openActionDialog = (action: 'accept' | 'decline') => {
    setActionType(action);
    setActionDialogOpen(true);
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  const renderScoreBar = (label: string, score: number, color?: string) => (
    <Box sx={{ mb: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption">{label}</Typography>
        <Typography variant="caption" fontWeight="bold">
          {(score * 100).toFixed(0)}%
        </Typography>
      </Box>
      <LinearProgress 
        variant="determinate" 
        value={score * 100} 
        color={color as any || getMatchScoreColor(score)}
        sx={{ height: 6, borderRadius: 3 }}
      />
    </Box>
  );

  return (
    <>
      <Card 
        sx={{ 
          mb: 2,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            boxShadow: 4,
          },
        }}
      >
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="h3" gutterBottom>
                {userRole === 'volunteer' ? match.event_title : match.volunteer_name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Chip 
                  label={match.status} 
                  size="small" 
                  color={getStatusColor(match.status)}
                />
                {match.is_urgent && (
                  <Chip label="Urgent" size="small" color="error" />
                )}
                {match.provides_training && (
                  <Chip label="Training Provided" size="small" color="info" />
                )}
              </Box>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color={getMatchScoreColor(match.match_score)} fontWeight="bold">
                {(match.match_score * 100).toFixed(0)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Match Score
              </Typography>
            </Box>
          </Box>

          {/* Basic Info */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            {match.event_date && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Schedule color="action" fontSize="small" />
                <Typography variant="body2">
                  {formatDate(match.event_date)}
                </Typography>
              </Box>
            )}
            
            {match.event_location && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOn color="action" fontSize="small" />
                <Typography variant="body2">
                  {match.event_location.city}, {match.event_location.state}
                </Typography>
              </Box>
            )}

            {match.volunteer_rating && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Star color="warning" fontSize="small" />
                <Rating value={match.volunteer_rating} readOnly size="small" />
                <Typography variant="body2">
                  {match.volunteer_rating.toFixed(1)}
                </Typography>
              </Box>
            )}
          </Box>

          {/* AI Explanation */}
          <Box sx={{ mb: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1, borderLeft: 4, borderColor: 'primary.main' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Psychology color="primary" fontSize="small" />
              <Typography variant="subtitle2" color="primary">
                AI Match Analysis
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {match.explanation}
            </Typography>
          </Box>

          {/* Skills Preview */}
          {match.volunteer_skills && match.volunteer_skills.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Relevant Skills
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {match.volunteer_skills.slice(0, 3).map((skill, index) => (
                  <Chip
                    key={index}
                    label={`${skill.name} (${skill.level})`}
                    size="small"
                    variant="outlined"
                  />
                ))}
                {match.volunteer_skills.length > 3 && (
                  <Chip
                    label={`+${match.volunteer_skills.length - 3} more`}
                    size="small"
                    variant="outlined"
                    color="primary"
                  />
                )}
              </Box>
            </Box>
          )}

          {/* Detailed Scores - Collapsible */}
          <Collapse in={expanded}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              Detailed Matching Scores
            </Typography>
            <Box sx={{ mt: 2 }}>
              {renderScoreBar('Skill Match', match.skill_score)}
              {match.location_score !== undefined && 
                renderScoreBar('Location Compatibility', match.location_score)}
              {match.availability_score !== undefined && 
                renderScoreBar('Availability Match', match.availability_score)}
              {match.interest_score !== undefined && 
                renderScoreBar('Interest Alignment', match.interest_score)}
              {match.commitment_score !== undefined && 
                renderScoreBar('Commitment Level', match.commitment_score)}
            </Box>
          </Collapse>
        </CardContent>

        <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
          <Button
            size="small"
            startIcon={expanded ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Less Details' : 'More Details'}
          </Button>

          {match.status === 'pending' && userRole === 'volunteer' && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<ThumbDown />}
                onClick={() => openActionDialog('decline')}
                color="error"
              >
                Decline
              </Button>
              <Button
                variant="contained"
                size="small"
                startIcon={<ThumbUp />}
                onClick={() => openActionDialog('accept')}
                color="success"
              >
                Accept
              </Button>
            </Box>
          )}

          {match.status === 'accepted' && (
            <Chip label="Accepted - Awaiting Event" color="success" />
          )}

          {match.status === 'completed' && (
            <Button variant="outlined" size="small">
              Rate Experience
            </Button>
          )}
        </CardActions>
      </Card>

      {/* Action Confirmation Dialog */}
      <Dialog open={actionDialogOpen} onClose={() => setActionDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {actionType === 'accept' ? 'Accept Match' : 'Decline Match'}
        </DialogTitle>
        <DialogContent>
          {actionType === 'accept' ? (
            <Typography>
              Are you sure you want to accept this volunteer match? 
              You'll be committed to participating in this event.
            </Typography>
          ) : (
            <>
              <Typography gutterBottom>
                Please provide a reason for declining this match (optional):
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="Reason for declining..."
                value={declineReason}
                onChange={(e) => setDeclineReason(e.target.value)}
                sx={{ mt: 2 }}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleAction(actionType)} 
            variant="contained"
            color={actionType === 'accept' ? 'success' : 'error'}
            disabled={loading}
          >
            {loading ? 'Processing...' : (actionType === 'accept' ? 'Accept Match' : 'Decline Match')}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default MatchCard; 