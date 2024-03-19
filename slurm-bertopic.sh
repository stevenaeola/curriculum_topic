#!/bin/bash
#SBATCH -N 1
#SBATCH -c 1
#SBATCH --gres=gpu
#SBATCH -p res-gpu-small
#SBATCH --qos=short
#SBATCH -t 01-00:00:00
#SBATCH --job-name=bertopic_hell-world
#SBATCH --mem=16G

source /etc/profile
source ../topic_env/bin/activate

python3 BERTopic_iticse.py
