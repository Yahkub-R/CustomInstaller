import requests
import hashlib
import time
import json
import os


def fetch_hashes_from_url(url):
    """Fetches JSON data from the provided URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the response was an error
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def compare_hashes(version, paths, url):
    remote = fetch_hashes_from_url(url)["versions"]
    if not remote or version not in remote:
        print(f"Version {version} not found in remote data.")
        return
    for path in paths:
        remote_hashes = remote[version]
        local_hash = calculate_file_hash(path, show_progress)
        filename = os.path.basename(path)
        if filename not in remote_hashes and "patches" in remote_hashes:
            remote_hashes = remote_hashes["patches"]
        if filename in remote_hashes:
            remote_hash = remote_hashes[filename]["hash"]
            if local_hash == remote_hash:
                print(f"{filename}: ✔")
            else:
                print(f"{filename}: Hash mismatch. Local: {local_hash}, Remote: {remote_hash}")
        else:
            print(f"{filename}: Not found in remote data.")


def calculate_file_hash(file_path, progress_callback=None):
    """Calculates the SHA-256 hash of a file's contents and shows progress."""
    sha256_hash = hashlib.sha256()
    file_size = os.path.getsize(file_path)
    bytes_read = 0

    # Determine the update frequency in bytes (e.g., every 1% of total size)
    update_freq = file_size // 100

    try:
        with open(file_path, 'rb') as file:
            while True:
                byte_block = file.read(4096)
                if not byte_block:
                    break
                sha256_hash.update(byte_block)
                bytes_read += len(byte_block)

                # Only invoke the progress callback based on the update frequency
                if progress_callback is not None and bytes_read % update_freq < 4096:
                    progress_callback(bytes_read, 4096, file_size)
    except IOError as e:
        print(f"Error opening or reading file: {file_path}. {e}")
        return None

    return sha256_hash.hexdigest()


def show_progress(bytes_read, block_size, total_size):
    progress = min(int(50 * bytes_read / total_size), 50)
    progress_bar = "\r[%s%s] %d%%" % ('■' * progress, ' ' * (50 - progress), int(100 * bytes_read / total_size))
    print(progress_bar, end='', flush=True)
    if bytes_read >= total_size:
        print()


def validate_and_store(version, paths, output_file):
    results = {}

    for path in paths:
        hash_value = calculate_file_hash(path, show_progress)
        filename = os.path.basename(path)
        if hash_value:
            print(f"SHA-256 Hash for {filename}: {hash_value}")
            results[filename] = {
                "hash": hash_value,
                "url": ""
            }
        else:
            print(f"Failed to calculate the file hash for {path}.")

    # Load existing data if the output file already exists
    if os.path.exists(output_file):
        with open(output_file, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # Update or add the version data
    existing_data[version] = results

    # Writing the updated data to the JSON file
    with open(output_file, 'w') as outfile:
        json.dump(existing_data, outfile, indent=4, sort_keys=True)
    print(f"Results for version {version} stored in {output_file}")


def newer(v1, v2):
    major1, minor1, patch1 = v1.split('.')
    major2, minor2, patch2 = v2.split('.')

    if int(major1) > int(major2):
        return False
    else:
        if int(minor1) > int(minor2):
            return False
        else:
            if int(patch1) > int(patch2):
                return False
    return True


if __name__ == "__main__":
    start_time = time.time()  # Record the start time
    # Version to be added or updated
    game = "tarkov"
    version = "28875"

    # List of file paths to calculate hashes for
    paths = [
        '../download/BepInEx_x64_5.4.22.0.zip',
        '../download/SIT.Manager.zip',
        '../download/SITCoop-1.6.0-WithAki3.8.0-d4ee8f-win.zip',
        '../download/Client.0.14.1.1.28875.zip',
        '../download/StayInTarkov.dll',
        '../download/Assembly-CSharp.dll',
        '../download/Client.0.14.1.1.28875-0.14.1.1.28965.update',
        '../download/Client.0.14.1.1.28965-0.14.1.2.29197.update',
        '../download/EFT-Patcher.exe',
    ]
    url = "https://jbruth.com/v/updater.info.json"

    compare_hashes(version, paths, url)
    # Output JSON file
    output_file = 'out.json'

    # validate_and_store(version, paths, output_file)

    end_time = time.time()  # Record the end time
    runtime = end_time - start_time  # Calculate the runtime
    print(f"Runtime: {runtime:.2f} seconds")  # Print the runtime
