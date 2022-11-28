import sys
import os

import pandas as pd
import numpy as np
import torch
from easydict import EasyDict

from dataloader import Dataset
from src.model.meta import PoolFormer
from src.trainer import Trainer

save_path = os.getcwd()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 

# 전체
dir_root = r'E:\관광'
meta_df = pd.read_csv(dir_root + '/train.csv')

# cat weights
weights_c1 = np.load("cat1.npy")
weights_c2 = np.load("cat2.npy")
weights_c3 = np.load("cat3.npy")

args = EasyDict(
    {
     # Path settings
     'root':'train_dir',
     'save_dict' : os.path.join(dir_root, 'cat3_pool_h_224_focal'),
     'df':meta_df,
     # Model parameter settings
     'CODER':'poolformer_m36', # 'regnety_040', 'efficientnet-b0' ,poolformer_m36
     'drop_path_rate':0.2,
     'model_class': PoolFormer,
     'weight':weights_c3,
     'pretrained':"E:\관광\cat3_pool_h_224_focal\model_poolformer_m36_0_0.0268.pth",
     
     # Training parameter settings
     ## Base Parameter
     'img_size':224,
     'test_size':224,
     'BATCH_SIZE':16,
     'epochs':200,
     'optimizer':'Lamb',
     'lr':4e-5,
     'weight_decay':1e-3,
     'Dataset' : Dataset,
     'fold_num':1,
     'bagging_num':4,
     'label':'cat3',

     ## Augmentation
     'pad':True,

     #scheduler 
     'scheduler':'cos',
     ## Scheduler (OnecycleLR)
     'warm_epoch':5,
     'max_lr':1e-3,

     ### Cosine Annealing
     'min_lr':5e-6,
     'tmax':145,

     ## etc.
     'patience':20,
     'clipping':None,

     # Hardware settings
     'amp':True,
     'multi_gpu':False,
     'logging':False,
     'num_workers':4,
     'seed':42,
     'device':device,

    })

# def seed_everything(seed):
#     random.seed(seed)
#     os.environ["PYTHONHASHSEED"] = str(seed)
#     np.random.seed(seed)
#     torch.manual_seed(seed)
#     torch.cuda.manual_seed(seed)
#     torch.backends.cudnn.deterministic = True
#     torch.backends.cudnn.benchmark = False

if __name__ == '__main__': 
    # seed_everything(np.random.randint(1, 5000))
    print(args.CODER + " train..")
    trainer = Trainer(args)
    # trainer = Mixup_trainer(args)
    trainer.fit()