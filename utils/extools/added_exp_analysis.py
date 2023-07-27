"""select analysis / plot generation for additional experiments, e.g.
lowering all inhibitory weights,
removing dale's law for the recurrent layer,
silencing cross-tuned inhibitory connections following training"""

# ---- external imports -------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import numpy.ma as ma
import os
import scipy
import sys
import seaborn as sns
import networkx as nx

from scipy.sparse import load_npz
from scipy.stats import kstest

# ---- internal imports -------------------------------------------------------
sys.path.append("../")
sys.path.append("../../")

from utils.misc import *
from utils.extools.analyze_structure import get_degrees
from utils.extools.fn_analysis import *
from utils.extools.MI import *
from utils.extools.analyze_structure import _nets_from_weights
from utils.extools.analyze_dynamics import *
from utils.extools.analyze_final import *

# ---- global variables -------------------------------------------------------
data_dir = '/data/experiments/'
experiment_string = 'run-batch30-specout-onlinerate0.1-savey'
task_experiment_string = 'run-batch30-onlytaskloss'
rate_experiment_string = 'run-batch30-onlyrateloss'
num_epochs = 1000
epochs_per_file = 10
e_end = 241
i_end = 300

n_input = 16
seq_len = 4080

savepath = '/data/results/experiment1/'

naive_batch_id = 0
trained_batch_id = 99

"""
# snippet of code to go thru a bunch of experiments that all contain a particular string
data_dirs = get_experiments(data_dir, experiment_string)
data_files = filenames(num_epochs, epochs_per_file)
fig, ax = plt.subplots(nrows=5, ncols=1)
# get your usual experiments first
for xdir in data_dirs:
"""

data_files = filenames(num_epochs, epochs_per_file)

#ALL DUAL TRAINED TO BEGIN WITH:
unspec_dirs = ["fwd-pipeline-inputspikeregen"]
spec_output_dirs = ["run-batch30-specout-onlinerate0.1-savey","run-batch30-dualloss-silence","run-batch30-dualloss-swaplabels"]
spec_input_dirs = ["run-batch30-dualloss-specinput0.3-rewire"]
spec_nointoout_dirs = ["run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-swaplabels-saveinz","run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz","run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire","run-batch30-dualloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire","run-batch30-dualloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire-inputx5"]
save_inz_dirs = ["run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-swaplabels-saveinz","run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz"]
save_inz_dirs_rate = ["run-batch30-rateloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz"]
save_inz_dirs_task = ["run-batch30-taskloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz"]
spec_nointoout_dirs_rate = ["run-batch30-rateloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz","run-batch30-rateloss-specinput0.2-nointoout-noinoutrewire","run-batch30-rateloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire","run-batch30-rateloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire-inputx5"]
spec_nointoout_dirs_task = ["run-batch30-taskloss-specinput0.2-nointoout-noinoutrewire","run-batch30-taskloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire","run-batch30-taskloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire-inputx5"]
all_spring_dual_dirs = ["run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire","run-batch30-dualloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire","run-batch30-dualloss-specinput0.2-nointoout-twopopsbyrate-noinoutrewire-inputx5","run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-swaplabels-saveinz","run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz"]
all_save_inz_dirs = ["run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-swaplabels-saveinz","run-batch30-dualloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz","run-batch30-rateloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz","run-batch30-taskloss-specinput0.2-nointoout-noinoutrewire-inputx5-saveinz"]


lowerinhib_data_dirs = ["2023-07-03 21.12.39","2023-07-08 17.53.59"]
nodales_data_dirs = ["2023-06-30 09.37.50","2023-06-28 00.01.42","2023-06-25 14.24.22"]


# plot losses for a single example experiment over time; error bar shading is for spread within epoch
def mod_losses_over_training(exp_dirs=nodales_data_dirs,exp_season='summer'):
    for exp_string in exp_dirs:
        if not 'exp_data_dirs' in locals():
            exp_data_dirs = get_experiments(data_dir, exp_string)
        else:
            exp_data_dirs = np.hstack([exp_data_dirs,get_experiments(data_dir, exp_string)])

    # check if folder exists, otherwise create it for saving files
    spath = '/data/results/experiment1/set_plots/'+exp_season+'/final/nodales'
    if not os.path.isdir(spath):
        os.makedirs(spath)

    for xdir in exp_data_dirs: # loop through experiments
        np_dir = os.path.join(data_dir, xdir, "npz-data")

        if not '06.03.22' in np_dir: # do not include that one awful experiment
            exp_path = xdir[-9:-1]

            #task_loss = []
            #rate_loss = []

            for filename in data_files:
                filepath = os.path.join(data_dir, xdir, "npz-data", filename)
                data = np.load(filepath)
                # mean across epochs/batches in this file
                #rate_loss.append(np.mean(data['step_rate_loss']))
                #task_loss.append(np.mean(data['step_task_loss']))
                # modify to be single experiment
                rate_loss = data['step_rate_loss']
                task_loss = data['step_task_loss']

                # concat losses together
                if not 'task_losses' in locals():
                    rate_losses = np.transpose(rate_loss)
                    task_losses = np.transpose(task_loss)
                else:
                    rate_losses = np.vstack([rate_losses,np.transpose(rate_loss)])
                    task_losses = np.vstack([task_losses,np.transpose(task_loss)])

                #print(np.shape(rate_losses))

            fig, ax = plt.subplots(nrows=2, ncols=1)
            epochs=np.arange(0,len(rate_losses))
            #ax[0].plot(epochs,task_loss,label='task loss',color='teal')
            #ax[0].plot(epochs,rate_loss,label='rate loss',color='blueviolet')
            ax[0].plot(epochs,np.mean(task_losses,1),label='task loss',color='orangered')
            ax[0].fill_between(epochs,np.mean(task_losses,1)-np.std(task_losses,1),np.mean(task_losses,1)+np.std(task_losses,1),facecolor='orangered',alpha=0.4)
            ax[0].plot(epochs,np.mean(rate_losses,1),label='rate loss',color='darkorange')
            ax[0].fill_between(epochs,np.mean(rate_losses,1)-np.std(rate_losses,1),np.mean(rate_losses,1)+np.std(rate_losses,1),facecolor='darkorange',alpha=0.4)

            # plot on same subplot, but keep blank subplot just for the look

            for j in range(0,len(ax)):
                ax[j].set_ylabel('loss',fontname='Ubuntu')
                ax[j].set_xlabel('training epoch',fontname='Ubuntu')
                ax[j].legend(prop={"family":"Ubuntu"})
                ax[j].set_ylim(0.0,0.6)
                for tick in ax[j].get_xticklabels():
                    tick.set_fontname("Ubuntu")
                for tick in ax[j].get_yticklabels():
                    tick.set_fontname("Ubuntu")
            plt.suptitle("Example evolution of loss without Dale's law",fontname='Ubuntu')
            plt.subplots_adjust(wspace=0.7, hspace=0.5)
            plt.draw()

            save_fname = spath+'/losses_over_training_'+exp_path+'.png'
            plt.savefig(save_fname,dpi=300)
            # Teardown
            plt.clf()
            plt.close()

            del rate_losses
            del task_losses

