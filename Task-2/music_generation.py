import os
import glob
import pickle
import numpy as np
from music21 import converter, instrument, note, chord, stream
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import to_categorical

DATA_DIR = "midi_songs"
SEQUENCE_LENGTH = 100
MODEL_PATH = "music_model.h5"
NOTES_PATH = "notes.pkl"
OUTPUT_MIDI = "generated_output.mid"


def extract_notes(data_dir):
    notes = []
    for file in glob.glob(os.path.join(data_dir, "*.mid")):
        midi = converter.parse(file)
        parts = instrument.partitionByInstrument(midi)
        elements = parts.parts[0].recurse() if parts else midi.flat.notes

        for element in elements:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes.append(".".join(str(n) for n in element.normalOrder))

    with open(NOTES_PATH, "wb") as f:
        pickle.dump(notes, f)

    return notes


def prepare_sequences(notes, sequence_length=SEQUENCE_LENGTH):
    pitch_names = sorted(set(notes))
    note_to_int = {n: i for i, n in enumerate(pitch_names)}

    network_input = []
    network_output = []

    for i in range(len(notes) - sequence_length):
        seq_in = notes[i:i + sequence_length]
        seq_out = notes[i + sequence_length]
        network_input.append([note_to_int[n] for n in seq_in])
        network_output.append(note_to_int[seq_out])

    n_patterns = len(network_input)
    n_vocab = len(pitch_names)

    X = np.reshape(network_input, (n_patterns, sequence_length, 1))
    X = X / float(n_vocab)
    y = to_categorical(network_output, num_classes=n_vocab)

    return X, y, pitch_names, note_to_int, n_vocab


def build_model(input_shape, n_vocab):
    model = Sequential()
    model.add(LSTM(512, input_shape=input_shape, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512))
    model.add(BatchNormalization())
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation("softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="adam")
    return model


def train(model, X, y, epochs=100, batch_size=64):
    checkpoint = ModelCheckpoint(
        MODEL_PATH, monitor="loss", verbose=1,
        save_best_only=True, mode="min"
    )
    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=[checkpoint])


def generate_notes(model, network_input, pitch_names, n_vocab, num_notes=200):
    int_to_note = {i: n for i, n in enumerate(pitch_names)}
    start = np.random.randint(0, len(network_input) - 1)
    pattern = list(network_input[start])
    prediction_output = []

    for _ in range(num_notes):
        input_seq = np.reshape(pattern, (1, len(pattern), 1))
        input_seq = input_seq / float(n_vocab)

        prediction = model.predict(input_seq, verbose=0)
        index = np.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1:]

    return prediction_output


def create_midi(prediction_output, output_path=OUTPUT_MIDI):
    offset = 0
    output_notes = []

    for pattern in prediction_output:
        if "." in pattern or pattern.isdigit():
            chord_notes = pattern.split(".")
            notes_in_chord = []
            for current_note in chord_notes:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes_in_chord.append(new_note)
            new_chord = chord.Chord(notes_in_chord)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        offset += 0.5

    midi_stream = stream.Stream(output_notes)
    midi_stream.write("midi", fp=output_path)


def main():
    if os.path.exists(NOTES_PATH):
        with open(NOTES_PATH, "rb") as f:
            notes = pickle.load(f)
    else:
        notes = extract_notes(DATA_DIR)

    X, y, pitch_names, note_to_int, n_vocab = prepare_sequences(notes)

    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
    else:
        model = build_model((X.shape[1], X.shape[2]), n_vocab)
        train(model, X, y)

    network_input = [
        [note_to_int[n] for n in notes[i:i + SEQUENCE_LENGTH]]
        for i in range(len(notes) - SEQUENCE_LENGTH)
    ]

    generated = generate_notes(model, network_input, pitch_names, n_vocab)
    create_midi(generated)
    print(f"Generated MIDI saved to {OUTPUT_MIDI}")


if __name__ == "__main__":
    main()
