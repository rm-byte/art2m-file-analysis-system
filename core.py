from os import mkdir
from win32api import GetLogicalDriveStrings

from graph import ARTGraph
from preanalyze import ChangedFilesTable
from vectors import Dataset


def system_prepare() -> None:
    """Creating the required file directories"""
    drives = GetLogicalDriveStrings()
    logical_disks = drives.split(':\\\x00')[:-1]
    dirname = ['logs', 'analysis', 'result', 'tree', 'vectors', 'graphs']
    for disk in logical_disks:
        dirname.append('analysis/' + disk)
    for name in dirname:
        try:
            mkdir(name, mode=0o777, dir_fd=None)
        except FileExistsError as e:
            pass


def draw_graph() -> None:
    artgraph = ARTGraph()
    artgraph.create_graph('graph.txt')
    artgraph.draw_graph()


def first_train_on_ember(directory: str) -> None:
    """

    :param directory: Full path to the directory with dataset EMBER.
    :return: None
    """
    dataset = Dataset()
    dataset.train_vectors_ember(directory)


def additional_train_on_ember(vectors: str, tree_parameters: str) -> None:
    """
    :param vectors: Full path to the file with new images. The full format is described in the note.
    :param tree_parameters: Full path to the file with the main parameters of the memory tree. The full format is described in the note.
    :return: None
    """
    dataset = Dataset()
    dataset.additional_training(vectors, tree_parameters)


def system_analysis(tree_parameters: str) -> None:
    """
    :param tree_parameters: Full path to the file with the main parameters of the memory tree. The full format is described in the note.
    :return: None
    """
    changed_files_table = ChangedFilesTable()
    changed_files_table.all_disks_analysis()
    dataset = Dataset().recognition_vectors(changed_files_table.changed_files, tree_parameters)


def file_analysis(pe_filename: str, tree_parameters: str) -> None:
    """
    :param pe_filename: Full path to the PE file.
    :param tree_parameters: Full path to the file with the main parameters of the memory tree. The full format is described in the note.
    :return: None
    """
    dataset = Dataset()
    dataset.recognition_vector(pe_filename, tree_parameters)
