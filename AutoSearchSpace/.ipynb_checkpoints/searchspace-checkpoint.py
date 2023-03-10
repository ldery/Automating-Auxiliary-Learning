import torch
import numpy as np
import torch.nn.functional as F
from config import Config
from torch.optim import SGD, Adam
import math
import os

def add_searchspace_args(parser):
	parser.add_argument('-prim-aux-lr', type=float, default=1e-4)
	parser.add_argument('-auxiliaries-lr', type=float, default=1e-4)
	parser.add_argument('-num-config-samples', type=int, default=16)
	parser.add_argument('-use-factored-model', action='store_true')
	parser.add_argument('-step-meta-every', type=int, default=1)
	parser.add_argument('-use-EG', action='store_true')
	parser.add_argument('-token_temp', type=float, default=1.0)
	parser.add_argument('-warmstart-path', type=str, default=None)
	parser.add_argument('-pure-transform', action='store_true')


def create_tensor(shape, init=0.0, requires_grad=True, is_cuda=True):
	inits = torch.ones(*shape) * init
	# Create the weights
	weights = inits.float().cuda() if is_cuda else inits.float()
	if requires_grad:
		weights.requires_grad = True
	return weights

import pdb
class SearchOptions(object):
	def __init__(
					self, config, prim_aux_lr, aux_lr, use_EG= False, step_every=1,
					use_factored_model=True, is_cuda=True, token_temp=1.0, warmstart_path=None,
					pure_transform=False
				):
		self.config = config  # Store in case
		self.weight_lr = prim_aux_lr
		self.aux_lr = aux_lr
		self.weights = {}
		self.step_every = step_every
		self.step_counter = 0
		self.pure_transform = pure_transform 

		num_stages = self.config.num_stages()
		base_shape = [1 for _ in range(num_stages)]
		all_dims = list(base_shape)
		self.stage_order = []
		for stage_id in range(num_stages):
			stage_name, ids_ = self.config.get_stage_w_name(stage_id)
			# Add the primary task to the output
			shape = list(base_shape)
			shape[stage_id] = len(ids_)
			st_weights = create_tensor(shape, init=int(use_EG), requires_grad=use_factored_model, is_cuda=is_cuda)
			self.weights[stage_name] = st_weights
			all_dims[stage_id] = shape[stage_id]
			self.stage_order.append(stage_name)
		self.weights['all'] = create_tensor(all_dims, init=int(use_EG), requires_grad=True, is_cuda=is_cuda)
		self.stage_order.append('all')
		self.valid_configurations = None
		self.create_mask_for_illegal(all_dims, is_cuda)

		self.prim_weight =  create_tensor((1,), init=int(use_EG), requires_grad=True, is_cuda=is_cuda)
		self.aux_weight = create_tensor((1,), init=int(use_EG), requires_grad=True, is_cuda=is_cuda)

		self.config_upstream_grad = create_tensor(all_dims,init=int(use_EG), requires_grad=False, is_cuda=is_cuda)
		self.prim_upstream_grad = create_tensor((1,), init=int(use_EG), requires_grad=False, is_cuda=is_cuda)
		self.aux_upstream_grad = create_tensor((1,), init=int(use_EG), requires_grad=False, is_cuda=is_cuda)

		self.use_EG = use_EG
		self.tau = token_temp
		if warmstart_path and (os.path.exists(warmstart_path)):
			self.load_state(warmstart_path)

		print('[STAT] We ended up with {} valid tasks'.format(len(self.valid_configurations)))

	def save_state(self, path):
		print('Saving SearchOpts state to : ', path)
		save_dict = {
			'weights': self.weights,
			'valid_configs': self.valid_configurations
		}
		torch.save(
			save_dict,
			path
		)

	def load_state(self, path):
		print('Loading SearchOpts state from : ', path)
		state_dict = torch.load(path)
		self.weights = state_dict['weights']
		for name, weight in self.weights.items():
			# Todo [ldery] - could do some sort of thresholding here if we wanted to that 
			# auxiliary tasks that have essentially low values previously will be set to zero
			if weight.requires_grad and (weight.grad is not None):
				with torch.no_grad():
					weight.grad.zero_()
	
		self.valid_configurations = state_dict['valid_configs']


	def get_valid_configs(self):
		return self.valid_configurations

	def get_all_and_out_relative(self, aux_configs):
		# gather all the likelihoods:
		values = []
		stage_name, _ = self.config.get_stage_w_name(3)
		with torch.no_grad():
			for conf_ in aux_configs:
				this_logit = (self.weights['all'][conf_[0], conf_[1], conf_[2], conf_[3]]).item()
				this_logit += (self.weights[stage_name][0, 0, 0, conf_[3]]).item()
				values.append(this_logit)
			values = F.softmax(torch.tensor(values), dim=-1)
			values = values.numpy().tolist()
			probas = {}
			for k, v in zip(aux_configs, values):
				probas[k] = v
		return probas

	def get_relative_probas(self, stage_id, stage_members, w_names=False):
		stage_name, stage_dict = self.config.get_stage_w_name(stage_id)
		if stage_members is None:
			stage_members = list(stage_dict.keys())
		with torch.no_grad():
			this_weights = (self.weights[stage_name]).squeeze()
			if this_weights.numel() == 1:
				this_weights = this_weights.unsqueeze(0)
			this_weights = this_weights.cpu().numpy()
			values = np.array([this_weights[id_] for id_ in stage_members])
			probas = F.softmax(torch.tensor(list(values)), dim=-1)
		if not w_names:
			return probas
		else:
			probas = probas.numpy().tolist()
			proba_dict = {}
			for k, v in stage_dict.items():
				proba_dict[v] = probas[k]
			return proba_dict
	
	def get_bert_relative(self, stage_id, tform_name, tform_id):
		stage_name, stage_dict = self.config.get_stage_w_name(stage_id)
		with torch.no_grad():
			if self.pure_transform:
				bias_ = {'None': float('-inf'), 'Replace': float('-inf'), 'Mask':float('-inf')}
				bias_[tform_name] = self.tau
			else:
				this_weights = (self.weights[stage_name]).squeeze().cpu().numpy()
				# We want to add ['None'=0.1, 'Replace'=0.1, 'Mask'=0.8] as a bias
				bias_ = {'None': 0, 'Replace': 0, 'Mask': 2.0794 * self.tau}
				bias_[tform_name] = bias_[tform_name] + this_weights[tform_id]
			values = np.array(list(bias_.values())) / self.tau
			probas = F.softmax(torch.tensor(list(values)), dim=-1).numpy().tolist()
			proba_dict = {}
			for k, v in zip(bias_.keys(), probas):
				proba_dict[k] = v
		return proba_dict

	def get_config_human_readable(self, config):
		name_ = ''
		for stage_id in range(len(config)):
			stage_name, ids_ = self.config.get_stage_w_name(stage_id)
			stage_ = "{}={}".format(stage_name, ids_[config[stage_id]])
			name_ = "{}|{}".format(name_, stage_) if len(name_) else stage_
		return name_
	
	def sample_configurations(self, num_samples):
		if num_samples >= len(self.valid_configurations):
			return self.valid_configurations
		idxs = np.random.choice(len(self.valid_configurations), size=num_samples, replace=False)
		return [self.valid_configurations[idx_] for idx_ in idxs]

	def create_mask_for_illegal(self, all_dims, is_cuda):
		assert len(all_dims) == 4, 'This assumes that there are only 4 stages. If not, please consider re-writing this function'
		self.valid_configurations = []
		# This is quite inefficient but since we only do it once, I think it's ok.
		# Will try to come up with a more polished version if it raises issues
		# This also assumes that there are only 4 stages.
		self.weights['mask'] = create_tensor(all_dims, init=0.0, requires_grad=False, is_cuda=is_cuda)
		self.stage_order.append('mask')
		neg_inf = float('-inf')
		for i in range(all_dims[0]):
			for j in range(all_dims[1]):
				for k in range(all_dims[2]):
					for l in range(all_dims[3]):
						if (self.config.is_illegal((i, j, k, l))):
							self.weights['mask'][i, j, k, l] = neg_inf
						else:
							self.valid_configurations.append((i, j, k, l))


	def get_weighttensor_nograd(self, softmax=True):
		with torch.no_grad():
			return self.get_weighttensor_wgrad(softmax=softmax)

	def get_weighttensor_wgrad(self, softmax=True):
		aux_config_tensor = sum([self.weights[name] for name in self.stage_order])
		full_ = torch.cat((self.prim_weight, self.aux_weight))
		if softmax:
			# Compute Normalization over all entries
			sm = F.softmax(full_, dim=-1)
			shape = aux_config_tensor.shape
			config_weights = F.softmax(aux_config_tensor.view(-1), dim=-1)
			config_weights = config_weights.view(*shape)
			return config_weights, sm[0], sm[1]
		else:
			return aux_config_tensor, self.prim_weight, self.aux_weight

	# Not the cleanest way to do this but it's ok for now
	def update_grad(self, config, grad):
		if isinstance(config, tuple):
			self.config_upstream_grad[config[0], config[1], config[2], config[3]].add_(grad)
		elif config == 'auxiliary':
			self.aux_upstream_grad.add_(grad)
		else:
			self.prim_upstream_grad.add_(grad)
	
	def clear_grads(self):
		self.config_upstream_grad.zero_()
		self.prim_upstream_grad.zero_()
		self.aux_upstream_grad.zero_()

	def set_weightensor_grads(self, upstream_grad_tensor, prim_upstream_grad, aux_upstream_grad):
		weight_tensor, prim_weight, aux_weight = self.get_weighttensor_wgrad(softmax=False)
		proxy_loss = (weight_tensor * upstream_grad_tensor).sum()
		proxy_loss.backward()

		proxy_loss = (prim_weight * prim_upstream_grad).sum()
		proxy_loss.backward()
		
		proxy_loss = (aux_weight * aux_upstream_grad).sum()
		proxy_loss.backward()


	def get_exp_update(self, weight, lr, is_output=False, factor=None):
		if factor is None:
			num_params = self.weights['all'].numel()
			factor = ((weight.numel() + int(is_output)) / num_params) / self.step_every
		return weight * torch.exp(-lr * weight.grad * factor)

	def update_weight(self, weight, lr):
		factor = 1.0 / self.step_every
		new_weight = weight - (lr * weight.grad * factor)
		weight.copy_(new_weight)
		weight.grad.zero_()

	def update_weighttensor(self):
		self.step_counter += 1
		self.set_weightensor_grads(self.config_upstream_grad, self.prim_upstream_grad, self.aux_upstream_grad)
		if (self.step_counter % self.step_every) == 0:
			output_norm, all_norm = None, None
			with torch.no_grad():
				for key, weight in self.weights.items():
					if not weight.requires_grad:
						continue
					if weight.grad is None:
						weight.grad = torch.zeros_like(weight)
					self.update_weight(weight, self.aux_lr)

				# Perform updates on the primary weight
				assert self.prim_weight.grad is not None, 'Prim Weight should have gradients'
				self.update_weight(self.prim_weight, self.weight_lr)
				self.update_weight(self.aux_weight, self.weight_lr)

		self.clear_grads()


	def is_tokenlevel(self, output_id):
		return self.config.is_tokenlevel(output_id)
	
	def is_tokenlevel_lm(self, output_id):
		return self.config.is_tokenlevel_lm(output_id)

	def is_dot_prod(self, output_id):
		return self.config.is_dot_prod(output_id)

	def is_sent_classf(self, output_id):
		return self.config.is_sent_classf(output_id)
	
	def get_vocab(self, output_id):
		return self.config.get_vocab(output_id)


