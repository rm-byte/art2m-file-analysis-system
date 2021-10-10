from datetime import datetime
from hashlib import sha384
from json import dumps, loads
from os import listdir, walk
from os.path import getmtime, join, getsize
from random import randint
from time import time

from win32api import GetLogicalDriveStrings

from logs import write_logs


def calculate_byte_histogram(filename) -> list or None:
    histogram = {}
    try:
        content = bytearray(open(filename, 'rb').read())
        for i in range(256):
            histogram.update({i: 0})

        for byte in content:
            was = histogram[byte]
            histogram.update({byte: was + 1})
        return list(histogram.values())
    except PermissionError as e:
        write_logs(str(e))
        return None


def hash_file(filename: str) -> str or None:
    """Хэширование файла"""
    chunk_size = 65536  # 64 kb
    hash = sha384()
    try:
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                hash.update(chunk)
        file.close()
        return hash.hexdigest()
    except PermissionError as e:
        write_logs(str(e))
        return None


def get_header_meta(filename: str) -> list:
    '''pe_file = pefile.PE(filename)
    header_meta = [pe_file.OPTIONAL_HEADER.MajorOperatingSystemVersion,
                   pe_file.OPTIONAL_HEADER.MinorOperatingSystemVersion, pe_file.OPTIONAL_HEADER.MinorLinkerVersion,
                   pe_file.OPTIONAL_HEADER.MajorLinkerVersion, pe_file.OPTIONAL_HEADER.MajorImageVersion,
                   pe_file.OPTIONAL_HEADER.MinorImageVersion]'''
    header_meta = [randint(0, 256) for i in range(6)]

    return header_meta


def file_vectorization(filename: str) -> list:
    histogram = calculate_byte_histogram(filename)
    header_meta = get_header_meta(filename)
    return histogram + header_meta


class ChangedFilesTable:
    def __init__(self):
        self.table = dict()
        self.changed_files = dict()
        self.pe_extensions = ['acm', 'ax', 'cpl', 'dll', 'drv', 'efi', 'exe', 'mui', 'ocx', 'scr', 'sys', 'tsp']
        self.root = './analysis/'

    def _get_last_modified_file(self, disk: str) -> str or None:
        files = listdir(self.root + disk)
        a = [(f, getmtime(f)) for f in [join(self.root, name) for name in files]]
        if a:
            max = a[0][1]
            filename = a[0][0]
            for pair in a:
                if pair[1] > max:
                    max = pair[1]
                    filename = pair[0]
            return filename
        else:
            return None

    def _write_table(self, disk: str) -> None:
        """Записывает полученную таблицу на диск"""
        file = open('analysis/' + disk + '/system_analysis_results_' + str(datetime.now().date()) + '.txt', 'w')
        for record in self.table:
            result = dumps({'filename': record, 'hash': self.table[record]})
            file.write(result + '\n')
        file.close()

    def _load_table(self, disk: str) -> None:
        """Загружает таблицу в память"""
        filename = self._get_last_modified_file(disk)
        if filename:
            file = open(filename, 'r')
            for line in file:
                result = loads(line)
                self.table.update({result['filename']: result['hash']})
            file.close()

    def all_disks_analysis(self) -> None:
        drives = GetLogicalDriveStrings()
        logical_disks = drives.split(':\\\x00')[:-1]
        for disk in logical_disks:
            print('Disk ', disk)
            self.disk_analysis(disk)

    def disk_analysis(self, disk: str) -> None:
        """Занесение исполняемых файлов и вычисленных хэшей в таблицу"""
        # self._load_table(disk)
        current_num = 0
        all_files_size = 0
        all_hashing_time = 0
        all_files_num = 0
        all_vectorization_time = 0
        all_start_time = time()

        for root, dirs, files in walk(disk + ':/'):
            for file_name in [join(root, name) for name in files]:
                all_files_num += 1
                file_extension = file_name.split('.')[-1]
                if file_extension in self.pe_extensions:
                    try:
                        all_files_size += getsize(file_name)

                        start_hash = time()
                        file_hash = hash_file(file_name)
                        end_hash = time()

                        if file_hash:
                            current_num+=1
                            all_hashing_time += end_hash - start_hash

                            start_vectorization = time()
                            try:
                                if self.table[file_name] != file_hash:
                                    self.table.update({file_name: file_hash})
                                    vector = file_vectorization(file_name)
                                    self.changed_files.update({file_name: vector})
                            except KeyError:
                                self.table.update({file_name: file_hash})
                                vector = file_vectorization(file_name)
                                self.changed_files.update({file_name: vector})
                            end_vectorization = time()
                            all_vectorization_time += end_vectorization - start_vectorization
                    except:
                        pass
        all_files_size /= (1024 * 1024)
        all_time = time() - all_start_time
        print('Всего файлов:', all_files_num)
        print('Количество ИФ:', current_num)
        print('Размер ИФ, Мбайт:', all_files_size)

        print('Время предварительного анализа ИФ, включая хеширование и векторизацию', all_time)
        print('Время хеширования:', all_hashing_time)
        print('Время векторизации составило:', all_vectorization_time)

        start = time()
        self._write_table(disk)

        print('Время выгрузки таблицы составило:', time() - start)


if __name__ == "__main__":
    # ChangedFilesTable().all_disks_analysis()
    ChangedFilesTable().disk_analysis('F')
