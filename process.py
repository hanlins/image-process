import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ExifTags


def process_photo(input_path, output_path, margin_size, logo_path, target_resolution):
    # Open the image
    img = Image.open(input_path)

    # Extract metadata
    exif_raw = img.info["exif"]
    exif_data = {}
    try:
        for tag, value in img._getexif().items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            exif_data[tag_name] = value
    except AttributeError:
        pass

    orientation = exif_data.get("Orientation", 1)
    if orientation == 8:
        img = img.rotate(90, expand=True)
    elif orientation == 6:
        img = img.rotate(-90, expand=True)

    # Add margin
    footer_size = 800
    img = add_margin(img, margin_size, footer_size)

    # Add logo aligned at the middle bottom
    img = add_logo(img, logo_path)

    # Add metadata as text to the right of the logo
    img = add_metadata_text(img, exif_data, margin_size, footer_size)

    # Lower resolution
    img = resize_image(img, target_resolution)

    if orientation == 8:
        img = img.rotate(-90, expand=True)
    elif orientation == 6:
        img = img.rotate(90, expand=True)

    # Save the processed image
    img.save(output_path, exif=exif_raw)


def add_margin(img, margin_size, footer_size):
    width, height = img.size
    new_width = width + 2 * margin_size
    new_height = height + 2 * margin_size + footer_size

    new_img = Image.new("RGB", (new_width, new_height), "white")
    new_img.paste(img, (margin_size, margin_size))

    return new_img


def add_logo(img, logo_path):
    logo = Image.open(logo_path)

    # Create a mask for the logo
    logo_mask = logo.convert("L").point(lambda x: 255 if x > 0 else 0)

    # Align logo at the middle bottom
    x_offset = (img.width - logo.width) // 2
    y_offset = img.height - logo.height
    img.paste(logo, (x_offset, y_offset), logo_mask)

    return img


def trim_printable(s):
    for i, c in enumerate(s):
        if not c.isprintable():
            s = s[:i]
            break
    return s


def add_metadata_text(img, exif_data, margin_size, footer_size):
    draw = ImageDraw.Draw(img)
    fsize = (img.width if img.width < img.height else img.height) // 75
    font = ImageFont.truetype("fonts/HackNerdFontMono-Regular.ttf", size=fsize)

    # Text position to the right of the logo
    text_position = (margin_size * 2, img.height - footer_size)

    params = {}
    shutter_speed = exif_data.get("ExposureTime", "N/A")
    aperture = exif_data.get("FNumber", "N/A")
    iso = exif_data.get("ISOSpeedRatings", "N/A")
    focal_length = exif_data.get("FocalLength", "N/A")

    if shutter_speed != "N/A":
        if shutter_speed < 1.0:
            shutter_speed = f"1/{int(1/shutter_speed)}s"
        elif shutter_speed > 1.0:
            shutter_speed = f"{shutter_speed}s"
        params["shutter"] = shutter_speed
    if aperture != "N/A":
        params["aperture"] = f"F{aperture}"
    if iso != "N/A":
        params["iso"] = f"{iso}"
    if focal_length != "N/A":
        params["focal length"] = f"{focal_length}mm"

    maxl = 0
    for k, v in params.items():
        maxl = max(maxl, len(k) + len(v))

    # Draw metadata as text
    metadata_text = ""
    for k, v in params.items():
        metadata_text += f"{k}  {(maxl - len(k) - len(v)) * ' '}{v}\n"

    # add timestamp
    timestamp = exif_data.get("DateTimeOriginal", "N/A")
    # replace the first two ':' with /
    timestamp = timestamp.replace(":", "/", 2)
    metadata_text += f"\ndate {timestamp}\n"
    # print(metadata_text)
    draw.text(text_position, metadata_text, font=font, fill="black")

    dev_info = {}
    dev_info["camera make"] = exif_data.get("Make", "N/A")
    dev_info["camera model"] = exif_data.get("Model", "N/A")
    dev_info["lens make"] = trim_printable(exif_data.get("LensMake", "N/A"))
    dev_info["lens model"] = trim_printable(exif_data.get("LensModel", "N/A"))
    maxl = 0
    for k, v in dev_info.items():
        maxl = max(maxl, len(k) + len(v))
    text_position = (
        img.width - maxl * fsize * 0.7 - margin_size,
        img.height - footer_size,
    )

    devinfo_text = ""
    for k, v in dev_info.items():
        devinfo_text += f"{k}  {(maxl - len(k) - len(v)) * ' '}{v}\n"
    draw.text(text_position, devinfo_text, font=font, fill="black")
    return img


def resize_image(img, target_resolution):
    img.thumbnail(target_resolution)
    return img


# Example usage
input_photo = "input2.jpg"
output_photo = "output_processed.jpg"
logo_path = "logo.jpg"
margin_size = 50
target_resolution = (2000, 2000)


def batch_process(dir):
    # iterate files in dir
    output_dir = os.path.join(dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for f in os.listdir(dir):
        if f.endswith(".JPG"):
            input_path = os.path.join(dir, f)
            output_path = os.path.join(output_dir, f)
            process_photo(
                input_path, output_path, margin_size, logo_path, target_resolution
            )


def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Process the photos in the specified directory"
    )

    # Add a positional argument for the directory path
    parser.add_argument("directory_path", type=str, help="Path to the directory")

    # Parse the command line arguments
    args = parser.parse_args()

    # batch_process(args.directory_path)
    print(args.directory_path)


if __name__ == "__main__":
    main()
