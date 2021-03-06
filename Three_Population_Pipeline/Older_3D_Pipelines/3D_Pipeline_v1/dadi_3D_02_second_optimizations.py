import sys
import os
import numpy as np
import dadi
import matplotlib
from datetime import datetime
import Models_3D
'''
usage: python dadi_3D_02_second_optimizations.py

Requires the Models_3D.py script to be in same working directory.
This is where all the population model functions are stored. This is written for the
models specifically found in that script. 

Script will perform optimizations from multiple starting points using a
2-fold perturbed set of USER SELECTED starting values for parameters. The output for
each model is a tab-delimited text file which can be opened and sorted to
find the best scoring replicate. The parameter values from this run can
be used as the starting values in the next script, "dadi_3D_03_third_optimizations.py".
The order of output parameters matches the input order, so they can be copied
and pasted into the next script within the appropriate list.

The outputs from here will be labeled according to model and a user
selected prefix name, and are written to the working directory.

Requires user to edit sections of code marked with #**************

You'll absolutely need to provide the path to your SNPs input file
along with your specific projections and population labels. 


############################################
Written for Python 2.7
Python modules required:
-Numpy
-Scipy
-Matplotlib
-dadi
############################################

Dan Portik
daniel.portik@uta.edu
April 2017
'''
t_begin = datetime.now()

#===========================================================================
#get snps file 
#**************
snps1 = "/FULL PATH TO/dadi_3pops_CVLS_CVLN_Cross_snps.txt"

#Create python dictionary from snps file
dd1 = dadi.Misc.make_data_dict(snps1)

#**************
#projection sizes, in ALLELES not individuals
proj_1 = [14,30,18]
#pop_ids is a list which should match the populations headers of your SNPs file columns
pop_ids=['CVLS','CVLN','Cross']

#Convert this dictionary into folded AFS object
#[polarized = False] creates folded spectrum object
fs_1 = dadi.Spectrum.from_data_dict(dd1, pop_ids=pop_ids, projections = proj_1, polarized = False)

print '\n', '\n', "Data for spectrum:"
print "projection", proj_1
print "sample sizes", fs_1.sample_sizes
print "Segregating sites",fs_1.S(), '\n', '\n'


#======================================================================================
#create function to take in grid size and freq spectrum for a population, then run all 
#models 'x' times from optimized parameters from heavily perturbed basic starting values
#write output of parameter optimizations, theta, likelihood, and AIC for each replicate for 
#each model to file

