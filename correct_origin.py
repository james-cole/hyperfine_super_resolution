#!/usr/bin/env python3
__author__ = 'SBV'
import argparse
import nibabel as nib
import numpy as np
import os
import subprocess as sp
import sys

## updated by James Cole to 

# Begin of check_program_exists function
def check_program_exists(program):
    """
    #####################################################################################
    # def check_program_exists(program)
    # Function   : Checks if a command exists by exploring path directories
    # Param      : program, command name like 'ls' or 'cat' or 'echo' or anything.
    #####################################################################################
    """

    fpath, fname = os.path.split(program)
    result = 0
    if fpath:
        if os.path.isfile(program) and os.access(program, os.X_OK):
            result = 1

    # Go through system paths
    if result == 0:
        for path in os.environ.get('PATH').split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, fname)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                sys.path.append(path)
                result = 1

    # Go through python path
    if result == 0:
        for path in sys.path:
            path = path.strip('"')
            exe_file = os.path.join(path, fname)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                result = 1

    if result == 0:
        print("Didn't find "+program)
        exit(-1)
    
    return
# End of check_program_exists function


def execute_cmd(cmd):
    cmd_out = True
    try:
        cmd_out = sp.call(cmd, shell=True)
    except:
        print('The following command failed:\n  %s' % cmd)
        exit(-1)

    if cmd_out:
        print('Issue running:\n  %s' % cmd)
        exit(-1)


# Main function for taking command-line input arguments and call functions to generate pdf report
parser = argparse.ArgumentParser()
parser.add_argument('--t1', dest='t1', help='The T1 file to process', required=True)
#parser.add_argument('--t2', dest='t2', help='The T2 file to process', required=True)
args = parser.parse_args()

# Define TPM file on comic
#tpm_file="/SAN/medic/cort_myelin_mri/templates/tpm/TPM.nii"
# Define TPM file on James' workstation
tpm_file = '/data/software/spm12/tpm/TPM.nii'

# Extract data directory
t1_file = os.path.abspath(args.t1)
#t2_file = os.path.abspath(args.t2)
out_dir = os.path.dirname(t1_file)

# niftyreg dir on comic
comic_niftyreg_path = "/data/software/niftyreg_install/bin"
sys.path.append(comic_niftyreg_path)

# Check if all required programs exist
check_program_exists('reg_aladin')

## T1 processing
#cor_t1_filename = os.path.abspath('t1_SR_cor.nii')
cor_t1_filename = os.path.join(out_dir,'t1_SR_cor.nii')
if not os.path.exists(cor_t1_filename):
    # Do rigid registration
    rig_out = os.path.join(out_dir, 'rig.nii.gz')
    rig_aff = os.path.join(out_dir, 'rig.txt')
    rig_reg_cmd = '/data/software/niftyreg_install/bin/reg_aladin -ref %s -flo %s -aff %s -res %s -lp 5 -voff' % \
                 (tpm_file, t1_file, rig_aff, rig_out)
    execute_cmd(rig_reg_cmd)
    # Remove output file
    execute_cmd('rm -f %s' % rig_out)

    # Read output affine file and delete it
    rig_trafo = np.loadtxt(rig_aff)
    execute_cmd('rm -f %s' % rig_aff)

    # Load nifti and correct header
    nii = nib.load(t1_file)
    nii.affine[0,3] = nii.affine[0,3] - rig_trafo[0,3]
    nii.affine[1,3] = nii.affine[1,3] - rig_trafo[1,3]
    nii.affine[2,3] = nii.affine[2,3] - rig_trafo[2,3]

    # Save
    nib.save(nib.Nifti1Image(nii.get_fdata(), nii.affine, nii.header), cor_t1_filename)

## T2 processing
#cor_t2_filename = os.path.abspath('T2w_cor.nii')
#if not os.path.exists(cor_t2_filename):
    # Do rigid registration
#    rig_out = os.path.join(out_dir, 'rig.nii.gz')
#    rig_aff = os.path.join(out_dir, 'rig.txt')
#    rig_reg_cmd = '/data/software/niftyreg_install/bin/reg_aladin -ref %s -flo %s -aff %s -res %s -lp 5 -voff' % \
#                 (tpm_file, t2_file, rig_aff, rig_out)
#    execute_cmd(rig_reg_cmd)
    # Remove output file
#    execute_cmd('rm -f %s' % rig_out)

    # Read output affine file and delete it
#   rig_trafo = np.loadtxt(rig_aff)
#   execute_cmd('rm -f %s' % rig_aff)

    # Load nifti and correct header
#    nii = nib.load(t2_file)
#    nii.affine[0,3] = nii.affine[0,3] - rig_trafo[0,3]
#    nii.affine[1,3] = nii.affine[1,3] - rig_trafo[1,3]
#    nii.affine[2,3] = nii.affine[2,3] - rig_trafo[2,3]

    # Save
 #   nib.save(nib.Nifti1Image(nii.get_fdata(), nii.affine, nii.header), cor_t2_filename)

