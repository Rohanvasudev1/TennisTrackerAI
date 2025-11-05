from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import json
import os
from typing import Dict, Any
import uuid
import requests
from urllib.parse import urlparse
import time
import re
import uuid
import os
from werkzeug.utils import secure_filename
import threading
from dotenv import load_dotenv

load_dotenv()

# Import video analysis components
import sys
sys.path.append('.')
from utils.video_utils import read_video, save_video
from trackers.player_tracker import PlayerTracker
from trackers.ball_tracker import BallTracker  
from court_detector.court_detector import CourtLineDetector

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB limit
CORS(app)

# Initialize OpenAI client with error handling
try:
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )
    print("✅ OpenAI client initialized successfully")
except Exception as e:
    print(f"⚠️ OpenAI client initialization failed: {e}")
    print("🚀 Server will start without OpenAI client (video upload will still work)")
    client = None

YOUTUBE_ID_RX = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{6,})")

def yt_id(url: str) -> str | None:
    m = YOUTUBE_ID_RX.search(url)
    return m.group(1) if m else None

def format_video_recommendations(videos):
    """
    videos: list of dicts like {"title": "...", "url": "...", "category": "..." (optional)}
    Returns clean text format for chat display.
    """
    lines = []
    for i, v in enumerate(videos, 1):
        title = v["title"].strip()
        link = v["url"]
        lines.append(f"{i}. 📹 **{title}** - [Watch Here]({link})")
    return "\n\n".join(lines)

def load_knowledge_base() -> Dict[str, Any]:
    """Load all knowledge base files into memory"""
    knowledge_base = {}
    kb_directory = "knowledge_base"
    
    if not os.path.exists(kb_directory):
        return knowledge_base
    
    for filename in os.listdir(kb_directory):
        if filename.endswith('.json'):
            filepath = os.path.join(kb_directory, filename)
            try:
                with open(filepath, 'r') as f:
                    category = filename.replace('.json', '')
                    knowledge_base[category] = json.load(f)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return knowledge_base

def get_relevant_knowledge(query: str, knowledge_base: Dict[str, Any]) -> tuple[str, list]:
    """Search knowledge base for relevant information based on query"""
    query_lower = query.lower()
    relevant_info = []
    
    # Search for specific terms including videos
    search_terms = {
        'forehand': ['strokes', 'videos'],
        'backhand': ['strokes', 'videos'], 
        'serve': ['strokes', 'videos'],
        'volley': ['strokes', 'videos'],
        'strategy': ['strategy', 'videos'],
        'fitness': ['fitness', 'videos'],
        'equipment': ['equipment'],
        'racquet': ['equipment'],
        'string': ['equipment'],
        'grip': ['strokes', 'equipment'],
        'rules': ['resources'],
        'drill': ['resources', 'videos'],
        'drills': ['resources', 'videos'],
        'coaching': ['resources', 'videos'],
        'practice': ['resources', 'videos'],
        'biomechanics': ['resources', 'videos'],
        'injury': ['resources'],
        'conditioning': ['resources', 'videos'],
        'tactics': ['resources', 'videos'],
        'doubles': ['strategy', 'resources', 'videos'],
        'tournament': ['resources'],
        'scoring': ['resources'],
        'tiebreaker': ['resources'],
        'footwork': ['videos'],
        'movement': ['videos'],
        'video': ['videos'],
        'videos': ['videos']
    }
    
    # First check traditional knowledge base files
    for term, categories in search_terms.items():
        if term in query_lower:
            for cat in categories:
                if cat in knowledge_base and cat not in ['resources', 'videos']:
                    relevant_info.append(f"\n--- {cat.upper()} KNOWLEDGE ---")
                    relevant_info.append(json.dumps(knowledge_base[cat], indent=2))
                    break
    
    # Check for relevant videos
    video_recommendations = []
    if 'videos' in knowledge_base:
        videos_data = knowledge_base['videos']
        # Handle case where videos is a list (flat structure)
        if isinstance(videos_data, list):
            for term, categories in search_terms.items():
                if term in query_lower and 'videos' in categories:
                    for video in videos_data:
                        video_title = video.get('title', '').lower()
                        video_category = video.get('category', '').lower()
                        if (term in video_title or term in video_category or 
                            (term == 'drill' and 'drill' in video_title) or
                            (term == 'serve' and 'serve' in video_title) or
                            (term == 'forehand' and 'forehand' in video_title) or
                            (term == 'backhand' and 'backhand' in video_title) or
                            (term == 'volley' and ('volley' in video_title or 'net' in video_category))):
                            video_recommendations.append(video)
                    
                    # Limit to 3 video recommendations
                    if video_recommendations:
                        break
    
    # Then check enhanced resources with extracted content
    if 'resources' in knowledge_base and 'tennis_resources' in knowledge_base['resources']:
        for resource in knowledge_base['resources']['tennis_resources']:
            if resource.get('extracted_content'):
                # Check if query terms match resource content
                resource_content = (resource.get('Title', '') + ' ' + 
                                  resource.get('Key_Topics', '') + ' ' +
                                  resource.get('extracted_content', '')).lower()
                
                # Check for query term matches
                if any(term in resource_content for term in query_lower.split()):
                    relevant_info.append(f"\n--- {resource['Title'].upper()} ---")
                    relevant_info.append(resource['extracted_content'])
                    break  # Only include one resource to manage token limits
    
    return '\n'.join(relevant_info[:3000]), video_recommendations[:3]  # Return videos separately

