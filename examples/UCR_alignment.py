"""
Created on Oct  2019

author: ronsha
"""

import os
import sys
module_path = os.path.abspath(os.path.join('..'))
import argparse

if module_path not in sys.path:
    sys.path.append(module_path)

# From other libraries
import numpy as np

# From tensorflow
from tensorflow.keras import backend as K

# From helper
from helper.util import get_dataset_info, print_NCC_results, get_test_results
from helper.plotting import plot_signals
from helper.UCR_loader import load_UCR_data

# models
from models.train_model import run_alignment_network


def argparser():
    parser = argparse.ArgumentParser(description='Process args')
    parser.add_argument('--tess_size', type=int, default=16,
                        help="CPA velocity field partition")
    parser.add_argument('--smoothness_prior', type=bool, default=True,
                        help="smoothness prior flag")
    parser.add_argument('--lambda_smooth', type=float, default=0.5,
                        help="lambda_smooth, larger values -> smoother warps")
    parser.add_argument('--lambda_var', type=float, default=0.1,
                        help="lambda_var, larger values -> larger warps")
    parser.add_argument('--n_recurrences', type=int, default=1,
                        help="number of recurrences of R-DTAN")
    parser.add_argument('--zero_boundary', type=bool, default=True,
                        help="zero boundary constrain")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = argparser()

    # data
    datadir = "data/"
    dataset_name = "ECGFiveDays"

    X_train, X_test, y_train, y_test = load_UCR_data(datadir, dataset_name)
    print("y_train.shape", y_train.shape)
    # Data info
    input_shape, n_classes = get_dataset_info(dataset_name, X_train, X_test, y_train, y_test, print_info=True)

    # args
    plot_signals_flag = True
    # run network - args holds all training related parameters
    DTAN = run_alignment_network(X_train, y_train, args)

    # Align data - forward pass the data through the network
    # create transformer function
    DTAN_aligner = K.function(inputs=[DTAN.input], outputs=[DTAN.layers[-1].output])

    X_train_aligned = np.squeeze(DTAN_aligner([X_train]))
    X_test_aligned = np.squeeze(DTAN_aligner([X_test]))

    # plot results
    if plot_signals_flag:
        # Plot test data
        plot_signals(X_test, X_test_aligned, y_test, dataset_name=dataset_name)