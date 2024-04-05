# -*- coding: utf-8 -*-
# file: train.py
# date: 2024-03-30
#
# A standalone flan-T5 fine-tuning program, originally 
# submitted to https://github.com/innerNULL/mia
#
# References:
# * https://www.datacamp.com/tutorial/flan-t5-tutorial
# 
# Run:
# CUDA_VISIBLE_DEVICES=0 python bin/model/flan_t5/finetune.py demo_configs/model/flan_t5/finetune.json 


import pdb
import sys
import os
import json
import random as rd
import numpy as np
from typing import Dict, List, Optional, Callable
from datasets import load_dataset
from datasets import disable_caching
from datasets import Dataset, DatasetDict
from torch import Tensor
from transformers import T5Tokenizer
from transformers import DataCollatorForSeq2Seq
from transformers import T5ForConditionalGeneration
from transformers import Seq2SeqTrainingArguments
from transformers import Seq2SeqTrainer
from transformers import PreTrainedModel
from transformers import PreTrainedTokenizer
from transformers import EvalPrediction
from transformers import BatchEncoding
from torchmetrics.text.rouge import ROUGEScore


def data_aug_mask_text(text: str, ratio: float, splitter: str=" ") -> str:    
    words: List[str] = text.split(splitter)
    masked_words: List[str] = []
    for word in words:
        if rd.random() >= ratio:
            masked_words.append(word)
    return splitter.join(masked_words)


def dataset_load(
    path_or_name: str, split: Optional[str]=None
) -> Dataset:
    if os.path.exists(path_or_name):
        if path_or_name.split(".")[-1] == "csv":
            return Dataset.from_pandas(pd.read_csv(path_or_name))
        elif path_or_name.split(".")[-1] == "jsonl":
            return load_dataset("json", data_files=path_or_name)["train"]
        else:
            raise Exception("Not a supported file format")
    else:
        if split is None:
            raise "Can not loading HuggingFace dataset without split info"
        return load_dataset(path_or_name, split=split)


def datasets_load(
    train_path_or_name: str,
    dev_path_or_name: str, test_path_or_name: str
) -> DatasetDict:
    datasets: DatasetDict = DatasetDict()
    datasets["train"] = dataset_load(train_path_or_name, "train")
    datasets["validation"] = dataset_load(dev_path_or_name, "validation")
    datasets["test"] = dataset_load(test_path_or_name, "test")
    return datasets


def generate_evaluator(tokenizer: T5Tokenizer) -> Callable:
    """
    TODO@20240330_1653:

    Do evaluation with using `compute_metrics` in `Trainer` is not
    a good choose, since HuggingFace had make simple thinkg as 
    evaluation too complicated, you have to work together with a 
    unnecessary data structure called `EvalPrediction`.

    A better approach is to use `TrainerCallback.on_epoch_end`, with 
    this you may have more work to do, but at least everything and 
    be more clear and clean.
    """
    def _evaluator(pred_and_labels: EvalPrediction) -> Dict[str, float]:
        output_token_ids: np.ndarray = None
        target_token_ids: np.ndarray = None
        output_token_ids, target_token_ids = pred_and_labels

        target_token_ids = np.where(
            target_token_ids != -100, target_token_ids, tokenizer.pad_token_id
        )
        decoded_preds = tokenizer.batch_decode(
            output_token_ids, skip_special_tokens=True
        )
        decoded_labels = tokenizer.batch_decode(
            target_token_ids, skip_special_tokens=True
        )
        metrics: Dict[str, Tensor] = ROUGEScore()(decoded_preds, decoded_labels)
        return {k: v.cpu().tolist() for k, v in metrics.items()}

    return _evaluator


class FeatureExtractor():
    def __init__(self, 
        tokenizer: T5Tokenizer, 
        input_text_col: str, 
        target_text_col: Optional[str]=None,
        max_input_token_len: int=512,
        max_target_token_len: int=512,
        input_tensor_col: str="input_ids",
        target_tensor_col: str="labels",
        prompt: str=""
    ):
        self.tokenizer: T5Tokenizer = tokenizer
        self.input_text_col: str = input_text_col
        self.target_text_col: Optional[str] = target_text_col
        self.max_input_token_len: int = max_input_token_len
        self.max_target_token_len: int = max_target_token_len
        self.input_tensor_col: str = input_tensor_col
        self.target_tensor_col: str = target_tensor_col
        self.prompt: str = prompt

    def __call__(self, raw_sample: Dict[str, str]) -> Dict[str, Tensor]:
        """
        Output is a key-value format Dict, all values are `Tensor`s, and 
        the keys are "input_ids", "attention_mask" and "labels"
        """
        out: Dict[str, Tensor] = self.tokenizer(
            self.prompt + "\n" + raw_sample[self.input_text_col], 
            max_length=self.max_input_token_len, truncation=True
        )
        if self.target_text_col is not None:
            out[self.target_tensor_col] = self.tokenizer(
                raw_sample[self.target_text_col], 
                max_length=self.max_target_token_len, truncation=True
            )["input_ids"]
        return out


