"""
This is the demo code that uses hydra

Author: Tulio Patriota
"""

from pathlib import Path

import hydra
import numpy as np
import pandas as pd
import torch
import torchvision
from hydra.utils import to_absolute_path as abspath
from omegaconf import DictConfig
from torch import nn
from torch.utils import data
from torchvision import transforms

from utils.Accumulator import Accumulator
from utils.FootballDataset import FootballDataset

# from d2l import torch as d2l


@hydra.main(config_path="../config", config_name="main")
def train_model(config: DictConfig):
    """Function to train the model"""

    input_path = abspath(config.processed.path)
    output_path = abspath(config.final.path)

    print(f"Train modeling using {input_path}")
    print(f"Model used: {config.model.name}")
    print(f"Save the output to {output_path}")

    # Step 1. Load the dataset and select the parameters/target
    num_params = config.model.num_params
    cat_params = config.model.cat_params
    target = ["pts"]

    print("Dataset loaded.")

    # Step 2. Create the data loaders
    train_iter, test_iter = load_data_football(
        config.model.data_iter_size, num_params, cat_params, target, input_path
    )
    for X, y in train_iter:
        input_size = X.shape[1]
    # Step 3. Instatiate the network

    # PyTorch does not implicitly reshape the inputs. Thus we define the flatten
    # layer to reshape the inputs before the linear layer in our network
    net = nn.Sequential(nn.Flatten(), nn.Linear(input_size, 3))

    def init_weights(m):
        if type(m) == nn.Linear:
            nn.init.normal_(m.weight, std=0.01)

    net.apply(init_weights)

    # Step 4. Define loss
    loss = nn.CrossEntropyLoss()

    # Step 5. Define the optimization algorithm
    trainer = torch.optim.SGD(net.parameters(), lr=config.model.learning_rate)

    # Step 6. Train the model
    print("Starting training...\n")
    num_epochs = config.model.num_epochs
    for epoch in range(num_epochs):
        train_metrics = train_epoch(net, train_iter, loss, trainer)
        test_acc = evaluate_accuracy(net, test_iter)
        print(
            f"Epoch {epoch}: training_loss = {train_metrics[0]}, train_acc = {train_metrics[1]}, test_acc = {test_acc}\n"
        )

    train_loss, train_acc = train_metrics
    # assert train_loss < 0.3, train_loss
    assert train_acc <= 1 and train_acc > 0.3, train_acc
    assert test_acc <= 1 and test_acc > 0.3, test_acc


# Data loading
def load_data_football(
    batch_size, num_par, cat_par, target, input_path
):  # @save
    """Load the dataset into memory."""
    # Load dataset
    dataset = FootballDataset(
        cat_par, num_par, target, csv_file=input_path
    )  # ,league = ["La liga"], season = [2015,2016] )

    # Split into training and test
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    trainset, testset = data.random_split(dataset, [train_size, test_size])

    # Dataloaders
    return (
        data.DataLoader(trainset, batch_size=batch_size, shuffle=True),
        data.DataLoader(testset, batch_size=batch_size, shuffle=False),
    )


# Function to train epoch
def train_epoch(net, train_iter, loss, updater):  # @save
    # Set the model to training mode
    if isinstance(net, torch.nn.Module):
        net.train()
    # Sum of training loss, sum of training accuracy, no. of examples
    metric = Accumulator(3)
    for X, y in train_iter:
        # Compute gradients and update parameters
        y_hat = net(X)
        loss_ = loss(y_hat, y)
        if isinstance(updater, torch.optim.Optimizer):
            # Using PyTorch in-built optimizer & loss criterion
            updater.zero_grad()
            loss_.backward()
            updater.step()
            metric.add(float(loss_) * len(y), accuracy(y_hat, y), y.numel())
        else:
            # Using custom built optimizer & loss criterion
            loss_.sum().backward()
            updater(X.shape[0])
            metric.add(float(loss_.sum()), accuracy(y_hat, y), y.numel())
    # Return training loss and training accuracy
    return metric[0] / metric[2], metric[1] / metric[2]


# Functions to evaluate accuracy
def evaluate_accuracy(net, data_iter):  # @save
    """Compute the accuracy for a model on a dataset."""
    if isinstance(net, torch.nn.Module):
        net.eval()  # Set the model to evaluation mode
    metric = Accumulator(2)  # No. of correct predictions, no. of predictions

    with torch.no_grad():
        for X, y in data_iter:
            metric.add(accuracy(net(X), y), y.numel())
    return metric[0] / metric[1]


def accuracy(y_hat, y):  # @save
    """Compute the number of correct predictions."""
    if len(y_hat.shape) > 1 and y_hat.shape[1] > 1:
        y_hat = y_hat.argmax(axis=1)
    cmp = y_hat.type(y.dtype) == y
    return float(cmp.type(y.dtype).sum())


if __name__ == "__main__":
    train_model()
