from moviepy import VideoFileClip

clip = VideoFileClip("entities_shell.mp4")  # replace with your actual path

# Optional: trim clip if desired
# clip = clip.subclip(2, 6)

# Resize correctly (MoviePy uses `resize`, not `resized`)
# clip = clip.resize(width=600)

# Export as GIF
clip.write_gif("advanced_shell.gif", fps=15)  # Adjust FPS for file size vs. smoothness