def extract_web_content(url: str, title: str) -> str:
    """Extract content from web URL using simple HTTP request and OpenAI processing"""
    try:
        print(f"Extracting content from: {title}")
        
        # Try to fetch the webpage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return None
        
        # Get raw content
        raw_content = response.text[:10000]  # Limit to first 10k characters
        
        # Use OpenAI to process and extract key information
        extract_response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    "role": "system",
                    "content": """You are a tennis content extractor. Extract and summarize key tennis information from the provided web content. 
                    Focus on practical, actionable information useful for tennis coaching:
                    - Rules and regulations
                    - Technique and biomechanics
                    - Training methods and drills
                    - Strategy and tactics
                    - Fitness and conditioning
                    Structure your response with clear sections and bullet points. 
                    If there's no useful tennis content, return 'NO_TENNIS_CONTENT'."""
                },
                {
                    "role": "user", 
                    "content": f"Title: {title}\nURL: {url}\n\nExtract key tennis information from this content:\n\n{raw_content}"
                }
            ],
            max_tokens=1200
        )
        
        extracted_content = extract_response.choices[0].message.content.strip()
        
        if 'NO_TENNIS_CONTENT' in extracted_content:
            return None
            
        return extracted_content
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def enhance_knowledge_base_with_web_content():
    """Extract content from tennis resources and enhance knowledge base"""
    if not os.path.exists('knowledge_base/resources.json'):
        print("Resources file not found")
        return
        
    # Load existing resources
    with open('knowledge_base/resources.json', 'r') as f:
        resources_data = json.load(f)
    
    # Priority URLs to extract first
    priority_resources = [
        "ITF Rules of Tennis (2025)",
        "Tennis Strategy Booklet", 
        "USTA Sport Science: Biomechanical Analysis of the Tennis Volley",
        "ITF Conditioning: Fitness Training",
        "USTA High-School Sample Practice Plan"
    ]
    
    enhanced_resources = []
    
    for resource in resources_data.get('tennis_resources', []):
        title = resource['Title']
        url = resource['Source_URL']
        
        # Start with priority resources
        if title in priority_resources:
            print(f"Processing priority resource: {title}")
            extracted_content = extract_web_content(url, title)
            
            if extracted_content:
                resource['extracted_content'] = extracted_content
                print(f"✅ Successfully extracted content from: {title}")
            else:
                resource['extracted_content'] = None
                print(f"❌ Failed to extract content from: {title}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        else:
            resource['extracted_content'] = None
            
        enhanced_resources.append(resource)
    
    # Save enhanced resources
    enhanced_data = {'tennis_resources': enhanced_resources}
    with open('knowledge_base/resources_enhanced.json', 'w') as f:
        json.dump(enhanced_data, f, indent=2)
    
    print("Enhanced knowledge base saved to resources_enhanced.json")
    return enhanced_data

# Load knowledge base at startup
knowledge_base = load_knowledge_base()

# Try to load enhanced resources if available
if os.path.exists('knowledge_base/resources_enhanced.json'):
    with open('knowledge_base/resources_enhanced.json', 'r') as f:
        enhanced_resources = json.load(f)
        knowledge_base['resources'] = enhanced_resources
else:
    print("No enhanced resources found. Run enhance_knowledge_base_with_web_content() to create them.")

def get_conversation_history():
    """Get conversation history for current session"""
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
        session['conversation_history'] = [
            {
                "role": "system", 
                "content": """You are an experienced tennis coach with over 15 years of coaching experience. 
                You specialize in helping players of all skill levels improve their game. You provide:
                
                - Technical advice on strokes (forehand, backhand, serve, volley)
                - Strategy and tactics for singles and doubles play
                - Mental game coaching and confidence building
                - Fitness and conditioning tips specific to tennis
                - Equipment recommendations
                - Match preparation and analysis
                
                Keep your responses encouraging, practical, and tailored to the player's skill level. 
                Ask follow-up questions to better understand their needs and current abilities.
                
                When relevant knowledge base information is provided, use it to give detailed, accurate answers.
                Always cite specific techniques, drills, or recommendations from the knowledge base when available.
                
                IMPORTANT: Never mention video recommendations in your responses - the interface handles video suggestions separately. 
                Focus purely on tennis coaching advice, techniques, and written instructions.
                
                Format your responses with proper markdown including bold text for emphasis and clear structure."""
            }
        ]
    
    return session['conversation_history']

@app.route('/')
def index():
    return jsonify({'message': 'Tennis Coach API is running!'})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Check if OpenAI client is available
        if client is None:
            return jsonify({
                'response': '⚠️ Chat functionality is temporarily unavailable due to OpenAI configuration issues. However, video upload and analysis features are still working!',
                'videos': [],
                'success': True
            })
        
        # Get conversation history
        conversation_history = get_conversation_history()
        
        # Get relevant knowledge and videos for this query
        relevant_knowledge, recommended_videos = get_relevant_knowledge(user_message, knowledge_base)
        
        # Add user message
        conversation_history.append({"role": "user", "content": user_message})
        
        # If we have relevant knowledge, add it as context
        if relevant_knowledge:
            knowledge_message = {
                "role": "system",
                "content": f"Here is relevant knowledge base information to help answer the user's question:\n{relevant_knowledge}\n\nIMPORTANT: Do NOT mention any video recommendations in your response - videos are handled separately by the interface. Focus only on providing coaching advice and technical information."
            }
            messages_with_knowledge = conversation_history + [knowledge_message]
        else:
            messages_with_knowledge = conversation_history
        
        response = client.chat.completions.create(
            model='gpt-3.5-turbo-0125',
            messages=messages_with_knowledge
        )
        
        assistant_message = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": assistant_message})
        
        # Update session
        session['conversation_history'] = conversation_history
        
        return jsonify({
            'response': assistant_message,
            'videos': recommended_videos,
            'success': True
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history"""
    session.pop('conversation_history', None)
    session.pop('conversation_id', None)
    return jsonify({'success': True})

@app.route('/enhance-knowledge-base', methods=['POST'])
def enhance_kb():
    """Endpoint to trigger knowledge base enhancement"""
    try:
        result = enhance_knowledge_base_with_web_content()
        return jsonify({
            'success': True, 
            'message': 'Knowledge base enhancement completed',
            'enhanced_count': len([r for r in result['tennis_resources'] if r.get('extracted_content')])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Video analysis storage
video_analysis_results = {}
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_tennis_video(video_path, video_id):
    """Analyze tennis video using YOLO models"""
    try:
        print(f"Starting analysis for video: {video_id}")
        
        # Update status
        video_analysis_results[video_id]['status'] = 'analyzing'
        video_analysis_results[video_id]['progress'] = 20
        
        # Read video frames
        videoframes = read_video(video_path)
        print(f"Read {len(videoframes)} frames from video")
        video_analysis_results[video_id]['progress'] = 40
        
        # Initialize trackers
        player_tracker = PlayerTracker(model_path="yolov8x")
        ball_tracker = BallTracker(model_path="models/last.pt")
        court_line_detector = CourtLineDetector('training/keypoints_model.pth')
        
        video_analysis_results[video_id]['progress'] = 50
        
        # Detect players and balls
        print("Detecting players...")
        player_detections = player_tracker.detect_frames(videoframes, read_from_stub=False)
        print("Detecting balls...")
        ball_detections = ball_tracker.detect_frames(videoframes, read_from_stub=False)
        ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)
        
        video_analysis_results[video_id]['progress'] = 70
        
        # Detect court lines on first frame
        print("Detecting court lines...")
        court_keypoints = court_line_detector.predict(videoframes[0])
        
        # Filter players based on court position
        print("Filtering players...")
        player_detections = player_tracker.choose_and_filter_players(court_keypoints, player_detections)
        
        video_analysis_results[video_id]['progress'] = 85
        
        # Generate output video with annotations
        print("Drawing annotations...")
        output_video_frames = player_tracker.draw_bboxes(videoframes, player_detections)
        output_video_frames = ball_tracker.draw_bboxes(output_video_frames, ball_detections)
        output_video_frames = court_line_detector.draw_keypoints_on_video(output_video_frames, court_keypoints)
        
        # Save processed video
        output_path = f"{RESULTS_FOLDER}/{video_id}_processed.avi"
        print(f"Saving processed video to: {output_path}")
        save_video(output_video_frames, output_path)
        
        # Generate analysis results
        player_count = sum(len(frame_detections) for frame_detections in player_detections)
        ball_count = sum(len(frame_detections) for frame_detections in ball_detections if frame_detections)
        
        analysis_data = {
            'player_positions': player_count,
            'ball_detections': ball_count,
            'court_keypoints': len(court_keypoints) // 2,  # keypoints come in pairs (x,y)
            'total_frames': len(videoframes),
            'processed_video_path': output_path
        }
        
        print(f"Analysis complete: {analysis_data}")
        
        # Generate AI coaching feedback
        coaching_feedback = generate_tennis_coaching_feedback(analysis_data)
        
        # Update final results
        video_analysis_results[video_id].update({
            'status': 'completed',
            'progress': 100,
            'analysis': analysis_data,
            'coaching_feedback': coaching_feedback,
            'processed_video_url': f'/results/{video_id}_processed.avi'
        })
        
        print(f"Analysis completed for video: {video_id}")
        
    except Exception as e:
        print(f"Error analyzing video {video_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        video_analysis_results[video_id].update({
            'status': 'error',
            'error': str(e)
        })

def generate_tennis_coaching_feedback(analysis_data):
    """Generate AI coaching feedback from video analysis"""
    try:
        # Check if OpenAI client is available
        if client is None:
            return f"""
## 🎾 Tennis Video Analysis Complete!

**Technical Analysis Results:**
- Total frames analyzed: {analysis_data['total_frames']}
- Player positions detected: {analysis_data['player_positions']}
- Ball detections: {analysis_data['ball_detections']}
- Court keypoints detected: {analysis_data['court_keypoints']}

**Note:** AI coaching feedback is temporarily unavailable due to configuration issues, but your video has been successfully processed with computer vision analysis. You can see the annotated video with player tracking, ball detection, and court line analysis above.
"""
        feedback_prompt = f"""
        Based on this tennis video analysis data, provide detailed coaching feedback:
        
        - Total frames analyzed: {analysis_data['total_frames']}
        - Player positions detected: {analysis_data['player_positions']}
        - Ball detections: {analysis_data['ball_detections']}
        - Court keypoints detected: {analysis_data['court_keypoints']}
        
        As an expert tennis coach, analyze this data and provide:
        1. **Technical Assessment**: What the detection data tells us about the player's technique
        2. **Key Strengths**: Positive aspects observed in the movement patterns
        3. **Areas for Improvement**: Specific technique corrections needed
        4. **Practice Recommendations**: Drills to address identified issues
        5. **Next Steps**: What to focus on in future practice sessions
        
        Format your response with clear sections and actionable advice.
        """
        
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert tennis coach analyzing video data. Provide detailed, 
                    actionable feedback based on computer vision analysis results. Focus on technique 
                    improvement and practical coaching advice."""
                },
                {
                    "role": "user",
                    "content": feedback_prompt
                }
            ],
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating coaching feedback: {str(e)}"

@app.route('/upload-video', methods=['POST'])
def upload_video():
    """Upload and analyze tennis video"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload MP4, AVI, MOV, or MKV files.'}), 400
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        filename = secure_filename(f"{video_id}_{file.filename}")
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(RESULTS_FOLDER, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Initialize analysis status
        video_analysis_results[video_id] = {
            'status': 'uploaded',
            'progress': 0,
            'filename': filename,
            'upload_path': file_path
        }
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(
            target=analyze_tennis_video, 
            args=(file_path, video_id)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'message': 'Video uploaded successfully. Analysis started.',
            'status': 'processing'
        })
        
    except Exception as e:
        print(f"Error in video upload: {str(e)}")
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500

@app.route('/video-analysis/<video_id>', methods=['GET'])
def get_video_analysis(video_id):
    """Get video analysis status and results"""
    if video_id not in video_analysis_results:
        return jsonify({'success': False, 'error': 'Video not found'}), 404
    
    result = video_analysis_results[video_id]
    return jsonify({
        'success': True,
        'video_id': video_id,
        **result
    })

@app.route('/results/<filename>')
def serve_result_video(filename):
    """Serve processed video files"""
    return send_from_directory(RESULTS_FOLDER, filename)

if __name__ == '__main__':
    print("🎾 Starting Tennis Coach Web App...")
    print("Visit http://localhost:4000 to start coaching!")
    app.run(debug=True, host='0.0.0.0', port=4000)