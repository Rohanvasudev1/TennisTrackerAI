import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaTableTennis, FaPaperPlane, FaRedo, FaUser, FaRobot, FaUpload, FaPlay } from 'react-icons/fa';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Inter', sans-serif;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
`;

const Header = styled.header`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  h1 {
    color: #2d3748;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  svg {
    color: #48bb78;
    font-size: 1.8rem;
    animation: spin 20s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const ResetButton = styled.button`
  background: #f56565;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  
  &:hover {
    background: #e53e3e;
    transform: translateY(-1px);
  }
`;

const ChatArea = styled.main`
  flex: 2;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  padding: 2rem;
`;

const VideoSidebar = styled.aside`
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem;
  height: fit-content;
  max-height: 80vh;
  overflow-y: auto;
`;

const VideoCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const VideoThumbnail = styled.img`
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 0.75rem;
`;

const ThumbnailPlaceholder = styled.div`
  width: 100%;
  height: 120px;
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  border-radius: 8px;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  overflow: hidden;
`;

const TennisCourtSVG = () => (
  <svg
    width="100%"
    height="100%"
    viewBox="0 0 200 120"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ position: 'absolute', top: 0, left: 0, opacity: 0.8 }}
  >
    {/* Tennis Court Lines */}
    <rect x="20" y="20" width="160" height="80" stroke="white" strokeWidth="2" fill="none" />
    
    {/* Center Line */}
    <line x1="100" y1="20" x2="100" y2="100" stroke="white" strokeWidth="1.5" />
    
    {/* Service Boxes */}
    <line x1="20" y1="45" x2="100" y2="45" stroke="white" strokeWidth="1" />
    <line x1="100" y1="45" x2="180" y2="45" stroke="white" strokeWidth="1" />
    <line x1="20" y1="75" x2="100" y2="75" stroke="white" strokeWidth="1" />
    <line x1="100" y1="75" x2="180" y2="75" stroke="white" strokeWidth="1" />
    
    {/* Service Lines */}
    <line x1="50" y1="20" x2="50" y2="100" stroke="white" strokeWidth="1" />
    <line x1="150" y1="20" x2="150" y2="100" stroke="white" strokeWidth="1" />
    
    {/* Tennis Ball */}
    <circle cx="85" cy="55" r="4" fill="white" />
    <path d="M81 55 Q85 51 89 55 M81 55 Q85 59 89 55" stroke="#48bb78" strokeWidth="1" fill="none" />
    
    {/* Tennis Racquet */}
    <g transform="translate(120, 70) rotate(-15)">
      {/* Racquet Head */}
      <ellipse cx="0" cy="-8" rx="8" ry="12" stroke="white" strokeWidth="1.5" fill="none" />
      {/* Handle */}
      <rect x="-1" y="4" width="2" height="15" fill="white" />
      {/* Strings */}
      <line x1="-6" y1="-8" x2="6" y2="-8" stroke="white" strokeWidth="0.5" opacity="0.7" />
      <line x1="-4" y1="-4" x2="4" y2="-4" stroke="white" strokeWidth="0.5" opacity="0.7" />
      <line x1="-4" y1="0" x2="4" y2="0" stroke="white" strokeWidth="0.5" opacity="0.7" />
      <line x1="0" y1="-16" x2="0" y2="4" stroke="white" strokeWidth="0.5" opacity="0.7" />
      <line x1="-4" y1="-16" x2="-4" y2="4" stroke="white" strokeWidth="0.5" opacity="0.7" />
      <line x1="4" y1="-16" x2="4" y2="4" stroke="white" strokeWidth="0.5" opacity="0.7" />
    </g>
    
    {/* Play Button Overlay */}
    <circle cx="100" cy="60" r="15" fill="rgba(255,255,255,0.9)" />
    <polygon points="94,52 94,68 110,60" fill="#48bb78" />
  </svg>
);

const TennisPlaceholderIcon = styled.div`
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  
  .tennis-icon {
    font-size: 2rem;
    opacity: 0.9;
  }
  
  .video-text {
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.8;
  }
`;

const VideoTitle = styled.h3`
  font-size: 0.9rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
  line-height: 1.3;
`;

const VideoCategory = styled.p`
  font-size: 0.75rem;
  color: #718096;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const VideoLink = styled.a`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #48bb78;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.85rem;
  
  &:hover {
    color: #38a169;
  }
