import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor

def convert_to_webp(
    image_path,
    output_folder="webp_images",
    error_log="webp_error_log.txt"
  ):
  """
  Converts a single image to WebP format using cwebp.

  Args:
    image_path: The path to the image file.
    output_folder: The folder to save the converted WebP image.
    error_log: The name of the error log file.
  """
  try:
    # Create the output folder if it doesn't exist.
    if not os.path.exists(output_folder):
      os.makedirs(output_folder)

    # Construct the output path for the WebP image.
    filename, ext = os.path.splitext(os.path.basename(image_path))
    output_path = os.path.join(output_folder, f"{filename}.webp")

    # Use cwebp to convert the image.
    subprocess.run(
      ["cwebp", image_path, "-o", output_path],  # Call to cwebp.
      check=True,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL
    )

  except subprocess.CalledProcessError as e:
    # Log the error to the error log file.
    with open(error_log, "a") as log_file:
      log_file.write(f"Error converting {image_path}: {e}\n")

def convert_images_to_webp(
    image_folder,
    output_folder="webp_images",
    max_threads=8,
    error_log="webp_error_log.txt"
  ):
  """
  Converts all images in a folder to WebP format using multiple threads.

  Args:
    image_folder: The path to the folder containing the images.
    output_folder: The folder to save the converted WebP images.
    max_threads: The maximum number of threads to use.
    error_log: The name of the error log file.
  """
  image_paths = [
      os.path.join(image_folder, f)
      for f in os.listdir(image_folder)
      if os.path.isfile(os.path.join(image_folder, f)) and 
      f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
  ]

  total_images = len(image_paths)
  converted_images = 0

  # Use a ThreadPoolExecutor to manage threads
  with ThreadPoolExecutor(max_workers=max_threads) as executor:
    for _ in executor.map(
      convert_to_webp,
      image_paths,
      [output_folder] * total_images,
      [error_log] * total_images
    ):
      converted_images += 1
      print(
        f"Converted {converted_images} of {total_images} images...",
        end="\r"
      )

  print(
    f"Converted {converted_images} of {total_images} images. " + 
    f"Errors logged to {error_log}."
  )

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Convert images in a folder to WebP format."
  )
  parser.add_argument(
      "image_folder", 
      help="Path to the folder containing images."
  )
  parser.add_argument(
      "-o", "--output", 
      default="webp_images", 
      help="Output folder name (default: webp_images)."
  )
  parser.add_argument(
      "-t", "--threads", 
      type=int, 
      default=8, 
      help="Maximum number of threads (default: 8)."
  )
  args = parser.parse_args()

  convert_images_to_webp(args.image_folder, args.output, args.threads)