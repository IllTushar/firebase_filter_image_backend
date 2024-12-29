from moviepy.video.io.VideoFileClip import VideoFileClip


def create_gif_from_video(video_path, gif_output_path, start_time=None, end_time=None, resize_factor=1.0):
    # Load the video file
    video = VideoFileClip(video_path)

    # Optional: Trim the video
    if start_time or end_time:
        try:
            video = video.subclip(start_time, end_time)  # Use subclip
        except AttributeError:
            video = video.subclipped(start_time, end_time)  # Use subclipped if subclip is unavailable
        except AttributeError:
            video = video.set_start(start_time).set_end(end_time)  # Fallback method

    # Optional: Resize the video
    if resize_factor != 1.0:
        video = video.resized(resize_factor)

    # Export the video as a GIF
    video.write_gif(gif_output_path, fps=10)


if __name__ == '__main__':
    # Usage Example
    create_gif_from_video(
        video_path=r"C:\Users\gtush\Videos\VID_20240410_175651.mp4",
        gif_output_path=r"C:\Users\gtush\Videos\output.gif",
        start_time=2,  # Start at 2 seconds
        end_time=6,  # End at 8 seconds
        resize_factor=0.5  # Resize to 50% of the original
    )