`;

const VideoUploadZone = styled.div`
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  margin: 0.5rem 0;
  background: ${props => props.isDragOver ? '#f7fafc' : 'transparent'};
  border-color: ${props => props.isDragOver ? '#48bb78' : '#e2e8f0'};
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: #48bb78;
    background: #f7fafc;
  }

  p {
    margin: 0.3rem 0;
    font-size: 0.9rem;
  }

  p:first-of-type {
    font-weight: 600;
  }
`;

const UploadButton = styled.button`
  background: #48bb78;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 auto;
  font-weight: 500;
  transition: all 0.2s;
  
  &:hover {
    background: #38a169;
    transform: translateY(-1px);
  }
  
  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
    transform: none;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  margin: 1rem 0;
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    height: 100%;
    width: ${props => props.progress || 0}%;
    background: linear-gradient(90deg, #48bb78, #38a169);
    transition: width 0.3s ease;
  }
`;

const VideoAnalysisCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #48bb78;
`;

const VideoPlayer = styled.video`
  width: 100%;
  max-width: 400px;
  border-radius: 8px;
  margin: 1rem 0;
`;

const ChatContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const WelcomeMessage = styled.div`
  padding: 2rem;
  text-align: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  
  h2 {
    color: #2d3748;
    margin-bottom: 1rem;
    font-size: 1.8rem;
  }
  
  p {
    color: #4a5568;
    margin-bottom: 1rem;
    line-height: 1.6;
  }
  
  ul {
    list-style: none;
    margin: 1rem 0;
    
    li {
      color: #4a5568;
      margin: 0.5rem 0;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      
      svg {
        color: #48bb78;
      }
    }
  }
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  max-height: 600px;
`;

const Message = styled.div`
  margin: 1rem 0;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  
  &.user {
    flex-direction: row-reverse;
  }
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 16px;
  line-height: 1.5;
  
  &.user {
    background: #4299e1;
    color: white;
    border-bottom-right-radius: 4px;
  }
  
  &.assistant {
    background: #f7fafc;
    color: #2d3748;
    border: 1px solid #e2e8f0;
    border-bottom-left-radius: 4px;
  }
  
  /* Markdown styling */
  p {
    margin-bottom: 0.75rem;
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  strong {
    font-weight: 600;
    color: #1a202c;
  }
  
  ul, ol {
    margin: 0.75rem 0;
    padding-left: 1.5rem;
  }
  
  li {
    margin-bottom: 0.5rem;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    margin: 1rem 0 0.5rem 0;
    color: #1a202c;
  }
  
  code {
    background: #edf2f7;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9em;
  }
`;

const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &.user {
    background: #4299e1;
    color: white;
  }
  
  &.assistant {
    background: #48bb78;
    color: white;
  }
`;

const InputContainer = styled.div`
  margin-top: 1rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  padding: 0.75rem;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  
  input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s;
    
    &:focus {
      border-color: #4299e1;
    }
  }
  
  button {
    background: #48bb78;
    color: white;
    border: none;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    transition: background 0.2s;
    
    &:hover:not(:disabled) {
      background: #38a169;
    }
    
    &:disabled {
      background: #a0aec0;
      cursor: not-allowed;
    }
  }
`;

const QuickQuestions = styled.div`
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  
  span {
    color: #4a5568;
    font-size: 0.9rem;
    margin-right: 0.5rem;
  }
