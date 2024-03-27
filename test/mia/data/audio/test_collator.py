# -*- coding: utf-8 -*-
# file: test_functions.py
# date: 2024-03-06


import pdb
import librosa
from opencc import OpenCC
from typing import Dict, List, Callable
from torch import Tensor
from transformers import WhisperProcessor

from audiopipeline.data.functions import datasetdict_load_jsonl
from audiopipeline.utils import jsonl_file2json_objs
from audiopipeline.data.collator import DataCollatorSpeechSeq2SeqWithPaddingV1


DEMO_JSONL_PATH: str = "./demo_data/demo_jsonl_dataset.jsonl"
DEMO_JSONL_DATA: List[Dict] = jsonl_file2json_objs(DEMO_JSONL_PATH)
AUDIO_PATH_COL: str = "path"
TEXT_COL: str = "text"
AUDIO_DURATION_COL: str = "input_length" 
MODEL_INPUT_COL: str = "input_features"
MODEL_TARGET_COL: str = "labels"
SAMPLE_ID_COL: str = "file_id"
TARGET_SAMPLE_RATE: int = 16000
DEVICE: str = "cpu"
FEA_EXTRACTOR: WhisperProcessor = WhisperProcessor.from_pretrained(
    "openai/whisper-small", language="mandarin", task="transcribe"
)


def test_DataCollatorSpeechSeq2SeqWithPaddingV1() -> None:
    datasets = datasetdict_load_jsonl(
        DEMO_JSONL_PATH, DEMO_JSONL_PATH, DEMO_JSONL_PATH, 
        sample_id_col=SAMPLE_ID_COL
    )
    jsonl_batch: List[Dict] = [x for x in datasets["train"]][:4]
    collator_obj = DataCollatorSpeechSeq2SeqWithPaddingV1(
        FEA_EXTRACTOR,
        lang="mandarin",
        tokenizer=None, 
        path_col=AUDIO_PATH_COL, text_col=TEXT_COL, 
        audio_duration_col=AUDIO_DURATION_COL, 
        model_input_col=MODEL_INPUT_COL, 
        model_label_col=MODEL_TARGET_COL,
        sample_id_col=SAMPLE_ID_COL, 
        target_sample_rate=TARGET_SAMPLE_RATE
    )
    train_inputs: Dict[str, Tensor] = collator_obj(jsonl_batch)

    assert(MODEL_INPUT_COL in train_inputs)
    assert("labels" in train_inputs)
    assert(SAMPLE_ID_COL in train_inputs)
    
    assert(train_inputs[SAMPLE_ID_COL].shape[0] == train_inputs[MODEL_INPUT_COL].shape[0])
    assert(train_inputs[SAMPLE_ID_COL].shape[0] == train_inputs["labels"].shape[0])

    decoded_texts: List[str] = FEA_EXTRACTOR.tokenizer.batch_decode(
        train_inputs[MODEL_TARGET_COL], skip_special_tokens=True
    )
    for text in decoded_texts:
        assert(OpenCC("tw2s.json").convert(text) == text)

