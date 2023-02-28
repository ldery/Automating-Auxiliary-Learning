from copy import deepcopy


HYPER_CONFIG_PARTIAL_BIG = {
		'auxlr': [0.1, 1.0],
		'soptlr': [0.01, 0.1],
		'classflr': [1e-4, 1e-3],
		'wfrac': [0.06],
		'nconf_samp': [3, 6],
		'primbsz': [128],
		'auxbsz': [256]
}
HYPER_CONFIG_PARTIAL_BIG_1 = deepcopy(HYPER_CONFIG_PARTIAL_BIG)
HYPER_CONFIG_PARTIAL_BIG_1['nconf_samp'] = [3]


HYPER_CONFIG_HYPERPARTISAN = deepcopy(HYPER_CONFIG_PARTIAL_BIG)
HYPER_CONFIG_HYPERPARTISAN['primbsz'] = [64]
HYPER_CONFIG_HYPERPARTISAN['auxbsz'] = [128]

HYPER_CONFIG_PARTIAL_BIG_1 = {
		'auxlr': [1.0, 0.1],
		'soptlr': [0.1],
		'classflr': [1e-3, 1e-4],
		'wfrac': [0.06],
		'nconf_samp': [6],
		'primbsz': [128],
		'auxbsz': [512, 1024]
}


HYPER_CONFIG_HYPERPARTISAN_1 = deepcopy(HYPER_CONFIG_PARTIAL_BIG_1)
HYPER_CONFIG_HYPERPARTISAN_1['primbsz'] = [64]
HYPER_CONFIG_HYPERPARTISAN_1['auxbsz'] = [128]


HYPER_CONFIG_PARTIAL_MULTI = {
		'auxlr': [0],
		'soptlr': [0],
		'classflr': [1e-4, 1e-3],
		'wfrac': [0.06],
		'nconf_samp': [3, 6],
		'primbsz': [128],
		'auxbsz': [256]
}


HYPER_CONFIG_PARTIAL_ONETASK = {
		'auxlr': [0.1],
		'soptlr': [0.01, 0.1, 1.0],
		'wfrac': [0.06],
		'primbsz': [128],
		'auxbsz': [256]
}
# deepcopy(HYPER_CONFIG_PARTIAL_BIG)
HYPER_CONFIG_PARTIAL_ONETASK['nconf_samp'] = [1]
HYPER_CONFIG_PARTIAL_ONETASK['classflr'] = [1e-3, 1e-4, 5e-5]

HYPER_CONFIG_HYPERPARTISAN_ONETASK = deepcopy(HYPER_CONFIG_PARTIAL_ONETASK)
HYPER_CONFIG_HYPERPARTISAN_ONETASK['primbsz'] = [64]
HYPER_CONFIG_HYPERPARTISAN_ONETASK['auxbsz'] = [128]


HYPER_CONFIG_FULL = {
		'auxlr': [0.1, 5e-1, 1.0],
		'soptlr': [1e-1],
		'classflr': [1e-3, 1e-4, 3e-3, 5e-3, 1e-2],
		'nconf_samp': [3, 6],
		'primbsz': [128],
		'auxbsz': [256]
}


HYPER_CONFIG_TEST = {
		'auxlr': [0.1],
		'soptlr': [1e-1],
		'classflr': [3e-3],
		'wfrac': [0.06],
		'nconf_samp': [1],
		'primbsz': [128],
		'auxbsz': [256]
}

CONFIG_NAMES = [
	"full",  "partial",
	"partial_big", "partial_onetask",
	"partial_hyperpartisan", "partial_big_1",
	"partial_big_multi", 'partial_hyperpartisan_onetask',
	'partial_hyperpartisan_1', 'all_data',
	'ct_best_ours', 'ct_best_gpt', 'ct_best_joint', 
	'ct_best_xlnet', 'ct_best_tapt'
]

def get_hyper_config(config_name):
	if config_name == 'full':
		return HYPER_CONFIG_FULL
	elif config_name == 'partial':
		return HYPER_CONFIG_PARTIAL
	elif config_name == 'partial_big':
		return HYPER_CONFIG_PARTIAL_BIG
	elif config_name == 'partial_big_1':
		return HYPER_CONFIG_PARTIAL_BIG_1
	elif config_name == 'partial_hyperpartisan_1':
		return HYPER_CONFIG_HYPERPARTISAN_1
	elif config_name == 'partial_onetask':
		return HYPER_CONFIG_PARTIAL_ONETASK
	elif config_name == 'partial_hyperpartisan':
		return HYPER_CONFIG_HYPERPARTISAN
	elif config_name == 'partial_hyperpartisan_onetask':
		return HYPER_CONFIG_HYPERPARTISAN_ONETASK
	elif config_name == 'partial_big_multi':
		return HYPER_CONFIG_PARTIAL_MULTI



# Modified appropriately
CITATION_INTENT = {
	'primtaskid': 'citation_intent',
	'trainfile':  'datasets/citation_intent/train.jsonl',
	'devfile':    'datasets/citation_intent/dev.jsonl',
	'testfile':   'datasets/citation_intent/test.jsonl',
	'taskdata':   'datasets/citation_intent/train.txt',
	'domaindata': 'datasets/citation_intent/domain.10xTAPT.txt',
	'metric':     'f1',
}
