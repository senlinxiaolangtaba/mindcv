''' cross entorpy smooth '''
#import warnings
from mindspore import nn
from mindspore.ops import functional as F

class CrossEntropySmooth(nn.LossBase):
    '''
    Cross entropy loss with label smoothing.
    Apply softmax activation function to input `logits`, and uses the given logits to compute cross entropy
    between the logits and the label.

    Args:
        smoothing: Label smoothing factor, a regularization tool used to prevent the model
            from overfitting when calculating Loss. The value range is [0.0, 1.0]. Default: 0.0.
        aux_factor: Auxiliary loss factor. Set aux_fuactor > 0.0 if the model has auxilary logit outputs (i.e., deep supervision), like inception_v3.  Default: 0.0.
        reduction: Apply specific reduction method to the output: 'mean' or 'sum'. Default: 'mean'.
        weight (Tensor): Class weight. Shape [C]. A rescaling weight applied to the loss of each batch element. Data type must be float16 or float32.

    Inputs:
        logits (Tensor or Tuple of Tensor): Input logits. Shape [N, C], where N is # samples, C is # classes.
                Tuple of two input logits are supported in order (main_logits, aux_logits) for auxilary loss used in networks like inception_v3.
        labels (Tensor): Ground truth label. Shape: [N] or [N, C].
                (1) Shape (N), sparse labels representing the class indinces. Must be int type.
                (2) Shape [N, C], dense labels representing the ground truth class probability values, or the one-hot labels. Must be float type.
    '''
    def __init__(self, smoothing=0., aux_factor=0., reduction='mean', weight=None):
        super().__init__()
        self.smoothing = smoothing
        self.aux_factor = aux_factor
        self.reduction = reduction
        self.weight = weight

    def construct(self, logits, labels):
        loss_aux = 0

        if isinstance(logits, tuple):
            logits, aux = logits
            if self.aux_factor > 0:
                loss_aux = F.cross_entropy(aux, labels, weight=self.weight, reduction=self.reduction, label_smoothing=self.smoothing)
            else:
                print("There are two logit output, but the auxilary loss factor is 0.")
        elif self.aux_factor > 0:
            print("aux_factor > 0 but there is no auxilary logits.")

        loss_logits = F.cross_entropy(logits, labels, weight=self.weight, reduction=self.reduction, label_smoothing=self.smoothing)
        loss = loss_logits + self.aux_factor * loss_aux
        return loss
