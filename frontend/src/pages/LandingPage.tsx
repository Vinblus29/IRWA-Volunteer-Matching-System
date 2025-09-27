import React from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Chip,
  Paper,
} from "@mui/material";
import {
  People,
  Event,
  TrendingUp,
  Security,
  Psychology,
  Speed,
  CheckCircle,
  Star,
  ArrowForward,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Psychology />,
      title: "AI-Powered Matching",
      description: "Advanced algorithms match volunteers with events based on skills, availability, and preferences.",
    },
    {
      icon: <Speed />,
      title: "Real-Time Updates",
      description: "Get instant notifications about new matches and event updates.",
    },
    {
      icon: <Security />,
      title: "Secure Platform",
      description: "Your data is protected with enterprise-grade security measures.",
    },
    {
      icon: <TrendingUp />,
      title: "Analytics Dashboard",
      description: "Track your volunteer impact and see detailed analytics.",
    },
  ];

  const stats = [
    { number: "10,000+", label: "Active Volunteers" },
    { number: "500+", label: "Organizations" },
    { number: "50,000+", label: "Hours Volunteered" },
    { number: "95%", label: "Match Success Rate" },
  ];

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Volunteer",
      content: "This platform has made it so easy to find meaningful volunteer opportunities that match my skills and schedule.",
      avatar: "SJ",
    },
    {
      name: "Mike Chen",
      role: "Event Organizer",
      content: "The AI matching system has helped us find the perfect volunteers for our events every time.",
      avatar: "MC",
    },
    {
      name: "Emily Rodriguez",
      role: "Nonprofit Director",
      content: "Our volunteer engagement has increased by 300% since using this platform.",
      avatar: "ER",
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          py: 12,
          textAlign: "center",
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
            Intelligent Volunteer Matching System
          </Typography>
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
            Connect passionate volunteers with meaningful opportunities through AI-powered matching
          </Typography>
          <Box sx={{ display: "flex", gap: 2, justifyContent: "center", flexWrap: "wrap" }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate("/register")}
              sx={{
                bgcolor: "white",
                color: "primary.main",
                "&:hover": { bgcolor: "grey.100" },
              }}
            >
              Get Started
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate("/login")}
              sx={{
                borderColor: "white",
                color: "white",
                "&:hover": { borderColor: "white", bgcolor: "rgba(255,255,255,0.1)" },
              }}
            >
              Sign In
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={4}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Box textAlign="center">
                <Typography variant="h3" component="div" color="primary" fontWeight="bold">
                  {stat.number}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  {stat.label}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Box sx={{ bgcolor: "grey.50", py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
            Why Choose Our Platform?
          </Typography>
          <Typography variant="h6" textAlign="center" color="text.secondary" sx={{ mb: 6 }}>
            Experience the future of volunteer matching
          </Typography>
          
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ height: "100%", p: 3 }}>
                  <Box sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}>
                    <Avatar sx={{ bgcolor: "primary.main", mr: 2 }}>
                      {feature.icon}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {feature.title}
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        {feature.description}
                      </Typography>
                    </Box>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
          How It Works
        </Typography>
        <Typography variant="h6" textAlign="center" color="text.secondary" sx={{ mb: 6 }}>
          Simple steps to start making a difference
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Avatar sx={{ bgcolor: "primary.main", width: 80, height: 80, mx: "auto", mb: 2 }}>
                <People sx={{ fontSize: 40 }} />
              </Avatar>
              <Typography variant="h5" component="h3" gutterBottom>
                1. Create Profile
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Sign up and create your volunteer profile with your skills, interests, and availability.
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Avatar sx={{ bgcolor: "secondary.main", width: 80, height: 80, mx: "auto", mb: 2 }}>
                <Event sx={{ fontSize: 40 }} />
              </Avatar>
              <Typography variant="h5" component="h3" gutterBottom>
                2. Get Matched
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Our AI analyzes your profile and matches you with relevant volunteer opportunities.
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Avatar sx={{ bgcolor: "success.main", width: 80, height: 80, mx: "auto", mb: 2 }}>
                <CheckCircle sx={{ fontSize: 40 }} />
              </Avatar>
              <Typography variant="h5" component="h3" gutterBottom>
                3. Start Volunteering
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Accept matches and start making a positive impact in your community.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* Testimonials Section */}
      <Box sx={{ bgcolor: "grey.50", py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
            What Our Users Say
          </Typography>
          <Typography variant="h6" textAlign="center" color="text.secondary" sx={{ mb: 6 }}>
            Join thousands of satisfied volunteers and organizations
          </Typography>
          
          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper sx={{ p: 3, height: "100%" }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Avatar sx={{ bgcolor: "primary.main", mr: 2 }}>
                      {testimonial.avatar}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" component="div">
                        {testimonial.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {testimonial.role}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body1" color="text.secondary">
                    "{testimonial.content}"
                  </Typography>
                  <Box sx={{ display: "flex", mt: 2 }}>
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} sx={{ color: "warning.main", fontSize: 20 }} />
                    ))}
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          py: 8,
          textAlign: "center",
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" component="h2" gutterBottom>
            Ready to Make a Difference?
          </Typography>
          <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
            Join our community of volunteers and start your journey today
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate("/register")}
            endIcon={<ArrowForward />}
            sx={{
              bgcolor: "white",
              color: "primary.main",
              px: 4,
              py: 1.5,
              "&:hover": { bgcolor: "grey.100" },
            }}
          >
            Get Started Now
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
