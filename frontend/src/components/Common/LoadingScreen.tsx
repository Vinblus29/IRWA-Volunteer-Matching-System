import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface LoadingScreenProps {
  message?: string;
  size?: number;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = "Loading...", 
  size = 60 
}) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        zIndex: 9999,
      }}
    >
      <CircularProgress 
        size={size} 
        sx={{ 
          color: 'white',
          mb: 3 
        }} 
      />
      <Typography 
        variant="h6" 
        sx={{ 
          color: 'white',
          fontWeight: 500,
          textAlign: 'center'
        }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export default LoadingScreen; 