# -*- coding: utf-8 -*-
# file: dataset.py
# date: 2024-03-06


import pdb
from datasets import load_dataset
from typing import Dict, Callable, Union, List, Tuple, Optional
from datasets import DatasetDict, Dataset


def datasetdict_load_jsonl(
    train_data_path: str, dev_data_path: str, test_data_path: str, 
    sample_id_col: str=""
) -> DatasetDict:
    print("Running dataset dict JSONL loader")
    dataset: DatasetDict = DatasetDict()

    if train_data_path is not None:
        dataset["train"] = load_dataset("json", data_files=train_data_path)["train"]
    if dev_data_path is not None:
        dataset["validation"] = load_dataset("json", data_files=dev_data_path)["train"]
    if test_data_path is not None:
        dataset["test"] = load_dataset("json", data_files=test_data_path)["train"]
    
    if sample_id_col not in {""}:
        def _add_sample_id(sample: Dict, idx: int) -> Dict:
            sample[sample_id_col] = idx
            return sample

        for split in dataset:
            dataset[split] = dataset[split].map(_add_sample_id, with_indices=True)

    return dataset


def hf_datasetdict_load_audio_jsonl(
    train_data_path: Optional[str]=None, 
    dev_data_path: Optional[str]=None, 
    test_data_path: Optional[str]=None,
    sample_id_col: str=""
) -> DatasetDict:
    return datasetdict_load_jsonl(
        train_data_path, dev_data_path, test_data_path, 
        sample_id_col
    )
