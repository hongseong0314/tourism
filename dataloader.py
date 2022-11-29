import re
import os
import random
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch.utils.data.sampler import SubsetRandomSampler
from torchvision import transforms
import json

def expand2square(pil_img):
    background_color = (0,0,0)
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result

class Dataset(torch.utils.data.Dataset):
    """
    dir_path : 데이터폴더 경로
    meta_df : 가져올 데이터 csv
    mode : 불러 올 데이터(train or test)
    mix_up : mix_up augmentation 유무
    reverse : reverse augmentation 유무
    sub_data : emnist 로 만든 sub data 사용 유무
    """
    def __init__(self,
                 files,
                 mode='train',
                 label= 'cat3',
                 img_size=224,
                 pad=True,
                 ):
        
        self.files = files
        self.pad = pad
        self.mode = mode
        self.label = label
        self.root = r'E:\관광'
        self.train_mode = transforms.Compose([
                    transforms.Resize((img_size,img_size)),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomVerticalFlip(),
                    # transforms.RandomRotation(90),
                    # transforms.RandomAffine((20)),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) 
                            ])
        """
        transforms.RandomAffine((20)),
        transforms.RandomRotation(90),
        
        """
        self.test_mode = transforms.Compose([
                        transforms.Resize((img_size,img_size)),
                        transforms.ToTensor(),
                        transforms.Normalize([0.485, 0.456, 0.406],[0.229, 0.224, 0.225])
                            ])

        # label encoder, decoder 
        with open(os.path.join("endecoder", label), 'r') as rf:
            coder = json.load(rf)
            self.cat2en = coder['{:s}toen'.format(label)]
            self.en2cat = coder['ento{:s}'.format(label)]
        
    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, index):
        data = self.files.iloc[index, ]
        labels = data[self.label]
        labels = self.cat2en[labels]

        image = Image.open(os.path.join(self.root, data.img_path)).convert('RGB')
        sample = {'image': image, 'labels':labels}

        # train mode transform
        if self.mode == 'train':
            if self.pad:
                sample['image'] = expand2square(sample['image'])
            try:
                sample['image'] = self.train_mode(sample['image'])
            except TypeError:
                print(data, sample['image'])

        # test mode transform
        elif self.mode == 'test' or self.mode == 'valid':
            if self.pad:
                sample['image'] = expand2square(sample['image'])
            sample['image'] = self.test_mode(sample['image'])
        return sample

class Dataset_test(torch.utils.data.Dataset):
    """
    dir_path : 데이터폴더 경로
    meta_df : 가져올 데이터 csv
    mode : 불러 올 데이터(train or test)
    mix_up : mix_up augmentation 유무
    reverse : reverse augmentation 유무
    sub_data : emnist 로 만든 sub data 사용 유무
    """
    def __init__(self,
                 files,
                 label= 'cat3',
                 img_size=224,
                 pad=True,
                 ):
        
        self.files = files
        self.pad = pad
        self.label = label
        self.root = r'E:\관광'
        self.test_mode = transforms.Compose([
                        transforms.Resize((img_size,img_size)),
                        transforms.ToTensor(),
                        transforms.Normalize([0.485, 0.456, 0.406],[0.229, 0.224, 0.225])
                            ])

        # label encoder, decoder 
        with open(os.path.join("endecoder", label), 'r') as rf:
            coder = json.load(rf)
            self.cat2en = coder['{:s}toen'.format(label)]
            self.en2cat = coder['ento{:s}'.format(label)]
        
    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, index):
        data = self.files.iloc[index, ]

        image = Image.open(os.path.join(self.root, data.img_path)).convert('RGB')
        sample = {'image': image}

        if self.pad:
            sample['image'] = expand2square(sample['image'])
        sample['image'] = self.test_mode(sample['image'])
        return sample
    
class UnNormalize(object):
    """
    정규화 inverse 한다.
    """
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        for t, m, s in zip(tensor, self.mean, self.std):
            t.mul_(s).add_(m)
        return tensor

def tensor2img(img):
    """
    tensor 형태에서 numpy 배열로 바꿔서 반환
    """
    unorm = UnNormalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
    a = unorm(img).numpy()
    a = a.transpose(1, 2, 0)
    return a