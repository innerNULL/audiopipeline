# My Implementations' Archive

## Archive Index
### Reproduced Papers
* [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675) 
    * [Document](https://github.com/innerNULL/mia/tree/main/bin/evaluation/text_summarisation)
    * [Run Evaluation](https://github.com/innerNULL/mia/blob/main/bin/evaluation/text_summarisation/eval_all_in_one_standalone.py)
* [Distil-Whisper: Robust Knowledge Distillation via Large-Scale Pseudo Labelling](https://arxiv.org/abs/2311.00430) 
    * [Document](https://github.com/innerNULL/mia/tree/main/bin/model/whisper_and_distil_whisper)
    * [Run Pseudo Labelling](https://github.com/innerNULL/mia/blob/main/bin/model/whisper_and_distil_whisper/run_pseudo_labelling.py)
    * [Initialize Distilled Whisper](https://github.com/innerNULL/mia/blob/main/bin/model/whisper_and_distil_whisper/create_student_model.py)
    * [Run Distillation](https://github.com/innerNULL/mia/blob/main/bin/model/whisper_and_distil_whisper/run_distillation.py)
* [SlimPajama-DC- Understanding Data Combinations for LLM Training](https://arxiv.org/abs/2309.10818)
    * [Run ETL](https://github.com/innerNULL/mia/tree/main/bin/etl/dataset/text_corpus/text_corpus_slimpajama_dc_processor.py)

### Model Training/Inference Runners
* [Distil-Whisper: Robust Knowledge Distillation via Large-Scale Pseudo Labelling](https://arxiv.org/abs/2311.00430) 
    * [Document](https://github.com/innerNULL/mia/tree/main/bin/model/whisper_and_distil_whisper)
    * [Run Pseudo Labelling](https://github.com/innerNULL/mia/blob/main/bin/model/whisper_and_distil_whisper/run_pseudo_labelling.py)
    * [Initialize Distilled Whisper](https://github.com/innerNULL/mia/blob/main/bin/model/whisper_and_distil_whisper/create_student_model.py)
    * [Run Distillation](https://github.com/innerNULL/mia/blob/main/bin/model/whisper_and_distil_whisper/run_distillation.py)
* [flan-T5](https://arxiv.org/abs/2210.11416)
    * [Document](https://github.com/innerNULL/mia/tree/main/bin/model/flan_t5)
    * [Fine-Tune](https://github.com/innerNULL/mia/tree/main/bin/model/flan_t5/finetune.py)
    * [Inference](https://github.com/innerNULL/mia/tree/main/bin/model/flan_t5/inference.py)
* LLM
    * [Document](https://github.com/innerNULL/mia/tree/main/bin/model/llm)
    * [Fine-Tune](https://github.com/innerNULL/mia/tree/main/bin/model/llm/finetune.py)

### Crawlers
#### [Audio Corpus Crawlers](https://github.com/innerNULL/mia/tree/main/bin/crawl/audio)

### ETL
* Line-Based Splitter to Generate Train/Dev/Test Dataset
    * `bash ./bin/etl/train_dev_test_splitter_for_lines_data.sh ${DATA_LINES_PATH} ${DEV_DATA_SIZE} ${TEST_DATA_SIZE}`
* SlimPajama-DC Text Corpus Low-Length Filtering and Deduplication
    * `python ./bin/etl/dataset/text_corpus/text_corpus_slimpajama_dc_processor.py ./bin/etl/dataset/text_corpus/text_corpus_slimpajama_dc_processor.json`