def mod_plot_all_weight_dists(exp_dirs=nodales_data_dirs,exp_season='summer/final/nodales'): # just for dual-training for now

    for exp_string in exp_dirs:
        if not 'exp_data_dirs' in locals():
            exp_data_dirs = get_experiments(data_dir, exp_string)
        else:
            exp_data_dirs = np.hstack([exp_data_dirs,get_experiments(data_dir, exp_string)])
    # go through all dirs and grab the weight distributions of the first and last epochs
    data_files = filenames(num_epochs, epochs_per_file) # useful for plotting evolution over the entire course of training
    in_naive = []
    in_trained = []
    rec_naive = []
    rec_trained = []
    out_naive = []
    out_trained = []
    for xdir in exp_data_dirs:
        np_dir = os.path.join(data_dir, xdir, "npz-data")

        # collect the truly naive weights
        if 'inputx5' in xdir:
            in_naive.append(np.load(os.path.join(data_dir,xdir,"npz-data","input_preweights.npy")))
        else:
            in_naive.append(np.load(os.path.join(data_dir,xdir,"npz-data","input_preweights.npy"))*5)
        rec_naive.append(np.load(os.path.join(data_dir,xdir,"npz-data","main_preweights.npy")))
        out_naive.append(np.load(os.path.join(data_dir,xdir,"npz-data","output_preweights.npy")))

        # collect trained weights
        trained_data = np.load(os.path.join(np_dir, "991-1000.npz"))
        if 'inputx5' in xdir:
            in_trained.append(trained_data['tv0.postweights'][99])
        else:
            in_trained.append(trained_data['tv0.postweights'][99]*5)
        rec_trained.append(trained_data['tv1.postweights'][99])
        out_trained.append(trained_data['tv2.postweights'][99])

    # convert to numpy arrays
    in_naive = np.array(in_naive)
    in_trained = np.array(in_trained)
    rec_naive = np.array(rec_naive)
    rec_trained = np.array(rec_trained)
    # maybe need to make less precise in order to plot
    #rec_trained = np.around(rec_trained,decimals=1)
    out_naive = np.array(out_naive)
    out_trained = np.array(out_trained)

    """

    # PLOT NONZERO INPUT WEIGHTS
    fig, ax = plt.subplots(nrows=2,ncols=1,figsize=(4.4,5))
    in_e_naive = in_naive[:,:,:e_end].flatten()
    in_i_naive = in_naive[:,:,e_end:].flatten()
    in_e_trained = in_trained[:,:,:e_end].flatten()
    in_i_trained = in_trained[:,:,e_end:].flatten()
    sns.kdeplot(in_e_naive[in_e_naive!=0],color='dodgerblue',label='to e',ax=ax[0])
    sns.kdeplot(in_i_naive[in_i_naive!=0],color='darkorange',label='to i',ax=ax[0])
    ax[0].set_title('naive input',fontname='Ubuntu')
    sns.kdeplot(in_e_trained[in_e_trained>0],color='dodgerblue',label='to e',ax=ax[1])
    sns.kdeplot(in_i_trained[in_i_trained!=0],color='darkorange',label='to i',ax=ax[1])
    ax[1].set_title('trained input',fontname='Ubuntu')
    plt.suptitle('Input Layer Weights',fontname='Ubuntu')
    plt.subplots_adjust(wspace=0.7, hspace=0.5)
    # go through and set all axes
    ax = ax.flatten()
    for i in range(0,len(ax)):
        ax[i].set_facecolor('white')
        ax[i].legend(prop={"family":"Ubuntu"})
        ax[i].set_xlim(-0.5,4.5)
        for tick in ax[i].get_xticklabels():
            tick.set_fontname("Ubuntu")
        for tick in ax[i].get_yticklabels():
            tick.set_fontname("Ubuntu")
        ax[i].set_xlabel('synaptic current (nA)',fontname='Ubuntu')
        ax[i].set_ylabel('density',fontname='Ubuntu')
    plt.draw()
    save_fname = savepath+'/set_plots/'+exp_season+'/all_input_weights.png'
    plt.savefig(save_fname,dpi=300)
    # Teardown
    plt.clf()
    plt.close()
    """

    # PLOT NONZERO OUTPUT WEIGHTS
    fig, ax = plt.subplots(nrows=2,ncols=1,figsize=(4.4,5))
    out_e_naive = out_naive[:,:e_end].flatten()
    out_i_naive = out_naive[:,e_end:].flatten()
    out_e_trained = out_trained[:,:e_end].flatten()
    out_i_trained = out_trained[:,e_end:].flatten()
    sns.kdeplot(out_e_naive[out_e_naive!=0],color='dodgerblue',label='from e',ax=ax[0])
    sns.kdeplot(out_i_naive[out_i_naive!=0],color='darkorange',label='from i',ax=ax[0])
    ax[0].set_title('naive output',fontname='Ubuntu')
    sns.kdeplot(out_e_trained[out_e_trained!=0],color='dodgerblue',label='from e',ax=ax[1])
    sns.kdeplot(out_i_trained[out_i_trained!=0],color='darkorange',label='from i',ax=ax[1])
    ax[1].set_title('trained output',fontname='Ubuntu')
    plt.suptitle('No Dales: Output Layer Weights',fontname='Ubuntu')
    plt.subplots_adjust(wspace=0.7, hspace=0.5)
    plt.legend()
    # go through and set all axes
    ax = ax.flatten()
    for i in range(0,len(ax)):
        ax[i].set_facecolor('white')
        ax[i].legend(prop={"family":"Ubuntu"})
        ax[i].set_xlim(-2.0,0.5)
        for tick in ax[i].get_xticklabels():
            tick.set_fontname("Ubuntu")
        for tick in ax[i].get_yticklabels():
            tick.set_fontname("Ubuntu")
        ax[i].set_xlabel('synaptic current (nA)',fontname='Ubuntu')
        ax[i].set_ylabel('density',fontname='Ubuntu')
    plt.draw()
    save_fname = savepath+'set_plots/'+exp_season+'/all_output_weights.png'
    plt.savefig(save_fname,dpi=300)
    # Teardown
    plt.clf()
    plt.close()


    # plot RECURRENT ee, ei, ie and ii separately, and only nonzero weight values
    fig, ax = plt.subplots(nrows=2,ncols=1,figsize=(3,5))
    rec_naive_ee = rec_naive[:,:e_end,:e_end].flatten()
    rec_naive_ei = rec_naive[:,:e_end,e_end:].flatten()
    rec_naive_ie = rec_naive[:,e_end:,:e_end].flatten()
    rec_naive_ii = rec_naive[:,e_end:,e_end:].flatten()
    rec_trained_ee = rec_trained[:9,:e_end,:e_end].flatten()
    rec_trained_ei = rec_trained[:,:e_end,e_end:].flatten()
    rec_trained_ie = rec_trained[:10,e_end:,:e_end].flatten()
    rec_trained_ii = rec_trained[:,e_end:,e_end:].flatten()

    sns.kdeplot(rec_naive_ee[rec_naive_ee>0],color='slateblue',alpha=0.7,label='ee',ax=ax[0])
    sns.kdeplot(rec_naive_ei[rec_naive_ei>0],color='mediumseagreen',alpha=0.7,label='ei',ax=ax[0])
    sns.kdeplot(rec_naive_ie[rec_naive_ie<0],color='orange',alpha=0.7,label='ie',ax=ax[0])
    sns.kdeplot(rec_naive_ii[rec_naive_ii<0],color='orangered',alpha=0.7,label='ii',ax=ax[0])
    ax[0].set_title('naive recurrent',fontname='Ubuntu')

    sns.kdeplot(rec_trained_ee[rec_trained_ee>0],color='slateblue',alpha=0.7,label='ee',ax=ax[1])
    sns.kdeplot(rec_trained_ei[rec_trained_ei>0],color='mediumseagreen',alpha=0.7,label='ei',ax=ax[1])
    sns.kdeplot(rec_trained_ie[rec_trained_ie<0],color='orange',alpha=0.7,label='ie',ax=ax[1])
    sns.kdeplot(rec_trained_ii[rec_trained_ii<0],color='orangered',alpha=0.7,label='ii',ax=ax[1])
    ax[1].set_title('trained recurrent',fontname='Ubuntu')

    plt.suptitle('No Dales: Main Recurrent Layer Weights',fontname='Ubuntu')
    plt.subplots_adjust(wspace=0.7, hspace=0.5)
    plt.legend()
    # go through and set all axes
    ax = ax.flatten()
    for i in range(0,len(ax)):
        ax[i].set_facecolor('white')
        ax[i].legend(prop={"family":"Ubuntu"})
        ax[i].set_xlim(-5,1)
        for tick in ax[i].get_xticklabels():
            tick.set_fontname("Ubuntu")
        for tick in ax[i].get_yticklabels():
            tick.set_fontname("Ubuntu")
        ax[i].set_xlabel('synaptic current (nA)',fontname='Ubuntu')
        ax[i].set_ylabel('density',fontname='Ubuntu')
    plt.draw()
    save_fname = savepath+'set_plots/'+exp_season+'/all_main_weights.png'
    plt.savefig(save_fname,dpi=300)

    # Teardown
    plt.clf()
    plt.close()


