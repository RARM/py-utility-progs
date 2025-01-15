import requests
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException
import argparse
import time

def download_image(url, folder_name="images", error_log="error_log.txt"):
  """
  Downloads a single image from a URL and saves it to a local folder.
  Logs errors to an error log file.

  Args:
    url: The URL of the image.
    folder_name: The name of the folder to save the image to.
    error_log: The name of the error log file.
  """
  try:
    # Get the filename from the URL.
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # Download the image.
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Save the image to the folder.
    filepath = os.path.join(folder_name, filename)
    with open(filepath, 'wb') as file:
      for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

  except RequestException as e:
    # Log the error to the error log file.
    with open(error_log, "a") as log_file:
      log_file.write(f"Error downloading {url}: {e}\n")

def download_images(
    image_urls,
    folder_name="images",
    max_threads=8,
    error_log="error_log.txt"
  ):
  """
  Downloads images from a list of URLs using multiple threads.
  Prints progress to the terminal and logs errors to an error log file.

  Args:
    image_urls: A list of image URLs.
    folder_name: The name of the folder to save the images to.
    max_threads: The maximum number of threads to use.
    error_log: The name of the error log file.
  """

  # Create the folder if it doesn't exist.
  if not os.path.exists(folder_name):
    os.makedirs(folder_name)

  total_images = len(image_urls)
  downloaded_images = 0

  # Use a ThreadPoolExecutor to manage threads.
  with ThreadPoolExecutor(max_workers=max_threads) as executor:
    for _ in executor.map(
      download_image,
      image_urls,
      [folder_name] * total_images,
      [error_log] * total_images
    ):
      downloaded_images += 1
      print(
        f"Completed {downloaded_images} of {total_images} images...",
        end="\r"
      )

  print(
    f"Completed {downloaded_images} of {total_images} images. " +
    "Errors logged to {error_log}."
  )

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Download images from a list of URLs."
  )
  parser.add_argument(
    "url_file",
    help="Path to the file containing image URLs (one URL per line)."
  )
  parser.add_argument(
    "-o",
    "--output",
    default="images",
    help="Output folder name (default: images)."
  )
  parser.add_argument(
    "-t",
    "--threads",
    type=int,
    default=8,
    help="Maximum number of threads (default: 8)."
  )
  args = parser.parse_args()

  # Read image URLs from the file
  with open(args.url_file, "r") as f:
    image_urls = [line.strip() for line in f]

  download_images(image_urls, args.output, args.threads)