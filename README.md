# PianoNet
## About
PianoNet is a deep neural network for generating piano compositions. The model architectures are similar to the dilated convolutional networks described in [WaveNet](https://arxiv.org/abs/1609.03499), with modifications for being able to handle piano midi data. These modifications are necessary, as piano notes are a time series of key states (2-dimensional), rather than 1-dimensional samples like the audio used to train WaveNet.

For an example performance generated by a medium-sized model, visit PianoNet's [SoundCloud page](https://soundcloud.com/tom-angsten)

## Features
* Build a generative piano model in minutes, train in a few days on a modern laptop
* Queue-based generation algorithm removing redundant convolution operations for lightning-fast piano performances
* Framework for easy experimentation using file-based interface for finding the optimal model architecture
* Clear logging of training results for tracking of training history
* Object-oriented abstraction of data components for painless dataset creation from raw midi files

## Installation
1. Clone this repository to a local directory
2. `cd` into the cloned directory
3. Create a [python virtualenv](https://docs.python.org/3/library/venv.html) in this directory using `python -m venv ./`
4. Activate the virtualenv using `source ./venv/bin/activate`
5. Run `python setup.py install`
6. Run `pip install -r requirements.txt`

## Example Usage

An end-to-end example, from dataset creation to performance generation, can be found in the examples/pianonet_mini directory. Here are the steps to run this example:

### Training the Model

1. Navigate to the example directory with `cd examples/pianonet_mini`
2. To create the training and validation datasets, run `python ../../pianonet/scripts/master_note_array_creation.py ./dataset_creation_description.json ./`
3. To initiate training, run `python ../../pianonet/scripts/runner.py ./` In a separate terminal in the same directory, you can run `tail -n 10000 -f output_train.log` to monitor the training loss in real time. After ten epochs, the trained model will be located at `./models/0_trained`
4. If you optionally wish to further train the model, re-run the command in the above step. This will concatenate output to output_train.log as before, and the new model will be checkpointed at `./models/1_trained`

### Generating Performances

1. Within the `examples/pianonet_mini` directory, run the command `jupyter notebook` This should start a notebook server and open a local file tree within your directory. Click on the notebook file named `get_performances.ipynb`
2. Once you've opened the notebook, run the cells in order and read the important notes in each cell. You will be able to listen to model performances and save perfromances you like as midi files.
3. If things don't sound as good as you would like, either train longer or add more data by scraping midi files from the internet. 

Enjoy, and please report any issues you run into!
