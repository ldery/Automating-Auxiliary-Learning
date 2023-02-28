## Notes on installation ##

Setup original don't stop pre-training environment
conda env create -f environment.yml
conda activate domains

Then there is the new packages that I have added, information about these will be found in aang_environment_august30th2022.yml
and you can try to look up the appropriate versions in that  file if you try to run after the first installation above and run into package not found errors.
Notes on Running
The run commands are in hyperparam_search.py (I have included both the config for the paper experiment and the best hpconfig that I found for each type of task for each type of task)
if you run hyperparam_search.py with the appropriate settings, results will be saved as a csv in resultsSheet which you can analyze
I've provided the data for 1 dataset citation_intent lmk if you want more details about the other datasets
I usually run experiments on A100 or A6000 - large memory devices are preferred. If you have memory issues you can increase -grad-accum-steps which will accumulate gradients over more steps with smaller batches
Let me know if you end up having any more questions / concerns :slightly_smiling_face:
NB : info is checkpointed to a folder autoaux_outputs - which can get big - you can either clear it out regularly or just reduce the checkpoint frequency in the code.