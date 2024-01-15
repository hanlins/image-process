# Image processing script

Image processor is a script to print metadata to the image.
The script will add margin, add logo and print out the parameters for the image.
It will also lower the resolution so it would be easier to share and protect the copyright of the image.

## Dependencies

Install pillow package:
```bash
pip install --upgrade Pillow
```
## Usage

Run following command to process the images in the specified directory in batch:
```bash
python process.py <directory-name>
```
The script will create an `output` directory in the specified directory and put the generated images there.

## Results

Here's the showcase for some of the processed images:
![Horizontal image](./image/DSCF0157.JPG)
The above image is a show case for horizontally aligned photo.

![Vertical image](./image/DSCF0204.JPG)
The above image is a show case for vertically aligned photo.

