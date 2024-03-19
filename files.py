import os
import shutil
import tempfile
import urllib.request
import zipfile
import console;
from urllib.parse import unquote, urlparse


def update_extraction_progress(count, total, callback):
    callback(count, 1, total)


def extract_all(zip_path, extract_to, overwrite=False, callback=None):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        if '.zip' not in zip_path: return;
        print(f"Extracting {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            total_files = len(all_files)
            extracted_count = 0

            for file_info in zip_ref.infolist():

                target_path = os.path.join(extract_to, file_info.filename)
                if not overwrite and os.path.exists(target_path):
                    total_files -= 1
                    continue

                zip_ref.extract(file_info, extract_to)
                if overwrite and os.path.exists(target_path):
                    os.remove(target_path)  # Remove the existing file to allow overwriting
                os.rename(os.path.join(extract_to, file_info.filename), target_path)

                extracted_count += 1
                progress = int(50 * extracted_count / total_files) if total_files else 0
                if callback:
                    callback(extracted_count, 1, total_files)


def extract_folder(temp_dir, extract_to, specific_folder, overwrite, callback):
    # Search for the specific folder
    specific_folder_path = None
    for root, dirs, files in os.walk(temp_dir):
        if specific_folder in dirs:
            specific_folder_path = os.path.join(root, specific_folder)
            break

    if specific_folder_path is None:
        print(f"The folder '{specific_folder}' was not found within '{temp_dir}'.")
        return

    # Calculate total number of files for progress tracking
    total_files = sum([len(files) for _, _, files in os.walk(specific_folder_path)])
    copied_files = 0

    # Merge the specific folder with the destination
    for root, dirs, files in os.walk(specific_folder_path):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, specific_folder_path)
            destination_path = os.path.join(extract_to, specific_folder, relative_path, file)

            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            if overwrite or not os.path.exists(destination_path):
                shutil.copy2(source_path, destination_path)
            copied_files += 1
            update_extraction_progress(copied_files, total_files, callback)


def extract_file(temp_dir, extract_to, specific_file, overwrite, callback):
    extracted_count = 0
    for root, _, files in os.walk(temp_dir):
        if specific_file in files:
            if overwrite or not os.path.exists(os.path.join(extract_to, specific_file)):
                shutil.copy2(os.path.join(root, specific_file), os.path.join(extract_to, specific_file))
            extracted_count += 1
            total_files = 1  # Since we are looking for a specific file
            update_extraction_progress(extracted_count, total_files, callback)
            break
    if extracted_count == 0:
        print(f"File {specific_file} not found in the archive.")


def extract(zip_path, extract_to, specific_file=None, specific_folder=None, overwrite=False, callback=None):
    if '.zip' not in zip_path:
        print("Not a ZIP file.")
        return
    print(f"Extracting {zip_path}")
    if not specific_file and not specific_folder:
        extract_all(zip_path, extract_to, overwrite, callback)
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        if specific_file:
            extract_file(temp_dir, extract_to, specific_file, overwrite, callback)

        elif specific_folder:
            extract_folder(temp_dir, extract_to, specific_folder, overwrite, callback)


def download(url, folder, overwrite=False, callback=None):
    os.makedirs(folder, exist_ok=True)
    pass
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    )

    with urllib.request.urlopen(req) as response:
        local_filename = None
        # Attempt to prioritize filename from the URL
        url_path = urlparse(url).path
        if url_path and '.' in url_path.rsplit('/', 1)[-1]:  # Basic check for a file extension
            local_filename = url_path.rsplit('/', 1)[-1]

        cd = response.headers.get('Content-Disposition')
        if not local_filename and cd:
            filenames = {}
            for part in cd.split(';'):
                part = part.strip()
                if '=' in part:
                    key, value = part.split('=', 1)
                    filenames[key] = value.strip('"\' ')

            if 'filename*' in filenames:
                encoding, encoded_name = filenames['filename*'].split("''")
                local_filename = unquote(encoded_name)
            elif 'filename' in filenames:
                local_filename = unquote(filenames['filename'])

        if not local_filename:
            raise ValueError("Filename could not be determined from the URL or the Content-Disposition header.")

        path = os.path.join(folder, local_filename)
        if os.path.exists(path) and not overwrite:
            return path
        print(f"Downloading {local_filename}")
        urllib.request.urlretrieve(url, path, callback)

    return path
