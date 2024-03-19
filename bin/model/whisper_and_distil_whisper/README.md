# Whisper and Distil-Whisper Modeling

## Whisper
TODO

## Distil-Whisper
Simple speaking, Whisper is too large to deploy into a lot of production 
environments, we can deal this with model distillation technique. 

The [paper "Distil-Whisper: Robust Knowledge Distillation via Large-Scale Pseudo Labelling"](
https://arxiv.org/abs/2311.00430) proposed a robust and straight forward approach to make 
full-size Whisper become smaller, but unfortunally, the [original implementation](
https://github.com/huggingface/distil-whisper) has following problems with make it painful 
to use in real working:
* Unnecessarily coupled together with a lot of HuggingFace lib, most of them are not really
  easy to use, like [datasets](https://github.com/huggingface/datasets), [huggingface_hub](
  https://github.com/huggingface/huggingface_hub).
* A lot of rarely using logics, like uploading your data, uploading your trained model....
  seriously, WHY WOULD I DO THAT...??
* Tied together with data on [HuggingFace Datasets platform](https://huggingface.co/datasets),
  I believe most MLE/researchers who need distil or fine-tune Whiper have their internal 
  datasets.

So the target of this working is to solve the problem brought by [original implementation](
https://github.com/huggingface/distil-whisper) and make MLEs/researchers life easier when 
they need distil Whisper with their customized datasets.

### Design
Basically do distillation of Whisper contain three steps:
* Generate psuedo labeled dataset based on original **training** dataset.
* Initialize a distilled/pruned Whisper based on full-sized model.
* Model distillation.

Each of above steps will corresponding with a single program to run.

#### Config
Compare with [original implementation](https://github.com/huggingface/distil-whisper), we make 
parameters be much more clear by put all parameter into a JSON configs, so:
* Do not have a lot of commond-line parameters, one JSON configs can have everything you need.
* Even you don't know or care some not commonly used default parameters, you can still get 
  their existance, in case when you need change it in future.
* After each task, the JSON configs will be copied into an output folder with which you can 
  always reproduce your task in future.

The demo configs can be found at `demo_configs/model/whisper_and_distil_whisper`.

#### Data
All audio datasets are just a JSON lines file.
* **Original Training Dataset**: Contains at least 2 fields, one represents text/transcript, 
  the other represents audio file path.
* **Psuedo Labelled Training Dataset**: Contains at least 3 fields, the first represents 
  text/transcript **generated by original full-sized Whiser(psuedo label)**, the second 
  for audio file path, and the third for CER/WER between psuedo label and original text. 

### Step-By-Step
#### Preparation
* A directory in which contains a pre-trained or fine-tuned HuggingFace Whisper model.
* JSON lines audio training & dev & test dataset.
* Build Python environment:
```shell
python3 -m venv ./_venv --copies
source ./bin/activate
python -m pip install ./
# deactivate
```

#### Psuedo Labelling
```shell
python ./bin/model/whisper_and_distil_whisper/run_pseudo_labelling.py ./demo_configs/model/whisper_and_distil_whisper/run_pseudo_labelling.json
```

#### Model Pruning
```shell
python ./bin/model/whisper_and_distil_whisper/create_student_model.py ./demo_configs/model/whisper_and_distil_whisper/create_student_model.json
```

#### Model Distillation
```shell
python ./bin/model/whisper_and_distil_whisper/run_distillation.py ./demo_configs/model/whisper_and_distil_whisper/run_distillation.json
```

### Notes
I did this on the internal datasets which only contains Mandarin and Hokkien. So far 
the performance can be understood as reproduced the [original paper](
https://arxiv.org/abs/2311.00430):
* Full-sized Whiser (Small) CER on Mixed Full Test Data: 0.3033 
* Distil-Whisper (Small) CER on Mixed Full Test Data: 0.3039