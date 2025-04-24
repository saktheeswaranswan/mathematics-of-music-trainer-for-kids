import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.widgets import Button
import time
import threading

# Initialize pygame for sound
pygame.mixer.init()

# Generate a 440 Hz sine wave sound for the click and note
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sine_wave = np.sin(2 * np.pi * frequency * t)
    # Normalize the wave to the range [-32767, 32767] for 16-bit sound
    sine_wave = np.int16(sine_wave * 32767)
    
    # Convert to stereo (2 channels)
    stereo_wave = np.column_stack((sine_wave, sine_wave))
    
    return pygame.sndarray.make_sound(stereo_wave)

# Create sound objects
click_sound = generate_sine_wave(440, 0.1)  # 440 Hz for the click sound (0.1 seconds)
note_sound = generate_sine_wave(440, 0.5)  # 440 Hz for the note sound (0.5 seconds)

# Table data for musical notes/rests
table_data = [
    ["Whole Note", "♩̄", 4],
    ["Whole Rest", "𝄻", 4],
    ["Half Note", "♫", 2],
    ["Half Rest", "𝄼", 2],
    ["Quarter Note", "♩", 1],
    ["Quarter Rest", "𝄽", 1],
    ["Eighth Note", "♪", 0.5],
    ["Eighth Rest", "𝄾", 0.5],
    ["Sixteenth Note", "♬", 0.25],
    ["Sixteenth Rest", "𝄿", 0.25],
    ["32nd Note", "𝄪", 0.125],
    ["32nd Rest", "𝄬", 0.125]
]

bpm_options = [120, 160, 2000]
current_bpm = 120
is_playing = False  # Flag to control background playback

# Calculate cell width and height for the grid
cell_width = 100
cell_height = 50
grid_offset_x = 150  # Offset to make room for BPM controls

# Function to update the BPM
def set_bpm(bpm):
    global current_bpm
    current_bpm = bpm

# Function to play a note or rest sound
def play_sound(note_symbol, beats):
    duration = (60 / current_bpm) * beats  # Calculate duration based on BPM
    if "Rest" not in note_symbol:
        note_sound.play(maxtime=int(duration * 1000))  # Play note sound for duration
    else:
        pygame.time.delay(int(duration * 1000))  # Wait for duration for rest

# Function to handle button clicks
def on_bpm_button_click(event, bpm):
    set_bpm(bpm)
    click_sound.play()  # Play click sound for feedback

# Background playback loop to continuously play beats
def play_background_loop():
    global is_playing
    while is_playing:
        for i, (name, symbol, beats) in enumerate(table_data):
            for j, bpm in enumerate(bpm_options):
                duration = (60 / current_bpm) * beats
                if "Rest" not in symbol:
                    note_sound.play(maxtime=int(duration * 1000))  # Play note sound for duration
                else:
                    pygame.time.delay(int(duration * 1000))  # Wait for duration for rest
                time.sleep(duration)  # Delay for each note/rest
            time.sleep(0.1)  # Small delay between repetitions of the whole loop

# Create the plot and grid
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, len(bpm_options) + 2)
ax.set_ylim(0, len(table_data) + 1)

# Set the number of x-ticks equal to the number of BPM options
ax.set_xticks(np.arange(2, len(bpm_options) + 2))  # Start at 2, matching the number of BPM options
ax.set_xticklabels([f'{bpm} BPM' for bpm in bpm_options], rotation=45)

ax.set_yticks(np.arange(1, len(table_data) + 1))
ax.set_yticklabels([f'{item[0]} {item[1]}' for item in table_data])

# Draw the grid for notes/rests
for i, (name, symbol, beats) in enumerate(table_data):
    for j, bpm in enumerate(bpm_options):
        ax.add_patch(plt.Rectangle((j + 2, len(table_data) - 1 - i), 1, 1, fill=False, color='black'))
        ax.text(j + 2.5, len(table_data) - 1 - i + 0.5, f"{(60 / bpm) * beats:.3f}s", ha='center', va='center')

# Add BPM buttons
button_width = 0.2
button_height = 0.1
button_y = 0.8

buttons = []
for i, bpm in enumerate(bpm_options):
    button = Button(plt.axes([0.85, button_y - i * button_height, button_width, button_height]), f'{bpm} BPM')
    button.on_clicked(lambda event, bpm=bpm: on_bpm_button_click(event, bpm))
    buttons.append(button)

# Function to handle mouse click on the grid
def on_click(event):
    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return

    # Detect the grid cell that was clicked
    row = int(len(table_data) - y - 1)
    col = int(x - 2)

    if 0 <= row < len(table_data) and 0 <= col < len(bpm_options):
        note_symbol = table_data[row][1]
        beats = table_data[row][2]
        play_sound(note_symbol, beats)

# Connect the click event
fig.canvas.mpl_connect('button_press_event', on_click)

# Start the background playback in a separate thread
def start_background_playback():
    global is_playing
    is_playing = True
    background_thread = threading.Thread(target=play_background_loop)
    background_thread.daemon = True  # Allow the thread to close when the main program exits
    background_thread.start()

# Start background playback when the application runs
start_background_playback()

plt.show()

