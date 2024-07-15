Learning action verbs. Basic concept idea from Total Physical Response (TPR). Using Hebrew verbs as an example. The user physically acts out each action verb as they are displayed in order to learn new vocabulatry.

## Features

- Display of images and playback of audio files for Hebrew verbs
- Random selection of verbs with customizable display time
- Option to replay audio
- Menu options for changing settings, including display time and repeat count
- Easy-to-use graphical interface built with Tkinter

## Requirements

- Python 3.x
- Tkinter
- Pillow
- Pygame

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/TPR-Game.git
   cd TPR-Game
   ```

2. **Install the required Python packages:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Prepare the resources:**
   - Create a directory named `milim` in the project root.
   - Inside the `milim` directory, add subdirectories for each category of verbs.
   - Place image files (`.png`, `.jpg`, `.jpeg`, `.gif`) and audio files (`.mp3`) in the respective subdirectories.

4. **Configure settings:**
   - Create a `settings.txt` file in the project root with the following format:
     ```
     display_time=2500
     repeat_count=1
     ```

## Usage

1. **Run the application:**
   ```sh
   python app.py
   ```

2. **Setup the game:**
   - Choose a directory to load resources from.
   - Set the display time in milliseconds and the repeat count.

3. **Interacting with the game:**
   - The game will automatically display images and play corresponding audio files.
   - Press the "Replay Audio" button or the spacebar to replay the current audio.
   - Use the File menu to change settings or exit the application.
   - Press 'q' to return to the main menu or 't' to change the display time.

## Contributing

Contributions are welcome! Please create an issue to discuss the changes you want to make before submitting a pull request.

## Acknowledgments

- TPR Game was developed by Jeremy Steinberg.
- Special thanks to the open-source community for providing the tools and libraries used in this project.
