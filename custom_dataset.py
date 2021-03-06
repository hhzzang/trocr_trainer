import torch
from torch.utils.data import Dataset
from PIL import Image
import os


class CustomDataset(Dataset):
    def __init__(self, df, processor, max_target_length=7, data_dir='./data/', tfms=None):
        self.root_dir = data_dir
        import pandas as pd
        if type(df) != type(pd.DataFrame()):
            self.df = self.make_df()
        else:
            self.df = df
        self.processor = processor
        self.max_target_length = max_target_length
        self.transform = tfms

    def __len__(self):
        return len(self.df)

    def make_df(self):
        import os
        import pandas as  pd
        label_path = os.path.join(self.root_dir, 'labels.txt')
        with open(label_path, 'r', encoding='utf-8') as f:
            data = f.read().split('\n')
        check = lambda x: x.split('.jpg') if len(x.split('.jpg')) == 2 else None
        return pd.DataFrame(map(check, data), columns=['file_name', 'text'])

    def __getitem__(self, idx):
        # get file name + text
        file_name = self.df['file_name'][idx]
        text = self.df['text'][idx]

        # prepare image (i.e. resize + normalize)
        image_dir = os.path.join(self.root_dir, 'images', f'{file_name}.jpg')
        image = Image.open(image_dir).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        # add labels (input_ids) by encoding the text

        labels = self.processor.tokenizer(text,
                                          padding="max_length",
                                          max_length=self.max_target_length,truncation=True).input_ids

        # important: make sure that PAD tokens are ignored by the loss function
        labels = [label if label != self.processor.tokenizer.pad_token_id else -100 for label in labels]

        encoding = {"pixel_values": pixel_values.squeeze(), "labels": torch.tensor(labels),'text': text}
        return encoding



class EmbeddingDataset(Dataset):
    def __init__(self, df, processor, max_target_length=7, data_dir='./data/', tfms=None):
        self.root_dir = data_dir
        import pandas as pd
        if type(df) != type(pd.DataFrame()):
            self.df = self.make_df()
        else:
            self.df = df
        self.processor = processor
        self.max_target_length = max_target_length
        self.transform = tfms

    def __len__(self):
        return len(self.df)

    def make_df(self):
        import os
        import pandas as  pd
        label_path = os.path.join(self.root_dir, 'aihub_labels.txt')
        with open(label_path, 'r', encoding='utf-8') as f:
            data = f.read().split('\n')
        check = lambda x: x.split('.jpg') if len(x.split('.jpg')) == 2 else False
        return pd.DataFrame(map(check, data), columns=['file_name', 'text'])

    def __getitem__(self, idx):
        # get file name + text
        file_name = self.df['file_name'][idx]
        text = self.df['text'][idx]

        # prepare image (i.e. resize + normalize)
        if int(file_name) <= int('01178909'):
            image_dir = os.path.join('ocr/apphia/kor_dataset/htr', 'images', f'{file_name}.png')
        elif int(file_name) <= int('03385349'):
            image_dir = os.path.join('ocr/apphia/kor_dataset/ocr', 'images', f'{file_name}.jpg')
        image = Image.open(image_dir).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        # add labels (input_ids) by encoding the text

        labels = self.processor.tokenizer(text,
                                          padding="max_length",
                                          max_length=self.max_target_length,truncation=True).input_ids
        input_ids = labels
        # important: make sure that PAD tokens are ignored by the loss function
        labels = [label if label != self.processor.tokenizer.pad_token_id else -100 for label in labels]
        
        encoding = {"pixel_values": pixel_values.squeeze(), "labels": torch.tensor(labels),'input_ids':input_ids}
        return encoding


if __name__ == '__main__':
    root_data_dir = './data/'
    from model_build import processor
    df = CustomDataset(None,processor=processor, data_dir=root_data_dir).df
    idx = 11000
    temp = df['text']
    print(temp[idx])
    tokens = processor.tokenizer(temp[idx],padding="max_length",max_length=256).input_ids
    print(tokens)
    print(processor.tokenizer.decode(tokens,skip_special_tokens=True))
