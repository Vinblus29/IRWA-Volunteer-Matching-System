import React from "react";
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  Button,
  Grid,
} from "@mui/material";
import {
  LocationOn,
  Schedule,
  Group,
  Star,
  Warning,
  School,
} from "@mui/icons-material";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";

interface EventCardProps {
  event: {
    id: string;
    title: string;
    description: string;
    location: {
      city: string;
      state: string;
    };
    start_date: string;
    start_time: string;
    max_volunteers: number;
    current_volunteers: number;
    event_type: string;
    difficulty_level?: string;
    image_url?: string;
  };
  onJoin?: (eventId: string) => void;
  onViewDetails?: (eventId: string) => void;
}

const EventCard: React.FC<EventCardProps> = ({
  event,
  onJoin,
  onViewDetails,
}) => {
  const navigate = useNavigate();

  const handleJoin = () => {
    if (onJoin) {
      onJoin(event.id);
    }
  };

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(event.id);
    } else {
      navigate(`/events/${event.id}`);
    }
  };

  const getEventTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "workshop":
        return "primary";
      case "conference":
        return "secondary";
      case "fundraiser":
        return "error";
      case "community_service":
        return "success";
      default:
        return "default";
    }
  };

  const getDifficultyColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case "beginner":
        return "success";
      case "intermediate":
        return "warning";
      case "advanced":
        return "error";
      default:
        return "default";
    }
  };

  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "transform 0.2s ease-in-out",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: 4,
        },
      }}
    >
      {event.image_url && (
        <CardMedia
          component="img"
          height="200"
          image={event.image_url}
          alt={event.title}
        />
      )}
      
      <CardContent sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {event.title}
        </Typography>
        
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {event.description}
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Chip
            label={event.event_type}
            color={getEventTypeColor(event.event_type) as any}
            size="small"
            sx={{ mr: 1, mb: 1 }}
          />
          {event.difficulty_level && (
            <Chip
              label={event.difficulty_level}
              color={getDifficultyColor(event.difficulty_level) as any}
              size="small"
              sx={{ mr: 1, mb: 1 }}
            />
          )}
        </Box>

        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={12}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <LocationOn sx={{ mr: 1, fontSize: 16, color: "text.secondary" }} />
              <Typography variant="body2" color="text.secondary">
                {event.location.city}, {event.location.state}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <Schedule sx={{ mr: 1, fontSize: 16, color: "text.secondary" }} />
              <Typography variant="body2" color="text.secondary">
                {format(new Date(event.start_date), "MMM dd, yyyy")} at{" "}
                {format(new Date(`2000-01-01T${event.start_time}`), "h:mm a")}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Group sx={{ mr: 1, fontSize: 16, color: "text.secondary" }} />
              <Typography variant="body2" color="text.secondary">
                {event.current_volunteers} / {event.max_volunteers} volunteers
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Box sx={{ mt: "auto", display: "flex", gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={handleViewDetails}
            sx={{ flex: 1 }}
          >
            View Details
          </Button>
          <Button
            variant="contained"
            size="small"
            onClick={handleJoin}
            disabled={event.current_volunteers >= event.max_volunteers}
            sx={{ flex: 1 }}
          >
            {event.current_volunteers >= event.max_volunteers ? "Full" : "Join"}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EventCard;
