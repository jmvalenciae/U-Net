# U-Net network to segment seeds

A neural network designed to segmentate 3 different classes, by default it was
thought to segmentate germinated seeds, no germinated seeds and the background

The principal scripts are:
* augmentation.py
* train.py
* make\_TFrecords.py
* predict.py

# Usage

## Install the requierements with pip

```shell
pip install requirements.txt
```

Run the following command in order to create two directories, one for the
tfrecords and other for the weights, which will be used later:

```shell
mkdir weights tfrecords
```

You might as well use different names or paths for this directories as long as
you specify them correctly in the following commands.


## (Optional) Data augmentation

It is possible to perform data augmentation before training. It applies some
random transformations to the input images such as rotations, crops and
shiftings.

Run:

```shell
python3 augmentation.py --img_path=INPUT IMAGES DIRECTORY --masks_path=MASKS PATH --augmented_path=PATH TO SAVE THE NEW DATASET --labels=LABELS DIRECTORY --n_images=NUMBER OF IMAGES TO GENERATE
```
By default `img_path` is set to `./DatasetE2/JPEGImages` , `masks_path` to
`./DatasetE2/SegmentationClass` , `labels` to `./DatasetE2/labelmap.txt` and
`n_images` to `192` 

The script generates a number of images multiple of 32 as closest as possible to
`n_images`.

The default for `augmented_path` is `None`, the script automatically creates a
new directory in the working directory with the results named `AugmentedDataset`
if left unspecified.

## Prepare the dataset

Before training, you must first create two tfrecords files using the script
make_TFrecords.py:

```shell
python3 make_TFrecords.py --img_path=INPUT IMAGES DIRECTORY --mask_path=LABEL IMAGES DIRECTORY --labels=LABELS DIRECTORY --tfrecord_path=PATH OF TFRECORDS --val_size= VALIDATION PARTITION
```

Make sure to replace with your corresponding paths and values. The defaults are: 
`val_size=0.2`, `tfrecord_path=./tfrecords/`,
`img_path=./seeds_data/JPEGImages/`,
`mask_path=./seeds_data/SegmentationClass/`,`labels=labelmap.txt`.

For example:

```shell
python3 make_TFrecords.py --img_path=../input/tomatoseedsdatasetjm/JPEGImages/ --mask_path=../input/tomatoseedsdatasetjm/SegmentationClass/ --labels=../input/tomatoseedsdatasetjm/labelmap.txt
```
## Train

Use the following command in order to train the model:

```shell
python3 train.py --train_Dataset=PATH TO THE TFRECORDS OF TRAINING DATA --val_Dataset=PATH TO TFRECORDS --weights=PATH TO WEIGHTS --buffer_size=BUFFER SIZE --batch_size=BATCH SIZE --epochs=EPOCHS --save_freq=SAVE FREQUENCY OF EPOCHS
```

The defaults for train_Dataset, val_Dataset and weights are the same as stated
before. The defaults the other FLAGS are: `buffer_size=100` , `batch_size=5` ,
`epochs=10`, `save_freq=5`

## Prediction

In order to do the prediction of an image run the following command:

```shell
python3 predict.py --image_path=IMAGE PATH --mask_path=MASK PATH --labels=LABELS PATH --show_results=True --weights=WEIGHTS PATH
```
In this case, weights is not the directory, but the specific file from the
weights we want to use to make the prediciton. mask_path is the path were the
predicted mask should be saved (None by default) (Recommended file extension:
png).

It is also possible to count the amount of germinated and no germinated seeds in
a true or predicted mask. To do this, simply run:

```shell
python3 count.py [MASK] [LABELS]
```
This will print the amount of germinated and no germinated seeds

## Check the performance
To see how good the prediction was use measure.py, it will print the dice and
jaccard indexes of the prediction respect to the mask.

Run:

```shell
python3 measure.py [TRUEMASK] [PREDMASK] [LABELS]
```

