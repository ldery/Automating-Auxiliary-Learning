# Automating-Auxiliary-Learning
Code associated with the ICLR2023 paper AANG: [Automating Auxiliary Learning](https://openreview.net/forum?id=vtVDI3w_BLL)

## Citation


```bibtex
@article{dery2022aang,
  title={AANG: Automating Auxiliary Learning},
  author={Dery, Lucio M and Michel, Paul and Khodak, Mikhail and Neubig, Graham and Talwalkar, Ameet},
  journal={arXiv preprint arXiv:2205.14082},
  year={2022}
}
```

## Notes on Installation

First, get original environment associated with the Dont-Stop-Pretraining paper.
```bash
conda env create -f environment.yml
conda activate domains
```
Note that extra packages can be found in this file :
```
aang_environment_august30th2022.yml
```
You can look up the appropriate versions in the above file if you try to run after the first installation above and run into package not found errors.

## Data Formatting
See datasets/* for an example dataset.

Code expects {train, test, dev}.jsonl as the data formatting.

Code for creating auxiliary objectives expects the train.jsonl to be converted to .txt file via simply concatenating the text (without the labels) from the train.jsonl file.

To add a new dataset, create a dict like at the end of the hyper_search_configs.py file that has all the information about the task data. Also update the `get_task_info` method in hyperpparam_search.py with the new task details.


## Running
command flags are formatted {example}{description}

```
python hyperparam_search.py
-task              {citation_intent}{name of task. These are listed in the hyperparam_search.py function -- get_task_info()}
-base-spconfig     {citation.supervised}{name of the search space -- list of search space names in AutoSearchSpace/searchspace_options.py in the get_config()}       
-patience          {20}{How long to keep running after validation set performance has plateaud before ending trianing} 
-grad-accum-steps  {4}{Number of gradient accumulation steps. This takes into already takes into account the total batch size so no need to update that if this is updated}
-exp-name          {SUPERVISED}{Name given to the experiment}
-gpu-list          {"[0, 1]"}{string array of the list of gpus to use. The script will automatically split hyper-parameters runs amongst these gpus} 
-hyperconfig       {partial_big}{Name of the hyper-parmeter config to explore. List is present in hyper_search_configs.py get_hyper_config(). }
-runthreads        {}{this is a flag. Turn this off if experiments have already been run and you just want to re-aggregate results}
-pure-transform    {}{this is a flag. This determines whether we start the corruption Transforms are pure transforms (replace only, mask only) verus mixed transforms as with BERT}
```
To run a single hyper-parameter configuration -- inspect the `get_base_runstring` function from  `hyperparam_search.py` and populate with your hand designed hyper-parameters.

### Important hyper-parameters
```
soptlr : Learning rate for weighting between primary and auxiliary objectives
aux-lr : Learning rate for weighting amongst auxiliary objectives. 
classflr : Overall learning rate for task.
```
Hyper-parameters for fitting the dev-head as in [META-TARTAN](https://arxiv.org/abs/2109.07437) can be found in the function AutoSearchSpace/modelling.py - add_modelling_options(). They are set to the defaults used in the META-TARTAN paper. 

To remove meta-learning and just use static multitasking just set `soptlr = aux-lr = 0` and the default equalized weightings will be used. Note that the current implementaiton of static multitasking is not faster than the meta-learning approach because we just set the weighting learning rate to 0 (all the overhead from computing meta-gradients is still incurred). Users are free to re-implement multitasking efficiently. 


### Addendums on Running
The run commands are in hyperparam_search.py

If you run hyperparam_search.py with the appropriate settings, results will be saved as a csv in resultsSheet which you can analyze
Data for 1 dataset citation_intent/ACL-ARC has been provided. Data for other tasks can be obtained by following the instructions listed here : 

https://github.com/allenai/dont-stop-pretraining#readme
 
Experiments were run on A100 or A6000 - large memory devices are preferred because of meta-learning approach. If you have memory issues you can increase 

`-grad-accum-steps`

which will accumulate gradients over more steps with smaller batches

Results are checkpointed into a folder called autoaux_outputs - which can get big - you can either clear it out regularly or just reduce the checkpoint frequency in the code.


## Checkpoints
The best checkpoints for [ACL-ARC](https://drive.google.com/file/d/1U8I2kHjHm4Yek0a3Tbog-ugQmC08svLg/view?usp=sharing) and [HYPERPARTISAN](https://drive.google.com/file/d/1Dc2CJTJGjV6V5bQoUVDF22Zw5WJ8m4fh/view?usp=sharing) tasks are linked here.
