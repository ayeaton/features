"""Evaluates the model"""

import argparse
import logging
import os

import numpy as np
import torch
from torch.autograd import Variable
import features.utils.utils as utils
from torch.utils.data import Dataset, DataLoader

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', help="Directory containing the dataset")
parser.add_argument('--model_dir', help="Directory containing params.json")
parser.add_argument('--restore_file', default='best', help="name of the file in --model_dir \
                     containing weights to load")

USE_CUDA = 1


def evaluate(model, val_loader, metrics_save, loss_func):
    """Evaluate the model on `num_steps` batches.
    Args:
        model: (torch.nn.Module) the neural network
        dataloader: (DataLoader) a torch.utils.data.DataLoader object that fetches data
        metrics: (dict) a dictionary of functions that compute a metric using the output and labels of each batch
    """

    # set model to evaluation mode
    model.eval()
    #loss_func = torch.nn.BCELoss()
    # summary for current eval loop
    summ = []

    # compute metrics over the dataset
    for i, val_batch in enumerate(val_loader):
      
        inputs,labels = val_batch
        outputs = model(utils.tovar(inputs))
        loss = loss_func(outputs, utils.tovar(labels))

        # extract data from torch Variable, move to cpu, convert to numpy arrays
        output_batch = outputs.data.cpu().numpy()
        labels_batch = labels.data.cpu().numpy()

        # compute all metrics on this batch
        summary_batch = {"accuracy":metrics_save["accuracy"](output_batch, labels_batch),
                         #"AUC":metrics_save["AUC"](output_batch, labels_batch),
                         #"mean_fpr":metrics_save["fpr"](output_batch, labels_batch),
                         #"mean_tpr":metrics_save["tpr"](output_batch, labels_batch),
                         "loss":loss.data[0]}
        summ.append(summary_batch)

    # compute mean of all metrics in summary
    metrics_mean = {metric:np.mean([x[metric] for x in summ]) for metric in summ[0]} 
    metrics_string = " ; ".join("{}: {:05.3f}".format(k, v) for k, v in metrics_mean.items())
    logging.info("- Eval metrics : " + metrics_string)
    return metrics_mean


if __name__ == '__main__':
    # Set the random seed for reproducible experiments
    torch.manual_seed(230)

    # Get the logger
    utils.set_logger(os.path.join(model_dir, 'evaluate.log'))

    # Create the input data pipeline
    logging.info("Creating the dataset...")

    test_dataset = data_loader.images_dataset(data_dir = data_directory, image_list_file = test_image_list,
                                 time_tile = 1)
    test_loader = DataLoader(dataset = test_dataset, batch_size = test_batch_size,
                                shuffle = True, num_workers = 8)
    logging.info("- done.")

    # Define the model and optimizer
    model = net.SimpleCNN()
    model.cuda()
    
    metrics_save = net.metrics_save

    logging.info("Starting evaluation")

    # Reload weights from the saved file
    utils.load_checkpoint(os.path.join(args.model_dir, args.restore_file + '.pth.tar'), model)
    
    
    # Evaluate
    test_metrics = evaluate(model, test_loader, metrics_save)
    save_path = os.path.join(model_dir, "metrics_test_{}.json".format(restore_file))
    utils.save_dict_to_json(test_metrics, save_path)