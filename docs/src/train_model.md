Module src.train_model
======================
Function to train a deep learning neural network using PyTorch and softmax for match result prediction. Model parameters are defined in the config files.

Author: Tulio Patriota

Functions
---------

    
`accuracy(y_hat, y)`
:   Compute the number of correct predictions.

    
`evaluate_accuracy(net, data_iter)`
:   Compute the accuracy for a model on a dataset.

    
`load_data_football(batch_size, num_par, cat_par, target, input_path)`
:   Load the dataset into memory.

    
`train_epoch(net, train_iter, loss, updater)`
:   

    
`train_model(config: omegaconf.dictconfig.DictConfig)`
:   Function to train the model
    args:
        config_path: path to configuration files.
        config_name: config file name.