def Three_Pop_Models(pts, fs, outfile, reps, y, model_name, params):
    print '\n',"============================================================================"
    print "Beginning analysis of {}".format(model_name)
    print "============================================================================"

    #create output file
    outname = "Round2_{0}_{1}_optimized.txt".format(outfile,model_name)
    fh_out = open(outname, 'a')
    fh_out.write("Model"+'\t'+"param_set"+'\t'+"Replicate"+'\t'+"log-likelihood"+'\t'+"theta"+'\t'+"AIC"+'\t'+"optimized_params"+'\n')
    fh_out.close()
    
    #variable to control number of loops per model (1 to x)
    x = int(reps) + int(1)
    
    ######################################################################################################################
    #Basic models
    ######################################################################################################################
    
    if model_name == "split_nomig":
        
        #####################################
        #Split with no migration
        #####################################
        print "---------------------------------------------------"
        print "Split with No Migration",'\n','\n'
        
        #first call a predefined model
        model_call = Models_3D.split_nomig

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0, 0]
        upper_bound = [30, 30, 30, 30, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, T1, T2]"

        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Split with No Migration"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, T1, T2]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt
            
            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*6)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    elif model_name == "split_symmig_all":
        
        #####################################
        #Split with symmetric migration
        #####################################
        print "---------------------------------------------------"
        print "Split with Symmetric Migration",'\n','\n'
        
        #first call a predefined model
        model_call = Models_3D.split_symmig_all

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 20, 20, 20, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, m3, T1, T2]"
        
        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Split with Symmetric Migration"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, m3, T1, T2]"+'\t') 
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*10)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'


    elif model_name == "split_symmig_adjacent":
        
        #####################################
        #Split with adjacent symmetric migration 
        #####################################
        print "---------------------------------------------------"
        print "Split with Adjacent Symmetric Migration",'\n','\n'
        
        #first call a predefined model
        model_call = Models_3D.split_symmig_adjacent

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 20, 20, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, T1, T2]"
        
        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Split with Adjacent Symmetric Migration"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, T1, T2]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*9)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    
    ######################################################################################################################
    #Refugial models
    ######################################################################################################################

    elif model_name == "refugia_1":
        
        #####################################
        #Refugia 1 with secondary contact
        #####################################
        print "---------------------------------------------------"
        print "Refugia 1 with secondary contact",'\n','\n'        

        #first call a predefined model
        model_call = Models_3D.refugia_1

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 20, 10, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, m1, m2, T1, T2, T3]"        

        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Refugia 1 with secondary contact"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, m1, m2, T1, T2, T3]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*9)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    elif model_name == "refugia_2":

        #####################################
        #Refugia 2 with secondary contact
        #####################################
        print "---------------------------------------------------"
        print "Refugia 2 with secondary contact",'\n','\n'
        
        #first call a predefined model
        model_call = Models_3D.refugia_2

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 20, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, m1, m2, T1, T2]"
        
        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Refugia 2 with secondary contact"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, m1, m2, T1, T2]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*8)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    elif model_name == "refugia_3":

        #####################################
        #Refugia with secondary contact, shortest isolation
        #####################################
        print "---------------------------------------------------"
        print "Refugia 3 with secondary contact",'\n','\n'
        
        #first call a predefined model
        model_call = Models_3D.refugia_3

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 20, 20, 10, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, T1a, T1b, T2]"
        
        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Refugia 3 with secondary contact"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, T1a, T1b, T2]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*10)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    
    ######################################################################################################################
    #Ancient migration models
    ######################################################################################################################

    elif model_name == "ancmig_3":

        #####################################
        #Ancient migration 3, long isolation
        #####################################
        print "---------------------------------------------------"
        print "Ancient migration 3",'\n','\n'        

        #first call a predefined model
        model_call = Models_3D.ancmig_3

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 10, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, mA, T1a, T1b, T2]"        

        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Ancient migration 3"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, mA, T1a, T1b, T2]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*8)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    elif model_name == "ancmig_2":

        #####################################
        #Ancient migration 2, shorter isolation
        #####################################
        print "---------------------------------------------------"
        print "Ancient migration 2",'\n','\n'        

        #first call a predefined model
        model_call = Models_3D.ancmig_2

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, mA, T1, T2]"        

        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Ancient migration 2"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, mA, T1, T2]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*7)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'

    elif model_name == "ancmig_1":

        #####################################
        #Ancient migration 1, shortest isolation
        #####################################
        print "---------------------------------------------------"
        print "Ancient migration 1",'\n','\n'
        
        #first call a predefined model
        model_call = Models_3D.ancmig_1

        #create an extrapolating function 
        func_exec = dadi.Numerics.make_extrap_log_func(model_call)

        #create parameter list for optimization, set bounds for search
        lower_bound = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0, 0, 0]
        upper_bound = [30, 30, 30, 30, 20, 20, 20, 10, 10, 10]
        print "parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, T1, T2, T3]"
        
        for i in range(1,x):
            fh_out = open(outname, 'a')
            fh_out.write("Ancient migration 1"+'\t')
            fh_out.write("parameter set = [nu1, nuA, nu2, nu3, mA, m1, m2, T1, T2, T3]"+'\t')
            fh_out.write("{}\t".format(i))
            print '\n', "Replicate {}:".format(i)
            print "starting parameters = ", params

            #perturb initial guesses
            params_perturbed = dadi.Misc.perturb_params(params, fold=2, upper_bound=upper_bound, lower_bound=lower_bound)

            #run optimization 
            params_opt = dadi.Inference.optimize_log_fmin(params_perturbed, fs, func_exec, pts,lower_bound=lower_bound, upper_bound=upper_bound, verbose=1, maxiter=y)
            print '\n',"optimized parameters = ", params_opt

            #simulate the model with the optimized parameters
            sim_model = func_exec(params_opt, fs.sample_sizes, pts)

            #calculate likelihood
            ll = dadi.Inference.ll_multinom(sim_model, fs)
            ll = np.around(ll, 2)
            print "likelihood = ", ll
            fh_out.write("{}\t".format(ll))

            #calculate theta
            theta = dadi.Inference.optimal_sfs_scaling(sim_model, fs)
            theta = np.around(theta, 2)
            print "Theta = ", theta
            fh_out.write("{}\t".format(theta))

            #calculate AIC 
            aic = ( -2*( float(ll))) + (2*10)
            print "AIC = ", aic, '\n', '\n'
            fh_out.write("{}\t".format(aic))

            for p in params_opt:
                p = np.around(p, 4)
                fh_out.write("{}\t".format(p))
            fh_out.write('\n')
            fh_out.close()

        print "---------------------------------------------------", '\n'



        
