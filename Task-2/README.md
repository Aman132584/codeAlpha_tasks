
# AI Music Generation

Generates new piano music by training an LSTM neural network on MIDI files.

## How it works

1. Reads `.mid` files and extracts notes/chords using `music21`
2. Converts them into numbered sequences the model can learn from
3. Trains an LSTM model to predict the next note in a sequence
4. Uses the trained model to generate a brand new sequence
5. Converts that sequence back into a playable `.mid` file

## Setup

```
pip install music21 tensorflow numpy
```

## Project structure

```
music_gen/
├── music_generation.py
└── midi_songs/
    ├── song1.mid
    ├── song2.mid
    └── ...
```

Place your training `.mid` files directly inside a `midi_songs` folder next to the script.

## Usage

```
python music_generation.py
```

- First run: extracts notes, trains the model, saves `music_model.h5`, then generates music
- Later runs: reuses the saved model and notes instead of retraining
- Output: `generated_output.mid`

## Notes

- Delete `notes.pkl` if you add/change MIDI files, so they get re-processed
- Delete `music_model.h5` to force retraining
- Training on CPU can take a while; more MIDI files and more epochs generally improve output quality
- Open `generated_output.mid` with any media player, DAW, or VLC to listen
