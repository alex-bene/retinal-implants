import torch
import torchvision
from torchvision.models import resnet

class ResNetMNIST(resnet.ResNet):
	def __init__(self, pretrained=True, feature_extraction=True, load_state_path=None):
		super().__init__(block=resnet.BasicBlock, layers=[2, 2, 2, 2])

		resnet18_path = 'https://download.pytorch.org/models/resnet18-5c106cde.pth'

		if pretrained:
			state_dict = torch.utils.model_zoo.load_url(resnet18_path)
			self.load_state_dict(state_dict)

		if feature_extraction:
			for param in self.parameters():
				param.requires_grad = False

		# change output layer to fit MNIST (10 classes)
		num_ftrs = self.fc.in_features
		self.fc  = torch.nn.Linear(num_ftrs, 10)

		self.input_size = 224

		self.load_state(load_state_path)

		if torch.cuda.is_available():
			self.cuda()

	def load_state(self, load_state_path=None):
		if load_state_path is not None:
			self.load_state_dict(torch.load(load_state_path))

	def freeze_layers(self, layers):
		if isinstance(layers, basestring ): # all until that layer
			found_name = False
			for name, params in self.named_parameters():
				if name == layers:
					found_name = True
				params.requires_grad = found_name
		elif isinstance(layers, int): # the first {layers} layers
			nop = len(self.named_parameters()) # number of parameters
			found_layer = False
			for cnt, params in enumerate(self.parameters()):
				if (nop - cnt) == layers:
					found_name = True
				params.requires_grad = found_name
		elif isinstance(layers, list) and all(isinstance(layer, basestring) for layer in layers): # only those with matching names
			for name, params in self.named_parameters():
				params.requires_grad = (name in layers)
		elif isinstance(layers, list) and all(isinstance(layer, int) for layer in layers): # only those with matching names
			for cnt, params in enumerate(self.parameters()):
				params.requires_grad = ((nop - cnt) in layers)
		else:
			raise TypeError('The argument must be a model parameter name or a list of them or an integer or a list of them')

	def print_trainable_params(self):
		params_to_update = model.parameters()
		print("Parameters to train:")
		cnt = 0
		for name, param in self.model.named_parameters():
			if param.requires_grad == True:
				print("\t", name)
				cnt += 1
		print(f"There are {cnt} trainable parameters")
		