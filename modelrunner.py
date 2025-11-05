from utils import save_video, read_video
from trackers import PlayerTracker, BallTracker
from court_detector import CourtLineDetector
def main():
    input = 'testingvideos/input_video.mp4'
    videoframes = read_video(input)

    player_tracker = PlayerTracker(model_path = "yolov8x")
    ball_tracker = BallTracker(model_path = "models/last.pt")
    player_detections = player_tracker.detect_frames(videoframes, read_from_stub=False, stub_path= "trackers_stubs/player_detections.pkl")
    ball_detections = ball_tracker.detect_frames(videoframes, read_from_stub=False, stub_path= "trackers_stubs/ball_detections.pkl")
    ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)

    court_line_path = 'training/keypoints_model.pth'
    court_line_detector = CourtLineDetector(court_line_path)
    court_keypoints = court_line_detector.predict(videoframes[0])

    player_detections = player_tracker.choose_and_filter_players(court_keypoints, player_detections)

    output_video_frames = player_tracker.draw_bboxes(videoframes, player_detections)
    output_video_frames = ball_tracker.draw_bboxes(videoframes, ball_detections)

    output_video_frames = court_line_detector.draw_keypoints_on_video(output_video_frames, court_keypoints)

    save_video(output_video_frames, "outputvideos/output.avi")

if __name__ == "__main__":
    main()


