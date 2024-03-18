import json
import shutil
import subprocess
import sys
from contextlib import contextmanager
import shlex

from PyQt5.QtCore import QObject, pyqtSignal
import os


@contextmanager
def custom_print(emit_func, buffer_size=0):
    class CustomPrinter:
        def __init__(self):
            self.buffer = []
            self.buffer_size = buffer_size

        def write(self, text):
            self.buffer.append(text)
            if len(self.buffer) >= self.buffer_size:
                emit_func(''.join(self.buffer))
                self.buffer.clear()

        def flush(self):
            if self.buffer:
                emit_func(''.join(self.buffer))
                self.buffer.clear()

    sys.stdout = CustomPrinter()
    try:
        yield
    finally:
        sys.stdout.flush()


class InstallWorker(QObject):
    finished = pyqtSignal()  # Signal to indicate the thread is finished
    progress = pyqtSignal(str)  # Signal to update progress (e.g., print statements)
    percent = 0

    def __init__(self, getVersion, gameCombo, versionCombo, filePath):
        super().__init__()
        self.data = getVersion()
        self.gameCombo = gameCombo
        self.versionCombo = versionCombo
        self.filePath = filePath

    def run(self):
        with custom_print(self.progress.emit):
            path = self.filePath.text() + "/" + self.gameCombo.currentText() + "." + self.versionCombo.currentText()
            os.makedirs(path, exist_ok=True)
            downloads = os.path.join(path, "download")
            installed_progress_path = os.path.join(path,
                                                   f"{self.gameCombo.currentText()}.{self.versionCombo.currentText()}.progress.log")

            steps = self.data["steps"]

            # Initialize a set to keep track of completed steps
            completed_steps = set()

            # Check if the progress file exists and read completed steps
            if os.path.exists(installed_progress_path):
                with open(installed_progress_path, 'r') as log_file:
                    completed_steps = set(log_file.read().splitlines())

            steps_total = len(steps)
            steps_done = 0
            with open(installed_progress_path, 'w') as progress:
                for step in steps:
                    type = step['type']
                    name = step['name']

                    # Skip this step if it's already completed
                    if f"{type}:{name}" in completed_steps or 'force' in step:
                        steps_done += 1
                        progress.write(f"{type}:{name}\n")
                        print(f"🟢 ({steps_done}/{steps_total}): {type}:{name}")
                        continue
                    try:
                        match type:
                            case 'download':
                                downloaded = files.download(step['url'], downloads, callback=self.display)
                                if 'to' in step:
                                    os.makedirs(os.path.join(path, step["to"]), exist_ok=True)
                                if ".zip" in downloaded:
                                    files.extract(downloaded, os.path.join(path, step["to"]), callback=self.display)
                                elif 'to' in step:
                                    destination = os.path.join(path, step["to"], name)
                                    shutil.copy(downloaded, destination)
                            case 'execute':
                                shell_cmd = shlex.split(step['command'], posix=False)
                                print(os.path.realpath(path))
                                results = subprocess.run(shell_cmd, cwd=path.replace('/', '\\'),
                                                         capture_output=True, text=True, shell=True)
                                if results.stderr:
                                    raise Exception("Failed to run command")
                                print(results.stdout)
                            case 'json':
                                json_file_path = os.path.join(path, step["file"]).replace("\\", "/")
                                # Ensure the file exists
                                if os.path.isfile(json_file_path):
                                    # Load the current JSON data from the file
                                    with open(json_file_path, 'r') as file:
                                        data = json.load(file)

                                    # Modify the specified entry
                                    # This assumes the 'from' key exists at the top level of the JSON structure
                                    if step["from"] in data:
                                        data[step["from"]] = step["to"]
                                        # Save the modified JSON data back to the file
                                        with open(json_file_path, 'w') as file:
                                            json.dump(data, file, indent=4)
                                    else:
                                        raise Exception(f"Key '{step['from']}' not found in {json_file_path}")
                                else:
                                    print(f"File {json_file_path} not found")
                                    raise Exception(f"Key '{step['from']}' not found in {json_file_path}")
                            case 'txt':
                                txt_file_path = os.path.join(path, step["file"]).replace("\\", "/")
                                # Ensure the file exists
                                if os.path.isfile(txt_file_path):
                                    # Load the current JSON data from the file
                                    with open(txt_file_path, 'r') as file:
                                        lines = file.readlines()
                                    wrote = False
                                    for index, line in enumerate(lines):
                                        if step['from'] in line:
                                            wrote = True
                                            lines[index] = line.replace(step['from'], step['to'])
                                    with open(txt_file_path, 'w') as file:
                                        file.writelines(lines)
                                    if not wrote:
                                        raise Exception(f"Text '{step['from']}' not found in {txt_file_path}")

                            case 'bat':
                                if 'to' not in step or ('to' in step and '.bat' not in step['to']):
                                    bat_file_path = os.path.join(path, f"{step['name']}.bat")
                                else:
                                    bat_file_path = os.path.join(path, step["to"])
                                bat_file_content = step["content"]

                                with open(bat_file_path, 'w') as file:
                                    file.write(bat_file_content)

                        # Mark this step as completed by writing it to the log
                        progress.write(f"{type}:{name}\n")
                        steps_done += 1
                        print(f"🟢 ({steps_done}/{steps_total}): {type}:{name}")
                    except Exception as e:
                        print(f"{e}\n🔴 step {type}:{name} failed️")
                        print(f"Completed {steps_done}/{steps_total} steps")
                        self.finished.emit()
                        return
        print(f"Completed {steps_done}/{steps_total} steps")
        self.finished.emit()

    def display(self, block_num, block_size, total_size):
        downloaded = block_num * block_size
        chars = 45
        p = min(int(chars * downloaded / total_size), chars)
        if self.percent != p:
            self.percent = p
            progress_bar = "\r[%s%s] %d%%" % (
                '■' * self.percent, ' ' * (chars - self.percent), int(100 * downloaded / total_size))
            print(progress_bar, end='')

        if p >= chars:
            print(" ")
            return

        pass;