class DataCollator(DataCollatorForSeq2Seq):
    def __init__(self,
        tokenizer: PreTrainedTokenizer,
        model: PreTrainedModel,
        fea_extractor: FeatureExtractor,
        text_mask_ratio: float=0.0,
        token_mask_ratio: float=0.0,
        padding: bool=True,
        max_length: Optional[int]=None,
        pad_to_multiple_of: Optional[int]=None,
        label_pad_token_id: int=-100,
        return_tensors: str="pt"
    ):
        super().__init__(
            tokenizer=tokenizer, model=model,
            padding=padding, max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of,
            label_pad_token_id=label_pad_token_id,
            return_tensors=return_tensors
        )
        self.fea_extractor: FeatureExtractor = fea_extractor
        self.text_mask_ratio: float = text_mask_ratio
        self.token_mask_ratio: float = token_mask_ratio

    def __call__(self,
        features: List[Dict[str, str]], return_tensors=None
    ) -> BatchEncoding:
        if self.text_mask_ratio > 0:
            for i in range(len(features)):
                masked_text: str = data_aug_mask_text(
                    features[i][fea_extractor.input_text_col], 
                    self.text_mask_ratio, " "
                )
                features[i][fea_extractor.input_text_col] = masked_text
        model_inputs: List[Dict[str, Tensor]] = [
            self.fea_extractor(feature) for feature in features
        ]
        if self.token_mask_ratio > 0:
            pass
        return super().__call__(
            features=model_inputs, return_tensors=return_tensors
        )


if __name__ == "__main__":
    configs: Dict = json.loads(open(sys.argv[1], "r").read())
    data_configs: Dict = configs["data"]
    model_configs: Dict = configs["model"]
    train_configs: Dict = configs["train"]

    print(data_configs)
    print(model_configs)
    print(train_configs)

    disable_caching()
    os.system("mkdir -p %s" % train_configs["ckpt_dir"])
    os.system("cp %s %s" % (sys.argv[1], train_configs["ckpt_dir"]))

    model: PreTrainedModel = T5ForConditionalGeneration.from_pretrained(
        model_configs["pretrained_model_path_or_name"]
    )
    tokenizer: T5Tokenizer = T5Tokenizer.from_pretrained(
        model_configs["tokenizer_path_or_name"]
    )
    fea_extractor: FeatureExtractor = FeatureExtractor(
        tokenizer=tokenizer, 
        input_text_col=data_configs["input_text_col"], 
        target_text_col=data_configs["target_text_col"],
        max_input_token_len=model_configs["max_input_token_len"], 
        max_target_token_len=model_configs["max_target_token_len"],
        input_tensor_col="input_ids", 
        target_tensor_col="labels", 
        prompt=train_configs["prompt"]
    )
    datasets: DatasetDict = datasets_load(
        data_configs["train_path_or_name"], 
        data_configs["dev_path_or_name"], data_configs["test_path_or_name"],
    )

    print("example raw sample:")
    print(datasets["test"][0])
    print("example input:")
    print(fea_extractor(datasets["test"][0]))
    
    if train_configs["text_mask_ratio"] > 0:
        print("text before masking:")
        print(datasets["test"][0][data_configs["input_text_col"]])
        print("text after masking:")
        print(data_aug_mask_text(
            datasets["test"][0][data_configs["input_text_col"]], 
            train_configs["text_mask_ratio"], " "
        ))

    data_collator: DataCollatorForSeq2Seq = None
    if not train_configs["advanced_feature"]:
        datasets = datasets.map(fea_extractor, num_proc=4)
        data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    else:
        data_collator = DataCollator(
            tokenizer=tokenizer, model=model, fea_extractor=fea_extractor,
            text_mask_ratio=train_configs["text_mask_ratio"], 
            token_mask_ratio=train_configs["token_mask_ratio"]
        )

    train_args: Seq2SeqTrainingArguments = Seq2SeqTrainingArguments(
        output_dir=train_configs["ckpt_dir"],
        evaluation_strategy="epoch",
        learning_rate=train_configs["learning_rate"],
        per_device_train_batch_size=train_configs["per_device_train_batch_size"],
        per_device_eval_batch_size=train_configs["per_device_eval_batch_size"],
        weight_decay=train_configs["weight_decay"],
        save_total_limit=7,
        num_train_epochs=train_configs["num_epoch"],
        predict_with_generate=True,
        push_to_hub=False,
        save_only_model=True,
        # This is a trap in HF transformers, refer to: 
        # https://discuss.huggingface.co/t/indexerror-invalid-key-16-is-out-of-bounds-for-size-0/14298/4
        # and 
        # https://github.com/huggingface/transformers/issues/15505
        remove_unused_columns=(not train_configs["advanced_feature"])
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=train_args,
        train_dataset=datasets["train"], eval_dataset=datasets["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=generate_evaluator(tokenizer)
    )
    
    trainer.train()
    
    #pdb.set_trace()
