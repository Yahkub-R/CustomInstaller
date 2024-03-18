import os
import urllib.request
import zipfile
import subprocess
import json
import console
from urllib.parse import unquote, urlparse


logo = '''######################################################
#   ____ ___ _____   _____          _                #
#  / ___|_ _|_   _| |_   _|_ _ _ __| | _______   __  #
#  \___ \| |  | |     | |/ _` | '__| |/ / _ \ \ / /  #
#   ___) | |  | |     | | (_| | |  |   < (_) \ V /   #
#  |____/___| |_|     |_|\__,_|_|  |_|\_\___/ \_/    #
#                                      Version J.1.0 #
######################################################
'''


script_dir = os.path.dirname(os.path.realpath(__file__))
def load_urls_from_json(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)


def download(url, folder, overwrite=False, name=None):
    os.makedirs(folder, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
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
            print(f"{local_filename} already exists, skipping download.")
            return path

        print(f"Downloading {local_filename}")


        # Download the file from `url` and save it locally under `path`
        urllib.request.urlretrieve(url, path, console.show_progress)

    return path


def extract(zip_path, extract_to, specific_file=None, overwrite=False):
    console.printc(f"Extracting {zip_path}", console.LIGHT_YELLOW)
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
            if (total_files > 0):
                progress_text = "\r[%s%s] %d%% (%d/%d)" % (
                    '■' * progress, ' ' * (50 - progress), 100 * extracted_count / total_files, extracted_count,
                    total_files)
                console.printc(progress_text, console.YELLOW, True)
                if extracted_count >= total_files and extracted_count > 0:
                    print("\n")


def bat(working_directory, exe_path, bat_path):
    with open(bat_path + ".bat", 'w') as bat_file:
        bat_file.write(f'@echo off\n')
        bat_file.write(f'cd /d "{working_directory}"\n')
        bat_file.write(f'start "" "{exe_path}.exe"\n')
        bat_file.write('exit')


def update_manager_config(install_path, server_path):
    config_path = os.path.join("Launcher", "ManagerConfig.json")
    config = {
        "LastServer": "http://127.0.0.1:6969",
        "Username": None,
        "Password": None,
        "RememberLogin": True,
        "CloseAfterLaunch": False,
        "LookForUpdates": True,
        "InstallPath": None,
        "AkiServerPath": None,
        "TarkovVersion": None,
        "SitVersion": "1.10.8827.30098",
        "HideIPAddress": True,
        "AcceptedModsDisclaimer": False,
        "ModCollectionVersion": None,
        "InstalledMods": {},
        "ConsoleFontColor": "#FFADD8E6",
        "ConsoleFontFamily": "Consolas"
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
        except json.JSONDecodeError:
            console.printc(f"Failed to decode JSON from {config_path}, using default configuration.",
                           console.RED)
        except Exception as e:
            console.printc(f"An unexpected error occurred while reading {config_path}: {e}", console.RED)


    install_path = os.path.join(install_path)
    server_path = os.path.join(server_path)

    install_path = os.path.abspath(install_path)
    server_path = os.path.abspath(server_path)

    config['InstallPath'] = install_path
    config['AkiServerPath'] = server_path

    try:
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        console.printc("SIT Manager config updated", console.LIGHT_YELLOW)
    except Exception as e:
        console.printc(f"An error occurred while writing to {config_path}: {e}", console.RED)


# Tarkov
def install_sit(download_path, install_path, server_path, urls):
    bepinex_plugins_path = os.path.join(install_path, "BepInEx", "plugins")

    if not os.path.exists(bepinex_plugins_path):
        os.makedirs(bepinex_plugins_path, exist_ok=True)

    bep_path = download(urls["bepinex"], download_path, overwrite=True)
    extract(bep_path, install_path )
    aki_path = download(urls["sit_server"], download_path, overwrite=True)
    extract(aki_path, server_path)


def should_patch_game(game_directory, urls):
    version = urls['update'].split('/')[-1].replace('.update', '').replace('Client.', '')

    version_file_path = os.path.join(game_directory, version + ".version")

    if os.path.exists(version_file_path):
        console.printc(f"Version {version} has already been patched. Skipping patching.", console.GRAY)
        return False
    else:
        with open(version_file_path, 'w') as version_file:
            version_file.write(f"Patched to version {version}")
        console.printc(f"Proceeding with patching to version {version}.", console.GREEN)
        return True


def main():
    console.printc(logo, console.LIGHT_BLUE)
    urls = load_urls_from_json("urls.json")

    os.makedirs("game", exist_ok=True)
    os.makedirs("launcher", exist_ok=True)
    os.makedirs("server", exist_ok=True)

    game_zip = download(urls['game'], "download")
    extract(game_zip, "game")

    sit_manager_zip = download(urls['launcher'], "download")
    extract(sit_manager_zip, "launcher")

    if urls['update'] and should_patch_game("Game", urls):
        download(urls['update'], "download")
        download(urls['patcher'], "download")
        subprocess.run(
            ["download/EFT-Patcher.exe", "-u", "Client.0.14.1.1.28875-0.14.1.1.28965.update", "-e", "../game"],
            cwd="download")

    update_manager_config("game", "server")
    install_sit("download", "game", "server", urls)

    # if shutil.which("dotnet") is not None:
    #     compile.process(urls['SIT_version'])
    #     shutil.move("src/bin/StayInTarkov.dll", "game/BepInEx/plugins/StayInTarkov.dll")
    #     shutil.move("src/bin/Assembly-CSharp.dll", "game/EscapeFromTarkov_Data/Managed/AssemblyCSharp.dll")
    #     shutil.rmtree("src/bin")
    # else:
    download(urls['SIT_DLL'], "game/bepinex/plugins", True)
    download(urls['ASSEMBLY_DLL'], "game/EscapeFromTarkov_Data/Managed", True)
    # extract(stay_in_tarkov_zip, "game/BepInEx/plugins", specific_file="StayInTarkov.dll", overwrite=True)
    # extract(stay_in_tarkov_zip, "game/EscapeFromTarkov_Data/Managed", specific_file="Assembly-CSharp.dll",
    #         overwrite=True)

    if os.path.exists("game/BepInEx/plugins/StayInTarkov-Release"):
        os.rmdir("game/BepInEx/plugins/StayInTarkov-Release")
    if os.path.exists("game/EscapeFromTarkov_Data/Managed/StayInTarkov-Release"):
        os.rmdir("game/EscapeFromTarkov_Data/Managed/StayInTarkov-Release")

    bat("Launcher", "SIT.Manager", "Client")
    bat("Server", "Aki.Server", "Server")
    console.printc("Setup complete, you may close this window", console.LIGHT_BLUE)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        input("Press Enter to exit...")
