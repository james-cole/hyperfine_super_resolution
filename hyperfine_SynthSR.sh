#!/bin/bash
## James Cole 06/07/2021
dir=$1

mkdir ${dir}/SynthSR

t1=`find ${dir} -name T1.nii.gz`
t2=`find ${dir} -name T2.nii.gz | head -1`
## upsample T1 image
mri_convert $t1 ${dir}/SynthSR/t1_1mm.nii.gz --voxsize 1 1 1 -odt float
## co-register T2 to upsampled T1
flirt -ref ${dir}/SynthSR/t1_1mm.nii.gz -in $t2 -dof 6 -o ${dir}/SynthSR/t2_1mm.nii.gz -cost normmi
#reg_aladin -ref ${dir}/SynthSR/t1_1mm.nii.gz -flo $t2 -res ${dir}/SynthSR/t2_1mm.nii.gz -aff /tmp/aff.txt -omp 4 -rigOnly -pad 0.0
## remove skull
hd-bet -i ${dir}/SynthSR/t1_1mm.nii.gz
## dilate using python script
python3 
## edit ipynb
t1_1mm=$(realpath ${dir}/SynthSR/t1_1mm.nii.gz)
t2_1mm=$(realpath ${dir}/SynthSR/t2_1mm.nii.gz)
output_dir=$(realpath ${dir}/SynthSR/)
sed -e "s@T1_FILE@"${t1_1mm}"@" -e "s@T2_FILE@"${t2_1mm}"@" -e "s@OUTPUT_FILE@"${output_dir}"@" /home/jcole/Desktop/hyperfine_super_res/SynthSR_Hyperfine.ipynb > ${dir}/SynthSR/tmp_SynthSR.ipynb
## run ipynb
runipy ${dir}/SynthSR/tmp_SynthSR.ipynb