def dales_over_training(exp_dirs=nodales_data_dirs,exp_season='summer'):
    # plot over the course of training the number of e connections [:e_end,:] that become negative
    # and the number of i units [e_end:,:] that become positive
    # this helps us visualize whether e and i units stabilize at some point

    # do so separately for each experiment
    for exp_string in exp_dirs:
        if not 'exp_data_dirs' in locals():
            exp_data_dirs = get_experiments(data_dir, exp_string)
        else:
            exp_data_dirs = np.hstack([exp_data_dirs,get_experiments(data_dir, exp_string)])

    # check if folder exists, otherwise create it for saving files
    spath = '/data/results/experiment1/set_plots/'+exp_season+'/final/nodales'
    if not os.path.isdir(spath):
        os.makedirs(spath)

    for xdir in exp_data_dirs: # loop through experiments
        np_dir = os.path.join(data_dir, xdir, "npz-data")
        exp_path = xdir[-9:-1]

        i_swap=[]
        i_swap_scale=[]
        e_swap=[]
        e_swap_scale=[]

        for filename in data_files:
            filepath = os.path.join(data_dir, xdir, "npz-data", filename)
            data = np.load(filepath)
            # mean across epochs/batches in this file
            #rate_loss.append(np.mean(data['step_rate_loss']))
            #task_loss.append(np.mean(data['step_task_loss']))
            # modify to be single experiment
            w = data['tv1.postweights']
            for i in range(0,len(w)):
                inhib = w[i][e_end:,:]
                excit = w[i][:e_end,:]
                i_swap.append(len(inhib[inhib>0])/len(inhib[inhib<0]))
                e_swap.append(len(excit[excit<0])/len(excit[excit>0]))
                i_swap_scale.append(np.abs(np.mean(inhib[inhib>0])/np.mean(inhib[inhib<0])))
                e_swap_scale.append(np.abs(np.mean(excit[excit<0])/np.mean(excit[excit>0])))

        fig, ax = plt.subplots(nrows=3, ncols=1)
        epochs=np.arange(0,len(i_swap))/100
        ax[0].plot(epochs,e_swap,label='e that became -',color='mediumseagreen')
        ax[0].plot(epochs,i_swap,label='i that became +',color='darkorange')
        ax[0].set_title('proportion of units that swapped sign',fontname='Ubuntu')

        ax[1].plot(epochs,e_swap_scale,color='mediumseagreen')
        ax[1].set_title('relative strength of swapped e edges',fontname='Ubuntu')

        ax[2].plot(epochs,i_swap_scale,color='darkorange')
        ax[2].set_title('relative strength of swapped i edges',fontname='Ubuntu')

        for j in range(0,len(ax)):
            #ax[j].set_ylabel('',fontname='Ubuntu')
            ax[j].set_xlabel('training epoch',fontname='Ubuntu')
            ax[j].legend(prop={"family":"Ubuntu"})
            for tick in ax[j].get_xticklabels():
                tick.set_fontname("Ubuntu")
            for tick in ax[j].get_yticklabels():
                tick.set_fontname("Ubuntu")
        plt.suptitle("Changes in weights without Dale's law",fontname='Ubuntu')
        plt.subplots_adjust(wspace=0.7, hspace=0.9)
        plt.draw()

        save_fname = spath+'/sign_swaps_'+exp_path+'.png'
        plt.savefig(save_fname,dpi=300)
        # Teardown
        plt.clf()
        plt.close()

    # to begin with, very straightforwardly define tuning according to prior protocol,
    # which is to look at the final trained state.
    # of course, units will no longer be excit and inhib in the same way
    # think about this a little harder this afternoon.


