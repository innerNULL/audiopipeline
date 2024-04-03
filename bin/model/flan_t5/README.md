# Flan-T5 
## Introduction
TBD

## T5 Fine-Tuning
Try:
```shell
CUDA_VISIBLE_DEVICES=0 python bin/model/flan_t5/finetune.py demo_configs/model/flan_t5/finetune.json
```
**The `train_path_or_name`, `dev_path_or_name` and `test_path_or_name` in 
config file can also be your customized JSON lines file.**

## T5 Inference (Offline)
This will generate a new JSON lines file, which contains input text, 
target text(groudtruth/label) and output text(generated by T5).
```shell
python bin/model/flan_t5/inference.py ./demo_configs/model/flan_t5/inference.json
```
**The `data_path_or_name` in config file do not necessary be HuggingFace Datasets 
data, any CSV or JSON lines file is OK.**

## T5 Evaluation
Update the configs file of `./bin/evaluation/text_summarisation/eval_all_in_one_standalone.py` 
with the JSON lines file generated by running `bin/model/flan_t5/inference.py`, and run: 
```shell
python ./bin/evaluation/text_summarisation/eval_all_in_one_standalone.py ${YOUR_CONFIG}.json
````