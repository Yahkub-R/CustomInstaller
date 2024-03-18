import requests
import zipfile
import subprocess
import shutil
import os
import console


def move_contents_up_one_level(extracted_dir):
    subfolders = [f.path for f in os.scandir(extracted_dir) if f.is_dir()]

    if len(subfolders) == 1:
        subfolder = subfolders[0]
        for item in os.listdir(subfolder):
            item_path = os.path.join(subfolder, item)
            new_location = os.path.join(extracted_dir, item)
            if os.path.exists(new_location):
                # Handle potential name conflicts
                print(f"Conflict: {new_location} already exists.")
            else:
                shutil.move(item_path, extracted_dir)
        os.rmdir(subfolder)
    else:
        print("Expected a single subfolder, but found multiple or none.")

def download_release_by_version(repo_url, version):
    parts = repo_url.split("/")
    owner, repo = parts[-2], parts[-1]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        for release in response.json():
            if str(version) in release['tag_name']:
                zipball_url = release['zipball_url']
                dir = download_and_extract_zip(zipball_url, version)
                return dir
        console.printc(f"Release with version {version} not found.", console.LIGHT_YELLOW)
    except requests.RequestException as e:
        console.printc(f"Error fetching releases: {e}", console.RED)

def download_and_extract_zip(url, version):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    bin_dir = os.path.join(script_dir,"bin")
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    local_zip_path = os.path.join(bin_dir, f"release-{version}.zip")
    extract_dir = os.path.join(bin_dir, f"release-{version}")

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    os.remove(local_zip_path)

    return extract_dir


def always_return_true_in_legality_check(file_path):
    start_pattern = 'public static void LegalityCheck(BepInEx.Configuration.ConfigFile config)'
    end_pattern = '}'
    brace_count = 0
    inside_method = False
    new_lines = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        if start_pattern in line:
            inside_method = True
            new_lines.append(line)
            new_lines.append('{\n')
            new_lines.append('            Checked = true;\n')
            new_lines.append('            ProcessLGF(true);\n')
            continue

        if inside_method:
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')

            if brace_count <= 0:
                inside_method = False
                new_lines.append('        }\n')  # Close the method explicitly
                brace_count = 0  # Reset the counter for safety
            continue

        if not inside_method:
            new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


def build_solution(solution_path,version):
    if not os.path.exists(solution_path):
        console.printc("Solution file not found. Please check the path.", console.RED)
        return

    command = ["dotnet", "build", solution_path, "-c", "Release"]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        console.printc(f"Built SIT client {version}", console.LIGHT_YELLOW)
        # print(result.stdout)
        copy_built_files(solution_path)
    except subprocess.CalledProcessError as e:
        console.printc(f"Build failed. {e}", console.RED)


def copy_built_files(solution_path):
    project_dir = os.path.dirname(solution_path)
    files =[
        "StayInTarkov.dll",
        "Assembly-CSharp.dll"
    ]
    source_files = [
        os.path.join(project_dir, "Source", "bin", "Release", "net472", "StayInTarkov.dll"),
        os.path.join(project_dir, "Source", "bin", "Release", "net472", "Assembly-CSharp.dll"),
    ]
    script_dir = os.path.dirname(os.path.realpath(__file__))
    bin_dir = os.path.join(script_dir,"bin")
    index = 0
    os.makedirs(bin_dir, exist_ok=True)
    for source_file in source_files:
        if os.path.exists(source_file):
            shutil.copy(source_file, os.path.join(bin_dir,files[index]))
        else:
            console.printc(f"File not found: {source_file}", console.RED)
        index+=1;

def process(version = "16985"):
    repo_url = "https://github.com/stayintarkov/StayInTarkov.Client"
    extracted_dir = download_release_by_version(repo_url, version)
    move_contents_up_one_level(extracted_dir)
    if extracted_dir:
        source_file_relative_path = "Source/EssentialPatches/LegalGameCheck.cs"
        legal_game_check_path = os.path.join(extracted_dir, source_file_relative_path)
        always_return_true_in_legality_check(legal_game_check_path)
        solution_path = os.path.join(extracted_dir, "StayInTarkov.sln")
        build_solution(solution_path,version)
        shutil.rmtree(extracted_dir)


if __name__ == "__main__":
    process()