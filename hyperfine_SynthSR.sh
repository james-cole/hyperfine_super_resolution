#!/bin/bash
## James Cole 06/07/2021
if [ $# -lt 1 ] ; then 
	echo "Error, you must specify a directory containing hyperfine T1 and T2 data"  
	echo "Usage: ./hyperfine_SynthSR subj_001_hyperfine"
  exit 1
fi

## specify input directory as first argument
dir=$1
## mkdir output directory
mkdir ${dir}/SynthSR
## find hyperfine T1 and T2 scans
t1=`find ${dir} -name T1.nii.gz`
t2=`find ${dir} -name T2.nii.gz | head -1`
## upsample T1 image
mri_convert $t1 ${dir}/SynthSR/t1_1mm.nii.gz --voxsize 1 1 1 -odt float
## co-register T2 to upsampled T1 using FSL FLIRT or NiftyReg reg_aladin
#flirt -ref ${dir}/SynthSR/t1_1mm.nii.gz -in $t2 -dof 6 -o ${dir}/SynthSR/t2_1mm.nii.gz -cost normmi
reg_aladin -ref ${dir}/SynthSR/t1_1mm.nii.gz -flo $t2 -res ${dir}/SynthSR/t2_1mm.nii.gz -aff /tmp/aff.txt -omp 4 -rigOnly -pad 0.0
## remove skull using HD-BET, requires GPU
hd-bet -i ${dir}/SynthSR/t1_1mm.nii.gz
## dilate using python script, takes filename and number of iterations as input
python3 /data/Scripts/dilate_nii.py ${dir}/SynthSR/t1_1mm_bet_mask.nii.gz 25
## mask T1 and T2 images
fslmaths ${dir}/SynthSR/t1_1mm.nii.gz -mas ${dir}/SynthSR/t1_1mm_bet_mask_dilated.nii.gz ${dir}/SynthSR/t1_1mm_masked.nii.gz
fslmaths ${dir}/SynthSR/t2_1mm.nii.gz -mas ${dir}/SynthSR/t1_1mm_bet_mask_dilated.nii.gz ${dir}/SynthSR/t2_1mm_masked.nii.gz
## edit SynthSR ipynb template
t1_1mm=$(realpath ${dir}/SynthSR/t1_1mm_masked.nii.gz)
t2_1mm=$(realpath ${dir}/SynthSR/t2_1mm_masked.nii.gz)
output_dir=$(realpath ${dir}/SynthSR/)
sed -e "s@T1_FILE@"${t1_1mm}"@" -e "s@T2_FILE@"${t2_1mm}"@" -e "s@OUTPUT_FILE@"${output_dir}"@" /data/low_field/hyperfine/SynthSR_analysis/SynthSR_Hyperfine.ipynb > ${dir}/SynthSR/tmp_SynthSR.ipynb
## run customised SynthSR ipynb
runipy ${dir}/SynthSR/tmp_SynthSR.ipynb
## correct origin of t1_SR
python3 /data/Scripts/correct_origin.py --t1 ${dir}/SynthSR/t1_SR.nii.gz
echo "finished ${dir}"

