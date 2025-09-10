# Advanced AI Video Processing Documentation

## Overview

The AI Heart Development Platform now includes comprehensive video processing capabilities powered by artificial intelligence. This system provides professional-grade video editing, enhancement, and content creation tools specifically designed for spiritual and educational content.

## Features

### 1. Video Upload and Processing
- **Supported Formats**: MP4, AVI, MOV, MKV, WebM, FLV
- **Maximum File Size**: 500MB
- **Automatic Metadata Extraction**: Duration, resolution, FPS, file size
- **Real-time Processing Status**: Live updates during upload and processing

### 2. Video Editing Pipeline

#### Trimming
- Precise time-based video trimming
- Supports millisecond accuracy
- Maintains original quality
- Automatic output optimization

#### Merging
- Combine multiple videos seamlessly
- Automatic resolution matching
- Audio synchronization
- Batch processing support

#### Effects and Transitions
- Professional video effects library
- Smooth transitions between clips
- Customizable effect parameters
- Real-time preview capabilities

### 3. AI-Powered Video Enhancement

#### Enhancement Presets
- **Spiritual Ambient**: Optimized for meditation and spiritual content
  - Brightness: +10%
  - Contrast: +20%
  - Saturation: -10%
  - Background blur and glow effects
  
- **Meditation Calm**: Perfect for relaxation videos
  - Brightness: +5%
  - Contrast: +10%
  - Saturation: -20%
  - Soft focus and warm tones
  
- **Teaching Clear**: Ideal for educational content
  - Brightness: Neutral
  - Contrast: +30%
  - Saturation: +10%
  - Sharpening and noise reduction

#### AI Upscaling
- Intelligent resolution enhancement
- Machine learning-based quality improvement
- Artifact reduction
- Supports up to 4K enhancement

### 4. Text-to-Speech Integration

#### Voice Options
- **Male Calm**: Gentle, calming voice for meditation content
- **Female Warm**: Nurturing voice for spiritual guidance
- **Male Deep**: Resonant voice for dharma talks
- **Female Gentle**: Serene voice for mantras and prayers
- **Spiritual Male**: Deep, contemplative voice
- **Spiritual Female**: Ethereal, peaceful voice

#### Features
- Natural speech synthesis
- Adjustable speech rate and tone
- Multiple language support
- Custom pronunciation handling
- Background music integration

### 5. Subtitle Generation and Translation

#### Automatic Subtitle Generation
- AI-powered speech recognition
- Timestamp synchronization
- Speaker identification
- Context-aware transcription

#### Multi-language Support
- **Primary Languages**: English, Spanish, French, German, Hindi, Sanskrit
- **Translation Features**: 
  - Real-time translation
  - Context preservation
  - Cultural adaptation
  - Technical term handling

#### Subtitle Formats
- SRT (SubRip Subtitle)
- VTT (WebVTT)
- ASS (Advanced SubStation Alpha)
- Custom formatting options

### 6. Video Analytics and Engagement Tracking

#### Metrics Tracked
- **Viewing Statistics**:
  - Total views
  - Watch time
  - Completion rate
  - Replay frequency
  
- **Engagement Metrics**:
  - User interaction points
  - Emotional response indicators
  - Learning effectiveness scores
  - Spiritual connection metrics
  
- **Technical Analytics**:
  - Processing performance
  - Quality improvements
  - File optimization results
  - Bandwidth usage

#### Real-time Dashboard
- Live analytics updates
- Visual performance charts
- Comparative analysis tools
- Export capabilities

### 7. Batch Processing

#### Supported Operations
- **Bulk Video Processing**: Process multiple videos simultaneously
- **Template Application**: Apply consistent settings across videos
- **Workflow Automation**: Predefined processing pipelines
- **Queue Management**: Priority-based processing order

#### Batch Operations
- Trimming multiple videos
- Applying enhancement presets
- Generating subtitles for video collections
- Batch text-to-speech generation
- Mass translation projects

## API Reference

### Base URL
```
/api/video/
```

### Endpoints

#### Video Upload
```http
POST /api/video/upload
Content-Type: multipart/form-data

Form Data:
- video_file: File (required)
- metadata: JSON string (optional)
```

#### Video Trimming
```http
POST /api/video/trim
Content-Type: application/json

{
  "video_id": "string",
  "start_time": number,
  "end_time": number
}
```

#### Video Merging
```http
POST /api/video/merge
Content-Type: application/json

{
  "video_ids": ["string", "string", ...],
  "output_name": "string" (optional)
}
```

#### Video Enhancement
```http
POST /api/video/enhance
Content-Type: application/json

{
  "video_id": "string",
  "enhancement_preset": "spiritual_ambient|meditation_calm|teaching_clear"
}
```

#### Text-to-Speech
```http
POST /api/video/text-to-speech
Content-Type: application/json

{
  "text": "string",
  "voice": "male_calm|female_warm|spiritual_male|spiritual_female",
  "output_name": "string" (optional)
}
```

