# process hdf5 weight files
"""
import sys
sys.path.append("tf2_migration/")
from process_hdf5 import *
end_epoch=19
"""
import numpy as np
import matplotlib.pyplot as plt
import h5py
import os

# eventually create loop
# for f in fullconn_w:
# hf = h5py.File(f, 'r')
def basic_w_vis():
    hf = h5py.File("tf2_testing/LIF/p50/test_epoch_0.hdf5",'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_cell = n2.get('lif_cell')
    in_w = lif_cell.get('input_weights:0')
    in_w = np.array(in_w)
    rec_w = lif_cell.get('recurrent_weights:0')
    rec_w = np.array(rec_w)

    # plot to check that distribution of weights is lognormal
    # (or that there are a lot of zeros if the matrix is sparse)
    fig, axes = plt.subplots(2)
    axes[0].hist(in_w)
    axes[0].set_title('input weights')
    axes[1].hist(rec_w)
    axes[1].set_title('recurrent weights')
    fig.subplots_adjust(hspace=.5)
    plt.show()
    plt.savefig('tf2_testing/LIF/p50/test_epoch_0_weights.png')

def LIF_EI_begin_end_compare(epoch):
    begin_fname = "tf2_testing/LIF_EI/begin_epoch_" + str(epoch) + ".hdf5"
    hf = h5py.File(begin_fname,'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_ei = n2.get('lif_ei')
    rec_w = lif_ei.get('recurrent_weights:0')
    begin_rec_w = np.array(rec_w)

    print("count of zeros at beginning of epoch:")
    print(begin_rec_w[begin_rec_w==0].shape[0])
    begin_diag = begin_rec_w.diagonal()
    print("count of self-recurrent synapses that are zero")
    print(begin_diag[begin_diag==0].shape[0])
    print("e:i synapses")
    print(begin_rec_w[begin_rec_w>0].shape[0])
    print(begin_rec_w[begin_rec_w<0].shape[0])

    end_fname = "tf2_testing/LIF_EI/end_epoch_" + str(epoch) + ".hdf5"
    hf = h5py.File(end_fname,'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_ei = n2.get('lif_ei')
    rec_w = lif_ei.get('recurrent_weights:0')
    end_rec_w = np.array(rec_w)

    print("count of zeros at end of epoch:")
    print(end_rec_w[end_rec_w==0].shape[0])
    end_diag = end_rec_w.diagonal()
    print("count of self-recurrent synapses that are zero")
    print(end_diag[end_diag==0].shape[0])
    print("e:i synapses")
    print(end_rec_w[end_rec_w>0].shape[0])
    print(end_rec_w[end_rec_w<0].shape[0])

    fig, axes = plt.subplots(2)
    axes[0].hist(begin_rec_w)
    axes[0].set_title('epoch beginning weights')
    axes[1].hist(end_rec_w)
    axes[1].set_title('epoch ending weights')
    fig.subplots_adjust(hspace=.5)
    plt.show()
    out_fname = "tf2_testing/LIF_EI/compare_epoch_" + str(epoch) + "_weights.png"
    plt.savefig(out_fname)

def plot_rewiring_over_time(end_epoch):
    # using only epoch beginnings, plus the final epoch end
    data_path = "tf2_testing/LIF_EI/rewiring/"
    filelist = [];
    for file in os.listdir(data_path):
        if file.endswith(".hdf5"):
            if file.startswith("begin"):
                filelist.append(os.path.join(data_path, file))
        #if file.endswith(str(end_epoch) + ".hdf5"):
            #filelist.append(os.path.join(dir, file))

    avg_i_w = []
    max_i = []
    avg_e_w = []
    max_e = []
    conn = []

    # goodness, for now loss is handwritten
    loss = [0.5269,0.4914,0.4849,0.4924,0.4758,0.4645,0.4351,0.4145,0.3664,0.3753,0.3454,0.3763,0.3802,0.3478,0.3393,0.3356,0.3011,0.2846,0.2883,0.2765]

    for idx in range(len(filelist)):
        fname = data_path + "begin_epoch_" + str(idx) + ".hdf5"
        hf = h5py.File(fname)
        n1 = hf.get('rnn')
        n2 = n1.get('rnn')
        lif_ei = n2.get('lif_ei')
        rec_w = lif_ei.get('recurrent_weights:0')
        rec_w = np.array(rec_w)
        zero_ct = rec_w[rec_w==0].shape[0]
        total_ct = np.size(rec_w)
        conn.append((total_ct - zero_ct)/float(total_ct))
        avg_i_w.append(np.mean(rec_w[rec_w<0]))
        avg_e_w.append(np.mean(rec_w[rec_w>0]))
        max_i.append(np.amin(rec_w[rec_w<0]))
        max_e.append(np.amax(rec_w[rec_w>0]))
        if idx==0:
            begin_w_dist = rec_w
        if idx==len(filelist)-1:
            end_w_dist = rec_w

    fig, ax = plt.subplots(4, figsize=(6, 7))
    fig.suptitle("LIF with unconstrained rewiring")

    ax[0].hist(begin_w_dist.flatten(), bins=50, fc=(0, 0, 1, 0.5), label="initial")
    ax[0].hist(end_w_dist.flatten(), bins=50, fc=(1, 0, 0, 0.5), label="end")
    ax[0].set_xlabel("weights")
    ax[0].set_ylabel("counts")
    ax[0].legend(prop={'size': 5})

    ax[1].plot(avg_e_w, 'b-', label="mean e weight")
    ax[1].plot(max_e, 'b*', label="highest e weight")
    ax[1].plot(avg_i_w, 'r-', label="mean i weight")
    ax[1].plot(max_i, 'r*', label="lowest i weight")
    ax[1].set_xlabel("epoch")
    ax[1].set_ylabel("weight")
    ax[1].legend(prop={'size': 5})

    ax[2].plot(conn, label = "recurrent connectivity")
    ax[2].set_xlabel("epoch")
    ax[2].set_ylabel("percent")
    ax[2].legend(prop={'size': 5})

    ax[3].plot(loss)
    ax[3].set_xlabel("epoch")
    ax[3].set_ylabel("total loss")

    fig.subplots_adjust(hspace=1)
    fig.subplots_adjust(hspace=1)
    plt.draw()
    plt.savefig(data_path + "rewiring_over_time.png", dpi=300)

def plot_histogram_compare_LIF():
    # epoch 0, 9, 19 weight distributions of sparse enforced LIF_EI and rewiring enabled LIF_EI
    data_path = "tf2_testing/LIF_EI/"
    for idx in [0,9,19]:
        fname = data_path + "begin_epoch_" + str(idx) + ".hdf5"
        hf = h5py.File(fname)
        n1 = hf.get('rnn')
        n2 = n1.get('rnn')
        lif_ei = n2.get('lif_ei')
        rec_w = lif_ei.get('recurrent_weights:0')
        rec_w = np.array(rec_w)
        if idx == 0:
            begin_w_dist = rec_w
        if idx == 9:
            mid_w_dist = rec_w
        if idx == 19:
            end_w_dist = rec_w

    fig, ax = plt.subplots(2, figsize=(6,9))

    ax[0].hist(begin_w_dist.flatten(), bins=20, fc=(0, 0, 1, 0.5), label="initial")
    ax[0].hist(mid_w_dist.flatten(), bins=20, fc=(0, 1, 0, 0.5), label="middle")
    ax[0].hist(end_w_dist.flatten(), bins=20, fc=(1, 0, 0, 0.5), label="end")
    ax[0].set_xlabel("weights")
    ax[0].set_ylabel("counts")
    ax[0].set_title("sparse enforced LIF")
    ax[0].legend()

    for idx in [0,9,19]:
        fname = data_path + "rewiring/begin_epoch_" + str(idx) + ".hdf5"
        hf = h5py.File(fname)
        n1 = hf.get('rnn')
        n2 = n1.get('rnn')
        lif_ei = n2.get('lif_ei')
        rec_w = lif_ei.get('recurrent_weights:0')
        rec_w = np.array(rec_w)
        if idx == 0:
            begin_w_dist = rec_w
        if idx == 9:
            mid_w_dist = rec_w
        if idx == 19:
            end_w_dist = rec_w

    ax[1].hist(begin_w_dist.flatten(), bins=20, fc=(0, 0, 1, 0.5), label="initial")
    ax[1].hist(mid_w_dist.flatten(), bins=20, fc=(0, 1, 0, 0.5), label="middle")
    ax[1].hist(end_w_dist.flatten(), bins=20, fc=(1, 0, 0, 0.5), label="end")
    ax[1].set_xlabel("weights")
    ax[1].set_ylabel("counts")
    ax[1].set_title("unconstrained rewiring LIF")
    ax[1].legend()

    plt.draw()
    plt.savefig(data_path + "compare_LIF_models_w.png", dpi=300)


def plot_sparse_over_time(end_epoch,set):
    data_path = "tf2_testing/LIF_EI/sparse/set" + str(set) + "/"
    filelist = [];
    for file in os.listdir(data_path):
        if file.endswith(".hdf5"):
            if file.startswith("begin"):
                filelist.append(os.path.join(data_path, file))

    avg_i_w = []
    max_i = []
    avg_e_w = []
    max_e = []
    conn = []

    # goodness, for now loss is handwritten
    # set 1
    # loss = [0.5160,0.4762,0.4418,0.4299,0.4298,0.4239,0.4180,0.4113,0.4090,0.3901,0.3576,0.2922,0.2409,0.1926,0.1846,0.1791,0.1455,0.1513,0.1493,0.1850]
    # set 2
    loss = []

    for idx in range(len(filelist)):
        fname = data_path + "begin_epoch_" + str(idx) + ".hdf5"
        hf = h5py.File(fname)
        n1 = hf.get('rnn')
        n2 = n1.get('rnn')
        lif_ei = n2.get('lif_ei')
        rec_w = lif_ei.get('recurrent_weights:0')
        rec_w = np.array(rec_w)
        zero_ct = rec_w[rec_w==0].shape[0]
        total_ct = np.size(rec_w)
        conn.append((total_ct - zero_ct)/float(total_ct))
        avg_i_w.append(np.mean(rec_w[rec_w<0]))
        avg_e_w.append(np.mean(rec_w[rec_w>0]))
        max_i.append(np.amin(rec_w[rec_w<0]))
        max_e.append(np.amax(rec_w[rec_w>0]))
        if idx==0:
            begin_w_dist = rec_w
        if idx==len(filelist)-1:
            end_w_dist = rec_w

    fig, ax = plt.subplots(4, figsize=(6, 7))
    fig.suptitle("LIF with sparsity constraint, set" + str(set))

    ax[0].hist(begin_w_dist.flatten(), bins=50, fc=(0, 0, 1, 0.5), label="initial")
    ax[0].hist(end_w_dist.flatten(), bins=50, fc=(1, 0, 0, 0.5), label="end")
    ax[0].set_xlabel("weights")
    ax[0].set_ylabel("counts")
    ax[0].legend(prop={'size': 5})

    ax[1].plot(avg_e_w, 'b-', label="mean e weight")
    ax[1].plot(max_e, 'b*', label="highest e weight")
    ax[1].plot(avg_i_w, 'r-', label="mean i weight")
    ax[1].plot(max_i, 'r*', label="lowest i weight")
    ax[1].set_xlabel("epoch")
    ax[1].set_ylabel("weight")
    ax[1].legend(prop={'size': 5})

    ax[2].plot(conn, label = "recurrent connectivity")
    ax[2].set_xlabel("epoch")
    ax[2].set_ylabel("percent")
    ax[2].legend(prop={'size': 5})

    ax[3].plot(loss)
    ax[3].set_xlabel("epoch")
    ax[3].set_ylabel("total loss")

    fig.subplots_adjust(hspace=1)
    fig.subplots_adjust(hspace=1)
    plt.draw()
    plt.savefig(data_path + "sparse_over_time.png", dpi=300)


def rewiring_begin_end_compare(epoch):
    begin_fname = "tf2_testing/LIF_EI/rewiring/begin_epoch_" + str(epoch) + ".hdf5"
    hf = h5py.File(begin_fname,'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_ei = n2.get('lif_ei')
    rec_w = lif_ei.get('recurrent_weights:0')
    begin_rec_w = np.array(rec_w)

    print("count of zeros at beginning of epoch:")
    print(begin_rec_w[begin_rec_w==0].shape[0])
    begin_diag = begin_rec_w.diagonal()
    print("count of self-recurrent synapses that are zero")
    print(begin_diag[begin_diag==0].shape[0])
    print("e:i synapses")
    print(begin_rec_w[begin_rec_w>0].shape[0])
    print(begin_rec_w[begin_rec_w<0].shape[0])

    end_fname = "tf2_testing/LIF_EI/rewiring/end_epoch_" + str(epoch) + ".hdf5"
    hf = h5py.File(end_fname,'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_ei = n2.get('lif_ei')
    rec_w = lif_ei.get('recurrent_weights:0')
    end_rec_w = np.array(rec_w)

    print("count of zeros at end of epoch:")
    print(end_rec_w[end_rec_w==0].shape[0])
    end_diag = end_rec_w.diagonal()
    print("count of self-recurrent synapses that are zero")
    print(end_diag[end_diag==0].shape[0])
    print("e:i synapses")
    print(end_rec_w[end_rec_w>0].shape[0])
    print(end_rec_w[end_rec_w<0].shape[0])

    fig, axes = plt.subplots(2)
    axes[0].hist(begin_rec_w)
    axes[0].set_title('epoch beginning weights')
    axes[1].hist(end_rec_w)
    axes[1].set_title('epoch ending weights')
    fig.subplots_adjust(hspace=.5)
    plt.show()
    out_fname = "tf2_testing/LIF_EI/rewiring/compare_epoch_" + str(epoch) + "_weights.png"
    plt.savefig(out_fname)


def LIF_epoch_begin_end_compare(p, epoch):
    begin_fname = "tf2_testing/LIF/p" + str(int(p*100)) + "/begin_epoch_" + str(epoch) + ".hdf5"
    hf = h5py.File(begin_fname,'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_cell = n2.get('lif_cell')
    rec_w = lif_cell.get('recurrent_weights:0')
    begin_rec_w = np.array(rec_w)

    print("count of zeros at beginning of epoch:")
    print(begin_rec_w[begin_rec_w==0].shape[0])
    begin_diag = begin_rec_w.diagonal()
    print("count of self-recurrent synapses that are zero")
    print(begin_diag[begin_diag==0].shape[0])

    end_fname = "tf2_testing/LIF/p" + str(int(p*100)) + "/end_epoch_" + str(epoch) + ".hdf5"
    hf = h5py.File(end_fname,'r')
    n1 = hf.get('rnn')
    n2 = n1.get('rnn')
    lif_cell = n2.get('lif_cell')
    rec_w = lif_cell.get('recurrent_weights:0')
    end_rec_w = np.array(rec_w)

    print("count of zeros at end of epoch:")
    print(end_rec_w[end_rec_w==0].shape[0])
    end_diag = end_rec_w.diagonal()
    print("count of self-recurrent synapses that are zero")
    print(end_diag[end_diag==0].shape[0])

    fig, axes = plt.subplots(2)
    axes[0].hist(begin_rec_w)
    axes[0].set_title('epoch beginning weights')
    axes[1].hist(end_rec_w)
    axes[1].set_title('epoch ending weights')
    fig.subplots_adjust(hspace=.5)
    plt.show()
    out_fname = "tf2_testing/LIF/p" + str(int(p*100)) + "/compare_epoch_" + str(epoch) + "_weights.png"
    plt.savefig(out_fname)