def run_tests():
	try:
		full_config = Config('full')
		searchOps = SearchOptions(full_config, 1.0)
		assert np.prod(searchOps.weights['all'].shape) == full_config.total_configs, 'All Tensor has wrong shape'
		assert np.prod(searchOps.weights['mask'].shape) == full_config.total_configs, 'Mask Tensor has wrong shape'
		num_valid = (searchOps.weights['mask'] == 0).sum().item()
		assert num_valid == 352, 'This is a hard coded number of valid configurations'
		upstream_grad_tensor = torch.ones_like(searchOps.weights['all']) * 0.5
		prim_upstream_grad = torch.ones_like(searchOps.prim_weight) * 0.5
		searchOps.set_weightensor_grads(upstream_grad_tensor, prim_upstream_grad)
		# Doing the gradient checking.
		have_grads = [v.grad is not None for k, v in searchOps.weights.items()][:-1]
		assert np.all(have_grads), 'All tensors except mask must have grad enabled'
		assert searchOps.prim_weight.grad is not None, 'Prim weight has no grad'
		print(searchOps.get_config_human_readable((0, 1, 1, 0)))
		msg = 'Passed.'
	except:
		msg = 'Failed.'
	print("run_tests : {}".format(msg))

if __name__ == '__main__':
	run_tests()