#### Subtitle Generation
```http
POST /api/video/subtitles/generate
Content-Type: application/json

{
  "video_id": "string",
  "language": "en|es|fr|de|hi|sa"
}
```

#### Subtitle Translation
```http
POST /api/video/subtitles/translate
Content-Type: application/json

{
  "subtitle_file": "string",
  "target_language": "string"
}
```

#### Analytics
```http
GET /api/video/analytics/{video_id}
```

#### Batch Processing
```http
POST /api/video/batch-process
Content-Type: application/json

{
  "operations": [
    {
      "type": "trim|enhance|subtitles|tts|merge",
      "video_id": "string",
      "parameters": {}
    }
  ]
}
```

#### Configuration Endpoints
```http
GET /api/video/voices
GET /api/video/enhancement-presets
GET /api/video/supported-formats
GET /api/video/health
```

## Frontend Components

### VideoProcessor Component
The main React component providing a comprehensive video processing interface:

```jsx
import VideoProcessor from './components/VideoProcessor';

function App() {
  return (
    <div className="App">
      <VideoProcessor />
    </div>
  );
}
```

### Features Include
- **Tabbed Interface**: Upload, Edit, Enhance, Speech, Subtitles, Analytics
- **Drag-and-Drop Upload**: Intuitive file handling
- **Real-time Processing Feedback**: Live status updates
- **Visual Analytics Dashboard**: Charts and metrics
- **Responsive Design**: Mobile and desktop compatibility

## Installation and Setup

### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Key Dependencies
- **OpenCV**: `opencv-python==4.8.1.78`
- **MoviePy**: `moviepy==1.0.3`
- **ImageIO**: `imageio==2.34.0`
- **PyDub**: `pydub==0.25.1`

### Frontend Dependencies
```bash
npm install framer-motion react-hot-toast
```

### Environment Configuration
```bash
# Optional: Configure external services
OPENAI_API_KEY=your_openai_key_here
GOOGLE_CLOUD_TTS_KEY=your_google_tts_key
AZURE_SPEECH_KEY=your_azure_speech_key
```

## Usage Examples

### Basic Video Processing
```javascript
// Upload a video
const formData = new FormData();
formData.append('video_file', file);

const uploadResponse = await fetch('/api/video/upload', {
  method: 'POST',
  body: formData
});

const uploadResult = await uploadResponse.json();
const videoId = uploadResult.video_id;

// Trim the video
const trimResponse = await fetch('/api/video/trim', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    video_id: videoId,
    start_time: 10.0,
    end_time: 60.0
  })
});

// Enhance the video
const enhanceResponse = await fetch('/api/video/enhance', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    video_id: videoId,
    enhancement_preset: 'spiritual_ambient'
  })
});
```

### Batch Processing Example
```javascript
const batchOperations = [
  {
    type: 'trim',
    video_id: 'video1',
    parameters: { start_time: 0, end_time: 30 }
  },
  {
    type: 'enhance',
    video_id: 'video1',
    parameters: { preset: 'meditation_calm' }
  },
  {
    type: 'subtitles',
    video_id: 'video1',
    parameters: { language: 'en' }
  }
];

const batchResponse = await fetch('/api/video/batch-process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ operations: batchOperations })
});
```

## Best Practices

### Video Quality
- Use high-quality source videos (1080p or higher)
- Ensure good lighting and stable footage
- Use external microphones for better audio quality
- Keep file sizes reasonable for faster processing

### Performance Optimization
- Process videos during off-peak hours
- Use batch processing for multiple operations
- Enable GPU acceleration when available
- Monitor system resources during processing

### Content Guidelines
- Follow spiritual and educational content guidelines
- Ensure appropriate content for meditation and learning
- Use clear, calm narration for better text-to-speech results
- Include proper context for accurate subtitle generation

## Troubleshooting

### Common Issues

#### Video Upload Failures
- **File too large**: Reduce file size or split into smaller segments
- **Unsupported format**: Convert to MP4 using external tools
- **Network timeout**: Check internet connection and retry

#### Processing Errors
- **Out of memory**: Reduce video resolution or processing batch size
- **Processing timeout**: Simplify operations or increase timeout limits
- **Dependencies missing**: Ensure all required packages are installed

#### Quality Issues
- **Poor enhancement results**: Try different presets or adjust source quality
- **Subtitle accuracy problems**: Improve audio quality or manual correction
- **TTS quality issues**: Adjust text formatting or try different voices

### Support
For technical support or feature requests, please contact the development team or refer to the project documentation.

## Future Enhancements

### Planned Features
- **Real-time Collaboration**: Multi-user editing capabilities
- **Advanced AI Effects**: Machine learning-powered visual effects
- **Live Streaming Integration**: Real-time processing for live content
- **Mobile App Support**: Native mobile processing capabilities
- **Cloud Integration**: Distributed processing and storage
- **Advanced Analytics**: Deeper insights and predictive analytics

This documentation provides a comprehensive guide to the advanced AI video processing capabilities. The system is designed to be both powerful and user-friendly, enabling creators to produce high-quality spiritual and educational content with minimal effort.