def mod_input_layer_over_training_by_coherence(dual_exp_dir=spec_nointoout_dirs_task,exp_season='spring_task'):
    # characterize the connectivity from the input layer to recurrent
    # plot over the course of training with shaded error bars
    # compare for rate- and dual-trained

    # ACTUALLY YOU NEED TO DO THIS FOR INDIVIDUAL EXPERIMENTS BECAUSE WE ARE FOLLOWING LABELS NOT ACTUAL COHERENCE

    # from actual experiment now
    for exp_string in dual_exp_dir:
        if not 'exp_data_dirs' in locals():
            exp_data_dirs = get_experiments(data_dir, exp_string)
        else:
            exp_data_dirs = np.hstack([exp_data_dirs,get_experiments(data_dir, exp_string)])

    # check if folder exists, otherwise create it for saving files
    spath = '/data/results/experiment1/set_plots/'+exp_season+'/final'
    if not os.path.isdir(spath):
        os.makedirs(spath)

    # get default input tunings from CNN outputs
    [default_coh0_idx, default_coh1_idx] = get_input_tuning_from_CNN()

    # aggregate over all experiments

    for xdir in exp_data_dirs: # loop through experiments
        np_dir = os.path.join(data_dir, xdir, "npz-data")

        coh1_e_exp = []
        coh1_i_exp = []
        coh0_e_exp = []
        coh0_i_exp = []
        epoch_task_loss_exp = []
        epoch_rate_loss_exp = []

        # check if inputs is saved; otherwise use defaults

        filepath = os.path.join(data_dir, xdir, "npz-data", '1-10.npz')
        data = np.load(filepath)
        if 'inputs' in data:
            [coh0_idx, coh1_idx] = get_input_tuning_single_exp(xdir)
        else:
            [coh0_idx, coh1_idx] = [default_coh0_idx, default_coh1_idx]

        # get the truly naive weights
        filepath = os.path.join(data_dir,xdir,"npz-data","input_preweights.npy")
        input_w = np.load(filepath)
        coh1_e_exp.append(np.mean(input_w[coh1_idx,:e_end]))
        coh1_i_exp.append(np.mean(input_w[coh1_idx,e_end:]))
        coh0_e_exp.append(np.mean(input_w[coh0_idx,:e_end]))
        coh0_i_exp.append(np.mean(input_w[coh0_idx,e_end:]))

        # now do weights over time
        for filename in data_files:
            filepath = os.path.join(data_dir, xdir, "npz-data", filename)
            data = np.load(filepath)
            input_w = data['tv0.postweights'][0] # just the singular for now; too much data and noise otherwise
            epoch_task_loss_exp.append(np.mean(data['step_task_loss']))
            epoch_rate_loss_exp.append(np.mean(data['step_rate_loss']))
            #for i in range(0,np.shape(input_w)[0]): # 100 trials
            # weights of each type to e units and to i units
            coh1_e_exp.append(np.mean(input_w[coh1_idx,:e_end]))
            coh1_i_exp.append(np.mean(input_w[coh1_idx,e_end:]))
            coh0_e_exp.append(np.mean(input_w[coh0_idx,:e_end]))
            coh0_i_exp.append(np.mean(input_w[coh0_idx,e_end:]))

            # you may want to expand this and grab ALL of the weights

        if not "coh1_e" in locals():
            coh1_e = coh1_e_exp
        else:
            coh1_e = np.vstack([coh1_e, coh1_e_exp])

        if not "coh1_i" in locals():
            coh1_i = coh1_i_exp
        else:
            coh1_i = np.vstack([coh1_i, coh1_i_exp])

        if not "coh0_e" in locals():
            coh0_e = coh0_e_exp
        else:
            coh0_e = np.vstack([coh0_e, coh0_e_exp])

        if not "coh0_i" in locals():
            coh0_i = coh0_i_exp
        else:
            coh0_i = np.vstack([coh0_i, coh0_i_exp])

        if not "epoch_task_loss" in locals():
            epoch_task_loss = epoch_task_loss_exp
        else:
            epoch_task_loss = np.vstack([epoch_task_loss, epoch_task_loss_exp])

        if not "epoch_rate_loss" in locals():
            epoch_rate_loss = epoch_rate_loss_exp
        else:
            epoch_rate_loss = np.vstack([epoch_rate_loss, epoch_rate_loss_exp])

    """
    # CHARACTERIZE AND COMPARE
    # naive and trained means and stds
    # order is avg coherence 1 tuned input to e, avg coherence 0 tuned input to e, avg coherence 1 tuned input to i, avg coherence 0 tuned input to i
    naive_means = [np.mean(coh1_e[:,0],0), np.mean(coh0_e[:,0],0), np.mean(coh1_i[:,0],0), np.mean(coh0_i[:,0],0)]
    naive_stds = [np.std(coh1_e[:,0],0), np.std(coh0_e[:,0],0), np.std(coh1_i[:,0],0), np.std(coh0_i[:,0],0)]

    trained_means = [np.mean(coh1_e[:,100],0), np.mean(coh0_e[:,100],0), np.mean(coh1_i[:,100],0), np.mean(coh0_i[:,100],0)]
    trained_stds = [np.std(coh1_e[:,100],0), np.std(coh0_e[:,100],0), np.std(coh1_i[:,100],0), np.std(coh0_i[:,100],0)]

    # in naive state
    # e recipients of 0 or 1 drive
    [D,p] = scipy.stats.kstest(coh0_e[:,0],coh1_e[:,0])
    # i recipients of 0 or 1 drive
    [D,p] = scipy.stats.kstest(coh0_i[:,0],coh1_i[:,0])

    # in trained state
    # e recipients of 0 or 1 drive
    [D,p] = scipy.stats.kstest(coh0_e[:,100],coh1_e[:,100])
    # i recipients of 0 or 1 drive
    [D,p] = scipy.stats.kstest(coh0_i[:,100],coh1_i[:,100])

    # ratios
    np.mean(coh0_e[:,0])/np.mean(coh0_i[:,0])
    np.mean(coh1_e[:,0])/np.mean(coh1_i[:,0])

    np.mean(coh0_e[:,100])/np.mean(coh0_i[:,100])
    np.mean(coh1_e[:,100])/np.mean(coh1_i[:,100])

    # THIS IS WHAT IS ACTUALLY IN PLOTS:
    np.mean(coh0_e[:,0])/np.mean(coh1_e[:,0])

    """

    fig, ax = plt.subplots(nrows=3, ncols=1)

    coh1_e_mean = np.mean(coh1_e,0)
    coh1_e_std = np.std(coh1_e,0)
    coh0_e_mean = np.mean(coh0_e,0)
    coh0_e_std = np.std(coh0_e,0)

    epochs = np.shape(coh1_e)[1]

    ax[0].plot(np.arange(0,epochs),coh1_e_mean, label='coh 1 tuned inputs', color='slateblue')
    ax[0].fill_between(np.arange(0,epochs),coh1_e_mean-coh1_e_std, coh1_e_mean+coh1_e_std, alpha=0.4, facecolor='slateblue')
    ax[0].plot(np.arange(0,epochs),coh0_e_mean, label='coh 0 tuned inputs', color='mediumseagreen')
    ax[0].fill_between(np.arange(0,epochs),coh0_e_mean-coh0_e_std, coh0_e_mean+coh0_e_std, alpha=0.4, facecolor='mediumseagreen')
    ax[0].set_title('input weights to excitatory units',fontname='Ubuntu')

    coh1_i_mean = np.mean(coh1_i,0)
    coh1_i_std = np.std(coh1_i,0)
    coh0_i_mean = np.mean(coh0_i,0)
    coh0_i_std = np.std(coh0_i,0)

    ax[1].plot(np.arange(0,epochs),coh1_i_mean, label='coh 1 tuned inputs', color='darkorange')
    ax[1].fill_between(np.arange(0,epochs),coh1_i_mean-coh1_i_std, coh1_i_mean+coh1_i_std, alpha=0.4, facecolor='darkorange')
    ax[1].plot(np.arange(0,epochs),coh0_i_mean, label='coh 0 tuned inputs', color='orangered')
    ax[1].fill_between(np.arange(0,epochs),coh0_i_mean-coh0_i_std, coh0_i_mean+coh0_i_std, alpha=0.4, facecolor='orangered')
    ax[1].set_title('input weights to inhibitory units',fontname='Ubuntu')

    epochs = np.shape(epoch_task_loss)[1]

    task_mean = np.mean(epoch_task_loss,0)
    task_error = np.std(epoch_task_loss,0)
    ax[2].plot(np.arange(0,epochs),task_mean, label='task loss', color='darkorange')
    ax[2].fill_between(np.arange(0,epochs),task_mean-task_error, task_mean+task_error, alpha=0.4, facecolor='darkorange')

    rate_mean = np.mean(epoch_rate_loss,0)
    rate_error = np.std(epoch_rate_loss,0)
    ax[2].plot(np.arange(0,epochs),rate_mean, label='rate loss', color='orangered')
    ax[2].fill_between(np.arange(0,epochs),rate_mean+rate_error, rate_mean+rate_error, alpha=0.4, facecolor='orangered') #other options include edgecolor='#CC4F1B', facecolor='#FF9848'

    ax[2].set_ylabel('loss',fontname='Ubuntu')
    ax[2].set_title('losses')

    for j in range(0,len(ax)):
        if j < 2:
            ax[j].set_ylabel('average weights',fontname='Ubuntu')
        ax[j].set_xlabel('training epoch',fontname='Ubuntu')
        ax[j].legend(prop={"family":"Ubuntu"})
        for tick in ax[j].get_xticklabels():
            tick.set_fontname("Ubuntu")
        for tick in ax[j].get_yticklabels():
            tick.set_fontname("Ubuntu")

    plt.suptitle('Evolution of input weights over task-training',fontname='Ubuntu')
    plt.subplots_adjust(wspace=1.0, hspace=1.0)
    plt.draw()

    save_fname = spath+'/corrected_inputs_to_ei_task.png'
    plt.savefig(save_fname,dpi=300)
    # Teardown
    plt.clf()
    plt.close()

    return [coh1_e,coh0_e,coh1_i,coh0_i]

    """
        for filename in data_files:
            filepath = os.path.join(data_dir, xdir, "npz-data", filename)

            data = np.load(filepath)
            spikes = data['spikes']
            true_y = data['true_y']

            # aggregate the mean connectivity strength from the two tuned input populations to e and i units
            # maybe it's too much to do it over more than just the last batch trial for each file
            # that's still 100 datapoints
            for i in range(0,np.shape(true_y)[0]):
                for j in range(0,np.shape(true_y)[1]):

            # ratio of weights; get naive vs. trained distributions and also see how they evolve over training too
            coh0in_to_e/coh0in_to_i
            coh1in_to_e/coh1in_to_i
            # aggregate over all experiments
    """

    # get a number distribution to quantify this, maybe for each experiment
    # the ratio between avg weight from input coh0 and coh1 to e and i recurrent units at the beginning and at the end of training
    # 0_to_e/0_to_i = 1 at beginning
    # 1_to_e/1_to_i = 1 at beginning
    # 0_to_e/0_to_i < 1 at end
    # 1_to_e/1_to_e > 1 at end
    # that's a good start