#======================================================================================
# Finally, execute model with appropriate arguments

# Three_Pop_Models(pts, fs, outfile, reps, maxiter, model_name, model_params):

# pts = grid choice (list of three numbers, ex. [20,30,40]

# fs = spectrum object name

# outfile = prefix for output naming (will result in "[prefix]_[model_name]_optimized_round1.txt")

# reps = integer to control number of replicates, ex. 10

# maxiter = max number of iterations per optimization step (not intuitive! see dadi user group)

# model_name = from this list ["split_nomig", "split_symmig_all", "split_symmig_adjacent", "refugia_1",
#        "refugia_2", "refugia_3", "ancmig_3", "ancmig_2", "ancmig_1"]

# model_params = list of parameter values to perturb and start optimizations from
#		ex. some_params = [4.787,0.465,7.071,1.879,0.181,0.635]



#===========================================================================
# enter best param values for each model here, presumably you will get these
# from the outputs of the previous script, "dadi_3D_01_first_optimizations.py"

#************** "split_nomig"
# 6 Values
split_nomig_params = [4.7878,0.4657,7.0718,1.8793,0.1819,0.6351]

#************** "split_symmig_all"
# 10 Values
split_symmig_all_params = [0.3645,2.3541,2.8694,0.1192,2.9680,0.2465,3.4061,2.2545,5.2956,0.3193]

#************** "split_symmig_adjacent"
# 9 Values
split_symmig_adjacent_params = [3.5506,3.6095,3.7157,1.1518,3.04188,0.5378,0.1777,5.8779,0.6790]

#************** "refugia_1"
# 9 Values
refugia_1_params = [0.9708,0.3971,1.5534,1.4487,0.7848,0.2466,0.5874,0.7914,0.2847]

#************** "refugia_2"
# 8 Values
refugia_2_params = [1.0230,5.8268,4.0113,0.8357,0.5673,1.3852,0.4637,0.4158]

#************** "refugia_3"
# 10 Values
refugia_3_params = [3.0755,3.4188,5.9098,1.1432,3.6431,0.1767,0.2083,2.5262,6.5821,1.1527]

#************** "ancmig_3"
# 8 Values
ancmig_3_params = [4.0832,4.3028,1.7475,3.9215,0.3003,1.7515,0.3969,0.2253]

#************** "ancmig_2"
# 7 Values
ancmig_2_params = [0.5117,6.7278,2.6933,0.7654,2.1216,0.4124,0.2513]

#************** "ancmig_1"
# 10 Values
ancmig_1_params = [1.5830,0.4784,7.2799,1.5639,3.5810,5.2661,6.5078,0.4697,2.2544,0.3212]



#**************
#Input some of the basic reusable arguments here
pts = [50,60,70]
fs = fs_1
outfile = "CVLS_CVLN_Cross"
reps = int(50)
maxiter = int(10)

#**************
# Here it is set up to call each model one by one sequentially, but this will take a very long time.
# I recommend blocking out all models except one (use a hash or delete), make several
# copies of the script and execute one model version for every core you have available.
# It will greatly speed up these steps, and sometimes if extrapolations fail the
# script will crash too.
# There are 20 models to test here. 

#Models from the Models_3D.py script 
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "split_nomig", split_nomig_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "split_symmig_all", split_symmig_all_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "split_symmig_adjacent", split_symmig_adjacent_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "refugia_1", refugia_1_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "refugia_2", refugia_2_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "refugia_3", refugia_3_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "ancmig_3", ancmig_3_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "ancmig_2", ancmig_2_params)
Three_Pop_Models(pts, fs, outfile, reps, maxiter, "ancmig_1", ancmig_1_params)



#===========================================================================
#clock it!

t_finish = datetime.now()
elapsed = t_finish - t_begin

print '\n', '\n', "-----------------------------------------------------------------------------------------------------"
print "Finished all analyses!"
print "Total time: {0} (H:M:S)".format(elapsed)
print "-----------------------------------------------------------------------------------------------------", '\n', '\n'
#===========================================================================