`;

const QuickButton = styled.button`
  background: #edf2f7;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  
  &:hover {
    background: #e2e8f0;
    color: #2d3748;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  font-style: italic;
  
  svg {
    animation: spin 1s linear infinite;
  }
`;

// Video thumbnail component with tennis court fallback
const VideoThumbnailContainer = ({ videoId, video }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const thumbnailUrl = videoId ? `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg` : '';

  const handleImageLoad = () => {
    setImageLoaded(true);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoaded(false);
  };

  // Show placeholder if no videoId, image failed to load, or no thumbnail URL
  if (!videoId || imageError || !thumbnailUrl) {
    return (
      <ThumbnailPlaceholder>
        <TennisCourtSVG />
        <TennisPlaceholderIcon>
          <FaPlay className="tennis-icon" />
          <span className="video-text">Tennis Video</span>
        </TennisPlaceholderIcon>
      </ThumbnailPlaceholder>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {/* Show placeholder while loading */}
      {!imageLoaded && (
        <ThumbnailPlaceholder>
          <TennisCourtSVG />
          <TennisPlaceholderIcon>
            <FaPlay className="tennis-icon" />
            <span className="video-text">Loading...</span>
          </TennisPlaceholderIcon>
        </ThumbnailPlaceholder>
      )}
      
      {/* Actual thumbnail image */}
      <VideoThumbnail
        src={thumbnailUrl}
        alt={video.title}
        onLoad={handleImageLoad}
        onError={handleImageError}
        style={{ display: imageLoaded ? 'block' : 'none' }}
      />
    </div>
  );
};

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [currentVideos, setCurrentVideos] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [videoAnalysis, setVideoAnalysis] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async (message = inputValue) => {
    if (!message.trim() || isLoading) return;

    const userMessage = { role: 'user', content: message.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setShowWelcome(false);
    setIsLoading(true);

    try {
      const response = await axios.post('/chat', {
        message: message.trim()
      });

      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.response 
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update videos if provided
      if (response.data.videos && response.data.videos.length > 0) {
        setCurrentVideos(response.data.videos);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetConversation = async () => {
    try {
      await axios.post('/reset');
      setMessages([]);
      setShowWelcome(true);
      setCurrentVideos([]);
      setVideoAnalysis(null);
    } catch (error) {
      console.error('Error resetting conversation:', error);
    }
  };

  // Helper function to extract YouTube video ID
  const getYouTubeId = (url) => {
    const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([A-Za-z0-9_-]{6,})/);
    return match ? match[1] : null;
  };

  // Video upload functions
  const handleVideoUpload = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('video', file);

    setIsUploading(true);
    setUploadProgress(0);
    setShowWelcome(false);

    // Add upload message to chat
    const uploadMessage = {
      role: 'user',
      content: `🎥 Uploading video: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`,
      type: 'video_upload'
    };
    setMessages(prev => [...prev, uploadMessage]);

    try {
      const response = await axios.post('/upload-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });

      if (response.data.success) {
        // Start polling for analysis results
        pollVideoAnalysis(response.data.video_id);
        
        const analysisMessage = {
          role: 'assistant',
          content: '🎾 Video uploaded successfully! I\'m now analyzing your tennis technique using computer vision. This may take a few moments...',
          type: 'analysis_start'
        };
        setMessages(prev => [...prev, analysisMessage]);
      }
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, there was an error uploading your video. Please try again with a smaller file or different format.',
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const pollVideoAnalysis = async (videoId) => {
    const maxAttempts = 60; // 5 minutes maximum
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await axios.get(`/video-analysis/${videoId}`);
        const data = response.data;

        if (data.status === 'completed') {
          // Analysis complete - show results
          setVideoAnalysis(data);
          
          const resultsMessage = {
            role: 'assistant',
            content: data.coaching_feedback,
            type: 'video_analysis',
            videoData: {
              processed_video_url: data.processed_video_url,
              analysis: data.analysis
            }
          };
          setMessages(prev => [...prev, resultsMessage]);
          
        } else if (data.status === 'error') {
          const errorMessage = {
            role: 'assistant',
            content: `Analysis failed: ${data.error}`,
            type: 'error'
          };
          setMessages(prev => [...prev, errorMessage]);
          
        } else if (attempts < maxAttempts) {
          // Still processing - continue polling
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          // Timeout
          const timeoutMessage = {
            role: 'assistant',
            content: 'Video analysis is taking longer than expected. Please try uploading a shorter video.',
            type: 'error'
          };
          setMessages(prev => [...prev, timeoutMessage]);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    poll();
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('video/')) {
        handleVideoUpload(file);
      } else {
        alert('Please upload a video file (MP4, AVI, MOV, MKV)');
      }
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleVideoUpload(file);
    }
  };


  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <AppContainer>
      <Header>
        <Logo>
          <FaTableTennis />
          <h1>Tennis Coach AI</h1>
        </Logo>
        <ResetButton onClick={resetConversation}>
          <FaRedo />
          New Session
        </ResetButton>
      </Header>

      <MainContent>
        <ChatArea>
          <ChatContainer>
          {showWelcome && (
            <WelcomeMessage>
              <h2>Welcome to your Personal Tennis Coach! 🎾</h2>
              <p>I'm here to help improve your tennis game. Ask me about:</p>
              <ul>
                <li><FaTableTennis /> Stroke technique (forehand, backhand, serve, volley)</li>
                <li><FaTableTennis /> Strategy and tactics</li>
                <li><FaTableTennis /> Tennis-specific fitness</li>
                <li><FaTableTennis /> Equipment recommendations</li>
              </ul>
              <p>What would you like to work on today?</p>
            </WelcomeMessage>
          )}

          <ChatMessages>
            {messages.map((message, index) => (
              <Message key={index} className={message.role}>
                <Avatar className={message.role}>
                  {message.role === 'user' ? <FaUser /> : <FaRobot />}
                </Avatar>
                <MessageBubble className={message.role}>
                  {message.role === 'assistant' ? (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  ) : (
                    message.content
                  )}
                  
                  {/* Video analysis results */}
                  {message.type === 'video_analysis' && message.videoData && (
                    <VideoAnalysisCard>
                      <h4>🎾 Video Analysis Results</h4>
                      <VideoPlayer controls>
                        <source src={message.videoData.processed_video_url} type="video/mp4" />
                        Your browser does not support video playback.
                      </VideoPlayer>
                      <div>
                        <strong>Analysis Data:</strong>
                        <ul>
                          <li>Total Frames: {message.videoData.analysis?.total_frames}</li>
                          <li>Player Positions: {message.videoData.analysis?.player_positions}</li>
                          <li>Ball Detections: {message.videoData.analysis?.ball_detections}</li>
                          <li>Court Keypoints: {message.videoData.analysis?.court_keypoints}</li>
                        </ul>
                      </div>
                    </VideoAnalysisCard>
                  )}
                </MessageBubble>
              </Message>
            ))}
            {isLoading && (
              <Message className="assistant">
                <Avatar className="assistant">
                  <FaRobot />
                </Avatar>
                <LoadingSpinner>
                  <FaTableTennis />
                  Coach is thinking...
                </LoadingSpinner>
              </Message>
            )}
            <div ref={messagesEndRef} />
          </ChatMessages>
        </ChatContainer>

        <InputContainer>
          {/* Video Upload Zone */}
          <VideoUploadZone
            isDragOver={isDragOver}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <FaUpload size={24} color="#48bb78" />
            <p><strong>Upload Tennis Video for Analysis</strong></p>
            <p>Drag & drop a video file here or click to browse</p>
            <p style={{fontSize: '0.8rem', color: '#718096'}}>
              Supports MP4, AVI, MOV, MKV (max 100MB)
            </p>
            {isUploading && (
              <div>
                <ProgressBar progress={uploadProgress} />
                <p>{uploadProgress}% uploaded</p>
              </div>
            )}
          </VideoUploadZone>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileInput}
            style={{display: 'none'}}
          />
          
          <InputWrapper>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about tennis..."
              maxLength={500}
              disabled={isLoading}
            />
            <button onClick={() => sendMessage()} disabled={isLoading}>
              <FaPaperPlane />
            </button>
          </InputWrapper>
          
          <QuickQuestions>
            <span>Quick questions:</span>
            <QuickButton onClick={() => sendMessage('How can I improve my forehand?')}>
              Improve Forehand
            </QuickButton>
            <QuickButton onClick={() => sendMessage('What racquet should I buy as a beginner?')}>
              Racquet Advice
            </QuickButton>
            <QuickButton onClick={() => sendMessage('How do I get more powerful serves?')}>
              Powerful Serve
            </QuickButton>
          </QuickQuestions>
        </InputContainer>
        </ChatArea>

        {/* Video Sidebar */}
        {currentVideos.length > 0 && (
          <VideoSidebar>
            <h3 style={{marginBottom: '1rem', color: '#2d3748', fontSize: '1.1rem'}}>
              📹 Recommended Videos
            </h3>
            {currentVideos.map((video, index) => {
              const videoId = getYouTubeId(video.url);
              
              return (
                <VideoCard key={index}>
                  <VideoThumbnailContainer 
                    videoId={videoId} 
                    video={video}
                    key={`${videoId}-${index}`} 
                  />
                  <VideoTitle>{video.title}</VideoTitle>
                  <VideoCategory>{video.category || 'Tennis'}</VideoCategory>
                  <VideoLink href={video.url} target="_blank" rel="noopener noreferrer">
                    🎥 Watch Video
                  </VideoLink>
                </VideoCard>
              );
            })}
          </VideoSidebar>
        )}
      </MainContent>
    </AppContainer>
  );
}

export default App;