def mod_tuned_rec_layer_over_training(exp_dirs=spec_nointoout_dirs_rate,exp_season='spring_rate'):
    # plot over the course of training with shaded error bars
    # plot the average weight within and between coherence tuning of recurrent layer units
    # make sure all axes are comparable
    # get the numbers (avg and std weight for all of these connection types? shape tho?) for the weight distributions at the beginning and end of training

    # look at tuning to coherence level
    # look at connections between units in accordance to tuning to coherence level
    for exp_string in exp_dirs:
        if not 'exp_data_dirs' in locals():
            exp_data_dirs = get_experiments(data_dir, exp_string)
        else:
            exp_data_dirs = np.hstack([exp_data_dirs,get_experiments(data_dir, exp_string)])

    # check if folder exists, otherwise create it for saving files
    spath = '/data/results/experiment1/set_plots/'+exp_season+'/final'
    if not os.path.isdir(spath):
        os.makedirs(spath)

    for xdir in exp_data_dirs:
        coh0_ee_ = []
        coh0_ei_ = []
        coh0_ie_ = []
        coh0_ii_ = []

        coh1_ee_ = []
        coh1_ei_ = []
        coh1_ie_ = []
        coh1_ii_ = []

        # coh 0 to 1
        het_ee_ = []
        het_ei_ = []
        het_ie_ = []
        het_ii_ = []

        # coh 1 to 0
        ero_ee_ = []
        ero_ei_ = []
        ero_ie_ = []
        ero_ii_ = []

        print('begin new exp')
        exp_path = xdir[-9:-1]

        np_dir = os.path.join(data_dir,xdir,"npz-data")
        data = np.load(os.path.join(np_dir,'991-1000.npz'))
        spikes=data['spikes']
        true_y=data['true_y']

        # find which units respond more to input of a certain coh level in the trained state
        coh0_rec_rates = []
        coh1_rec_rates = []

        for i in range(0,np.shape(true_y)[0]):
            for j in range(0,np.shape(true_y)[1]):
                if true_y[i][j][0]==true_y[i][j][seq_len-1]:
                    if true_y[i][j][0]==0:
                        coh0_rec_rates.append(np.mean(spikes[i][j],0))
                    else:
                        coh1_rec_rates.append(np.mean(spikes[i][j],0))

        # find which of the 300 recurrent units respond more on average to one coherence level over the other
        coh1_rec_idx = np.where(np.mean(coh1_rec_rates,0)>np.mean(coh0_rec_rates,0))[0]
        """
        print('there are '+str(len(coh1_rec_idx[coh1_rec_idx<e_end]))+' coh1-tuned e units')
        print('there are '+str(len(coh1_rec_idx[coh1_rec_idx>=e_end]))+' coh1-tuned i units')
        """
        coh0_rec_idx = np.where(np.mean(coh1_rec_rates,0)<np.mean(coh0_rec_rates,0))[0]
        """
        print('there are '+str(len(coh0_rec_idx[coh0_rec_idx<e_end]))+' coh0-tuned e units')
        print('there are '+str(len(coh0_rec_idx[coh0_rec_idx>=e_end]))+' coh0-tuned i units')
        """

        coh0_rec_rates = np.array(coh0_rec_rates)
        coh1_rec_rates = np.array(coh1_rec_rates)

        # just average weights to begin with?
        coh1_e = np.array(coh1_rec_idx[coh1_rec_idx<e_end])
        coh1_i = np.array(coh1_rec_idx[coh1_rec_idx>=e_end])
        coh0_e = np.array(coh0_rec_idx[coh0_rec_idx<e_end])
        coh0_i = np.array(coh0_rec_idx[coh0_rec_idx>=e_end])


        # collect weights over all of training
        temporal_w = []
        data_files = filenames(num_epochs, epochs_per_file)

        for filename in data_files:
            filepath = os.path.join(data_dir, xdir, "npz-data", filename)
            temp_data = np.load(filepath)
            temporal_w.append(temp_data['tv1.postweights'][99])

        # name them as homo and hetero lol
        # plot weights based on coh tuning over time

        for i in range(0,np.shape(temporal_w)[0]): # again over all training time, but now just one per file (100) instead of craziness (10000)
            coh0_ee_.append(np.mean(temporal_w[i][coh0_e,:][:,coh0_e]))
            coh0_ei_.append(np.mean(temporal_w[i][coh0_e,:][:,coh0_i]))
            coh0_ie_.append(np.mean(temporal_w[i][coh0_i,:][:,coh0_e]))
            coh0_ii_.append(np.mean(temporal_w[i][coh0_i,:][:,coh0_i]))

            coh1_ee_.append(np.mean(temporal_w[i][coh1_e,:][:,coh1_e]))
            coh1_ei_.append(np.mean(temporal_w[i][coh1_e,:][:,coh1_i]))
            coh1_ie_.append(np.mean(temporal_w[i][coh1_i,:][:,coh1_e]))
            coh1_ii_.append(np.mean(temporal_w[i][coh1_i,:][:,coh1_i]))

            het_ee_.append(np.mean(temporal_w[i][coh0_e,:][:,coh1_e]))
            het_ei_.append(np.mean(temporal_w[i][coh0_e,:][:,coh1_i]))
            het_ie_.append(np.mean(temporal_w[i][coh0_i,:][:,coh1_e]))
            het_ii_.append(np.mean(temporal_w[i][coh0_i,:][:,coh1_i]))

            ero_ee_.append(np.mean(temporal_w[i][coh1_e,:][:,coh0_e]))
            ero_ei_.append(np.mean(temporal_w[i][coh1_e,:][:,coh0_i]))
            ero_ie_.append(np.mean(temporal_w[i][coh1_i,:][:,coh0_e]))
            ero_ii_.append(np.mean(temporal_w[i][coh1_i,:][:,coh0_i]))

        if not np.isnan(coh0_ee_).any():
            if not "coh0_ee" in locals():
                coh0_ee = coh0_ee_
            else:
                coh0_ee = np.vstack([coh0_ee, coh0_ee_])

        if not np.isnan(coh0_ei_).any():
            if not "coh0_ei" in locals():
                coh0_ei = coh0_ei_
            else:
                coh0_ei = np.vstack([coh0_ei, coh0_ei_])

        if not np.isnan(coh0_ie_).any():
            if not "coh0_ie" in locals():
                coh0_ie = coh0_ie_
            else:
                coh0_ie = np.vstack([coh0_ie, coh0_ie_])

        if not np.isnan(coh0_ii_).any():
            if not "coh0_ii" in locals():
                coh0_ii = coh0_ii_
            else:
                coh0_ii = np.vstack([coh0_ii, coh0_ii_])

        if not np.isnan(coh1_ee_).any():
            if not "coh1_ee" in locals():
                coh1_ee = coh1_ee_
            else:
                coh1_ee = np.vstack([coh1_ee, coh1_ee_])

        if not np.isnan(coh1_ei_).any():
            if not "coh1_ei" in locals():
                coh1_ei = coh1_ei_
            else:
                coh1_ei = np.vstack([coh1_ei, coh1_ei_])

        if not np.isnan(coh1_ie_).any():
            if not "coh1_ie" in locals():
                coh1_ie = coh1_ie_
            else:
                coh1_ie = np.vstack([coh1_ie, coh1_ie_])

        if not np.isnan(coh1_ii_).any():
            if not "coh1_ii" in locals():
                coh1_ii = coh1_ii_
            else:
                coh1_ii = np.vstack([coh1_ii, coh1_ii_])

        if not np.isnan(het_ee_).any():
            if not "het_ee" in locals():
                het_ee = het_ee_
            else:
                het_ee = np.vstack([het_ee, het_ee_])

        if not np.isnan(het_ei_).any():
            if not "het_ei" in locals():
                het_ei = het_ei_
            else:
                het_ei = np.vstack([het_ei, het_ei_])

        if not np.isnan(het_ie_).any():
            if not "het_ie" in locals():
                het_ie = het_ie_
            else:
                het_ie = np.vstack([het_ie, het_ie_])

        if not np.isnan(het_ii_).any():
            if not "het_ii" in locals():
                het_ii = het_ii_
            else:
                het_ii = np.vstack([het_ii, het_ii_])

        if not np.isnan(ero_ee_).any():
            if not "ero_ee" in locals():
                ero_ee = ero_ee_
            else:
                ero_ee = np.vstack([ero_ee, ero_ee_])

        if not np.isnan(ero_ei_).any():
            if not "ero_ei" in locals():
                ero_ei = ero_ei_
            else:
                ero_ei = np.vstack([ero_ei, ero_ei_])

        if not np.isnan(ero_ie_).any():
            if not "ero_ie" in locals():
                ero_ie = ero_ie_
            else:
                ero_ie = np.vstack([ero_ie, ero_ie_])

        if not np.isnan(ero_ii_).any():
            if not "ero_ii" in locals():
                ero_ii = ero_ii_
            else:
                ero_ii = np.vstack([ero_ii, ero_ii_])

    fig, ax = plt.subplots(nrows=4,ncols=1,figsize=(8,10))

    epochs = np.shape(coh0_ee)[1]

    coh0_ee_mean = np.mean(coh0_ee,0)
    coh0_ee_std = np.std(coh0_ee,0)
    ax[0].plot(np.arange(0,epochs),coh0_ee_mean,color='slateblue',label='ee')
    ax[0].fill_between(np.arange(0,epochs),coh0_ee_mean-coh0_ee_std, coh0_ee_mean+coh0_ee_std, alpha=0.4, facecolor='slateblue')

    coh0_ei_mean = np.mean(coh0_ei,0)
    coh0_ei_std = np.std(coh0_ei,0)
    ax[0].plot(np.arange(0,epochs),coh0_ei_mean,color='mediumseagreen',label='ei')
    ax[0].fill_between(np.arange(0,epochs),coh0_ei_mean-coh0_ei_std, coh0_ei_mean+coh0_ei_std, alpha=0.4, facecolor='mediumseagreen')

    coh0_ie_mean = np.mean(coh0_ie,0)
    coh0_ie_std = np.std(coh0_ie,0)
    ax[0].plot(np.arange(0,epochs),coh0_ie_mean,color='darkorange',label='ie')
    ax[0].fill_between(np.arange(0,epochs),coh0_ie_mean-coh0_ie_std, coh0_ie_mean+coh0_ie_std, alpha=0.4, facecolor='darkorange')

    coh0_ii_mean = np.mean(coh0_ii,0)
    coh0_ii_std = np.std(coh0_ii,0)
    ax[0].plot(np.arange(0,epochs),coh0_ii_mean,color='orangered',label='ii')
    ax[0].fill_between(np.arange(0,epochs),coh0_ii_mean-coh0_ii_std, coh0_ii_mean+coh0_ii_std, alpha=0.4, facecolor='orangered')

    ax[0].set_title('coherence 0 tuned recurrent connections',fontname='Ubuntu')
    ax[0].set_ylabel('average weight',fontname='Ubuntu')


    ax[1].plot(np.arange(0,epochs),np.mean(coh1_ee,0),color='slateblue',label='ee')
    ax[1].fill_between(np.arange(0,epochs),np.mean(coh1_ee,0)-np.std(coh1_ee,0), np.mean(coh1_ee,0)+np.std(coh1_ee,0), alpha=0.4, facecolor='slateblue')

    ax[1].plot(np.arange(0,epochs),np.mean(coh1_ei,0),color='mediumseagreen',label='ei')
    ax[1].fill_between(np.arange(0,epochs),np.mean(coh1_ei,0)-np.std(coh1_ei,0), np.mean(coh1_ei,0)+np.std(coh1_ei,0), alpha=0.4, facecolor='mediumseagreen')

    ax[1].plot(np.arange(0,epochs),np.mean(coh1_ie,0),color='darkorange',label='ie')
    ax[1].fill_between(np.arange(0,epochs),np.mean(coh1_ie,0)-np.std(coh1_ie,0), np.mean(coh1_ie,0)+np.std(coh1_ie,0), alpha=0.4, facecolor='darkorange')

    ax[1].plot(np.arange(0,epochs),np.mean(coh1_ii,0),color='orangered',label='ii')
    ax[1].fill_between(np.arange(0,epochs),np.mean(coh1_ii,0)-np.std(coh1_ii,0), np.mean(coh1_ii,0)+np.std(coh1_ii,0), alpha=0.4, facecolor='orangered')

    ax[1].set_title('coherence 1 tuned recurrent connections',fontname='Ubuntu')
    ax[1].set_ylabel('average weight',fontname='Ubuntu')


    ax[2].plot(np.arange(0,epochs),np.mean(het_ee,0),color='slateblue',label='ee')
    ax[2].fill_between(np.arange(0,epochs),np.mean(het_ee,0)-np.std(het_ee,0), np.mean(het_ee,0)+np.std(het_ee,0), alpha=0.4, facecolor='slateblue')

    ax[2].plot(np.arange(0,epochs),np.mean(het_ei,0),color='mediumseagreen',label='ei')
    ax[2].fill_between(np.arange(0,epochs),np.mean(het_ei,0)-np.std(het_ei,0), np.mean(het_ei,0)+np.std(het_ei,0), alpha=0.4, facecolor='mediumseagreen')

    ax[2].plot(np.arange(0,epochs),np.mean(het_ie,0),color='darkorange',label='ie')
    ax[2].fill_between(np.arange(0,epochs),np.mean(het_ie,0)-np.std(het_ie,0), np.mean(het_ie,0)+np.std(het_ie,0), alpha=0.4, facecolor='darkorange')

    ax[2].plot(np.arange(0,epochs),np.mean(het_ii,0),color='orangered',label='ii')
    ax[2].fill_between(np.arange(0,epochs),np.mean(het_ii,0)-np.std(het_ii,0), np.mean(het_ii,0)+np.std(het_ii,0), alpha=0.4, facecolor='orangered')

    ax[2].set_title('coherence 0 to coherence 1 tuned recurrent connections',fontname='Ubuntu')
    ax[2].set_ylabel('average weight',fontname='Ubuntu')

    ax[3].plot(np.arange(0,epochs),np.mean(ero_ee,0),color='slateblue',label='ee')
    ax[3].fill_between(np.arange(0,epochs),np.mean(ero_ee,0)-np.std(ero_ee,0), np.mean(ero_ee,0)+np.std(ero_ee,0), alpha=0.4, facecolor='slateblue')

    ax[3].plot(np.arange(0,epochs),np.mean(ero_ei,0),color='mediumseagreen',label='ei')
    ax[3].fill_between(np.arange(0,epochs),np.mean(ero_ei,0)-np.std(ero_ei,0), np.mean(ero_ei,0)+np.std(ero_ei,0), alpha=0.4, facecolor='mediumseagreen')

    ax[3].plot(np.arange(0,epochs),np.mean(ero_ie,0),color='darkorange',label='ie')
    ax[3].fill_between(np.arange(0,epochs),np.mean(ero_ie,0)-np.std(ero_ie,0), np.mean(ero_ie,0)+np.std(ero_ie,0), alpha=0.4, facecolor='darkorange')

    ax[3].plot(np.arange(0,epochs),np.mean(ero_ii,0),color='orangered',label='ii')
    ax[3].fill_between(np.arange(0,epochs),np.mean(ero_ii,0)-np.std(ero_ii,0), np.mean(ero_ii,0)+np.std(ero_ii,0), alpha=0.4, facecolor='orangered')

    ax[3].set_title('coherence 1 to coherence 0 tuned recurrent connections',fontname='Ubuntu')
    ax[3].set_ylabel('average weight',fontname='Ubuntu')

    for j in range(0,len(ax)):
        ax[j].set_xlim(left=-5,right=105)
        ax[j].set_ylim(bottom=-1.5,top=0.25)
        ax[j].set_xlabel('training epoch')
        ax[j].legend(prop={"family":"Ubuntu"})
        for tick in ax[j].get_xticklabels():
            tick.set_fontname("Ubuntu")
        for tick in ax[j].get_yticklabels():
            tick.set_fontname("Ubuntu")

    plt.suptitle('Recurrent Connectivity by Coherence Tuning: Rate Trained',fontname='Ubuntu')
    save_fname = spath+'/rec_weights_by_tuning_over_ratetraining.png'
    plt.subplots_adjust(hspace=0.8,wspace=0.8)
    plt.draw()
    plt.savefig(save_fname,dpi=300)
    # Teardown
    plt.clf()
    plt.close()
