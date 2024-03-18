import os
import urllib.request
import zipfile
import console;
from urllib.parse import unquote, urlparse


def extract(zip_path, extract_to, specific_file=None, overwrite=False, callback=None):
    if '.zip' not in zip_path: return ;
    print(f"Extracting {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        all_files = zip_ref.namelist()
        if specific_file:
            all_files = [f for f in all_files if f.endswith(specific_file)]
        total_files = len(all_files)
        extracted_count = 0

        for file_info in zip_ref.infolist():
            if specific_file and not file_info.filename.endswith(specific_file):
                continue

            target_path = os.path.join(extract_to, file_info.filename if not specific_file else specific_file)
            if not overwrite and os.path.exists(target_path):
                total_files -= 1
                continue

            zip_ref.extract(file_info, extract_to)
            if specific_file:
                if overwrite and os.path.exists(target_path):
                    os.remove(target_path)  # Remove the existing file to allow overwriting
                os.rename(os.path.join(extract_to, file_info.filename), target_path)

            extracted_count += 1
            progress = int(50 * extracted_count / total_files) if total_files else 0
            if callback:
                callback(extracted_count,1,total_files)


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
