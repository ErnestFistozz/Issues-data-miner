import csv
import platform
import subprocess

class Utils:
    @staticmethod
    def read_file(file_name: str) -> list:
        with open(file_name, 'r') as file:
            return [line.split()[0].split("/") for line in file]

    @staticmethod
    def determine_directory() -> str:
        match platform.system().lower():
            case 'linux' | 'darwin':
                cmd = "whoami"
                result = subprocess.run(cmd, capture_output=True, shell=True, text=True, check=True).stdout
                data = result.replace('\n','')
                directory = rf'/home/{data}/studies/issues/'
                return directory
            case 'windows':
                cmd = '$env:USERNAME'
                result = (subprocess.run(["powershell", "-Command", cmd],
                                         capture_output=True, shell=True).stdout)
                data = result.decode('utf8').replace("'", '"')
                directory = rf'C:\Users\{data}\Desktop\AzureDevOpsRepos\studies\issues' + "\\"
                return directory

    @staticmethod
    def write_to_file(filename: str, headers: list, data: list) -> None:
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            if csvfile.tell() == 0:
                writer.writeheader()
            if data:
                for row in data:
                    for header in headers:
                        if header not in row:
                            row[header] = ''
                    writer.writerow(row)
