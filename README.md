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



### Notes on Running
The run commands are in hyperparam_search.py

If you run hyperparam_search.py with the appropriate settings, results will be saved as a csv in resultsSheet which you can analyze
Data for 1 dataset citation_intent/ACL-ARC has been provided. Data for other tasks can be obtained by following the instructions listed here : 

https://github.com/allenai/dont-stop-pretraining#readme
 
Experiments were run on A100 or A6000 - large memory devices are preferred because of meta-learning approach. If you have memory issues you can increase 

`-grad-accum-steps`

which will accumulate gradients over more steps with smaller batches

Results are checkpointed into a folder called autoaux_outputs - which can get big - you can either clear it out regularly or just reduce the checkpoint frequency in the code.
