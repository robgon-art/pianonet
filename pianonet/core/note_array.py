import pickle
import joblib
import random

import numpy as np

from pianonet.core.misc_tools import get_hash_string_of_numpy_array


class NoteArray(object):
    """
    A NoteArray is a 1D stream of piano note states derived from flattening a pianoroll. The notearray is useful
    for training a 1D convolutional neural net. The given pianoroll can be down-sampled to lower resolution before
    flattening. Also, most keys in pianorolls are always or nearly always zero, usually the highest and lowest keys.
    This is why cropping high and low keys of the input pianoroll is supported.

    Example array:

    timestep = 0                 timestep = 1
     A  A# B  C  C# D  D# E  ... A  A# B  C  C# D  D# E  ...
    [0, 0, 0, 1, 0, 0, 0, 0, ... 1, 0, 0, 1, 0, 0, 0, 0, ...]
    """

    def __init__(self, pianoroll=None, flat_array=None, file_path=None, note_array_transformer=None):
        """
        pianoroll: Instance of Pianoroll class used to populate the notearray's array
        flat_array: Optionally can initialize from a 1D array of note states. **This 1D array is assumed to already
                    be cropped and downsampled at the specified parameters given to this constructor**
        file_path: Optionally can initialize from a NoteArray instance that was saved to file.
        note_array_transformer: NoteArrayTransformer instance for converting a pianoroll or flat array into a NoteArray
        """

        if file_path != None:
            self.load(file_path=file_path)
        else:
            self.note_array_transformer = note_array_transformer

            pianoroll_is_defined = (pianoroll != None)
            flat_array_is_defined = isinstance(flat_array, np.ndarray)

            if pianoroll_is_defined and flat_array_is_defined:
                raise Exception("Cannot use both a pianoroll and flat_array initializer. Choose one.")

            elif pianoroll_is_defined:
                self.array = self.note_array_transformer.get_flat_array_from_pianoroll(pianoroll=pianoroll)

            elif flat_array_is_defined:
                self.note_array_transformer.validate_flat_array(flat_array)
                self.array = flat_array.copy()

            else:
                raise Exception("Neither a pianoroll nor a flat_array initializer has been provided.")

    def get_pianoroll(self):
        """
        Recover the original pianoroll as high of fidelity as possible given the initial down-sampling and cropping.
        A Pianoroll instance is returned.
        """

        return self.note_array_transformer.get_pianoroll_from_flat_array(flat_array=self.array)

    def get_length_in_notes(self):
        """
        Returns as an integer the length of the stored 1D array
        """

        return self.array.shape[0]

    def get_length_in_timesteps(self):
        """
        Returns as an integer the length of the note array in timesteps
        """

        return (self.get_length_in_notes() // self.note_array_transformer.num_keys)

    def play(self):
        """
        Reformats as pianoroll then plays as midi.
        """

        self.get_pianoroll().play()

    def get_note_array_from_random_segment_of_time_steps(self, num_time_steps):
        """
        Returns a NoteArray that has data that is a random segment num_time_steps in length.

        num_time_steps: Integer denoting how many time steps of data should be returned
        """

        if num_time_steps > self.get_length_in_timesteps():
            raise Exception("Number of requested time steps is longer than the note array")

        if not isinstance(num_time_steps, int):
            raise Exception("Number of requested time steps should be an integer. Instead got " + str(num_time_steps))

        max_ending_time_step = self.get_length_in_timesteps() - num_time_steps

        starting_time_step = random.randint(0, max_ending_time_step)
        starting_note_index = starting_time_step * self.note_array_transformer.num_keys
        ending_note_index = starting_note_index + num_time_steps * self.note_array_transformer.num_keys

        array = self.array[starting_note_index:ending_note_index]

        return self.note_array_transformer.get_note_array(flat_array=array)

    def get_values_in_range(self, start_index, end_index, use_zero_padding_for_out_of_bounds=False):
        """
        start_index: Start index of desired note array values (can be None for empty part of slice)
        end_index: End index (non-inclusive) of desired note array values (can be None for empty part of slice)
        use_zero_padding_for_out_of_bounds: If true, zeros are returned for those indices in the range that are
                                            out of bounds. Must be false if either start or end indices are None
        """

        if use_zero_padding_for_out_of_bounds:
            pad_count_at_start = 0
            pad_count_at_end = 0

            bounded_start_index = max(start_index, 0)
            bounded_end_index = min(end_index, self.get_length_in_notes())

            values = self.array[bounded_start_index:bounded_end_index]

            if start_index < 0:
                pad_count_at_start = abs(start_index)

            if end_index > self.get_length_in_notes():
                pad_count_at_end = end_index - self.get_length_in_notes()

            if (pad_count_at_start + pad_count_at_end) > 0:
                values = np.pad(array=values,
                                pad_width=(pad_count_at_start, pad_count_at_end),
                                mode='constant').astype('bool')
        else:
            values = self.array[start_index:end_index]

        return values

    def get_hash_string(self):
        """
        Returns a hash of the data contained in self.array. This is useful for verifying that two note arrays are
        indeed the same.
        """

        return get_hash_string_of_numpy_array(self.array)

    def save(self, file_path):
        """
        file_path: Path indicating where on disc to save the NoteArray instance.

        Saves the NoteArray instance to a file.
        """

        if file_path.find('.mna_jl') != -1:
            joblib.dump(self, file_path)
        else:
            with open(file_path, 'wb') as file:
                pickle.dump(self, file=file)

    def load(self, file_path):
        """
        file_path: Path indicating from where on disc to load the NoteArray instance.

        Loads the NoteArray instance from a file.
        """

        loaded_instance = None

        if file_path.find('.mna_jl') != -1:
            loaded_instance = joblib.load(file_path)
        else:
            with open(file_path, 'rb') as file:
                loaded_instance = pickle.load(file)

        self.__dict__ = loaded_instance.__dict__
