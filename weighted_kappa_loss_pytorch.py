import torch
class SoftArgmax1D(torch.nn.Module):
    """
    Implementation of a 1d soft arg-max function as an nn.Module, so that we can differentiate through arg-max operations.
    """
    def __init__(self, base_index=0, step_size=1):
        """
        The "arguments" are base_index, base_index+step_size, base_index+2*step_size, ... and so on for
        arguments at indices 0, 1, 2, ....
        Assumes that the input to this layer will be a batch of 1D tensors (so a 2D tensor).
        :param base_index: Remember a base index for 'indices' for the input
        :param step_size: Step size for 'indices' from the input
        """
        super(SoftArgmax1D, self).__init__()
        self.base_index = base_index
        self.step_size = step_size
        self.softmax = torch.nn.Softmax(dim=1)


    def forward(self, x):
        """
        Compute the forward pass of the 1D soft arg-max function as defined below:
        SoftArgMax(x) = \sum_i (i * softmax(x)_i)
        :param x: The input to the soft arg-max layer
        :return: Output of the soft arg-max layer
        """
        smax = self.softmax(x)
        end_index = self.base_index + x.size()[1] * self.step_size
        indices = torch.arange(start=self.base_index, end=end_index, step=self.step_size).type(torch.DoubleTensor)
        return torch.round(torch.matmul(smax, indices))
class WeightedKappaLoss(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.softargmax = SoftArgmax1D()
    def forward(self, preds, true,nb_classes = None):
        nb_classes = preds.shape[1]
        pred = self.softargmax(preds.view(1,-1).type(torch.cuda.FloatTensor))
        pred = pred.type(torch.cuda.FloatTensor)
        pred.requires_grad = True
        confusion_matrix = torch.empty([nb_classes, nb_classes],requires_grad = True)
        for t, p in zip(pred.view(-1), true.view(-1)):
            confusion_matrix[p.long(), t.long()] += 1
        weights = torch.empty([nb_classes,nb_classes],requires_grad = True)
        for i in range(len(weights)):
            for j in range(len(weights)):
                weights[i][j] = float(((i-j)**2)/(len(weights)-1)**2)
        #Histograms
        true_hist= torch.empty([nb_classes],requires_grad = True)
        for item in true: 
            true_hist[item]+=1
        pred_hist=torch.empty([nb_classes],requires_grad = True)
        for item in pred: 
            pred_hist[int(item)]+=1
        E = torch.ger(true_hist,pred_hist)
        E = E/E.sum()
        confusion_matrix = confusion_matrix/confusion_matrix.sum()
        num = (confusion_matrix*weights).sum()
        den = (E*weights).sum()
        return num/den
