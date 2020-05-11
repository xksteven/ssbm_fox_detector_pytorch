"""
Transformations that are applied identically to both the image and the target.
"""
import random

import torch
import torchvision
from torchvision.transforms import functional as F


class Compose(torchvision.transforms.Compose):
    """
    A modified version of the torchvision Compose transformation, that expects all
    provided transformations to accept an image and a target.
    """

    def __call__(self, image, target):
        for transform in self.transforms:
            image, target = transform(image, target)
        return image, target


class RandomGrayscale(torchvision.transforms.RandomGrayscale):
    """
    A modified version of the torchvision RandomGrayscale transformation.
    Does not modify the target.
    """

    def __call__(self, image, target):
        grayscale_image = super().__call__(image)
        return grayscale_image, target


class RandomHorizontalFlip(torchvision.transforms.RandomHorizontalFlip):
    """
    A modified version of the torchvision RandomHorizontalFlip that accepts a target.
    Expects ToFRCNNFormat to be called beforehand.
    """

    def __call__(self, image, target):
        if random.random() >= self.p:
            return image, target
        flipped_image = F.hflip(image)
        width, _ = flipped_image.size
        bbox = target["boxes"]
        bbox[:, [0, 2]] = width - bbox[:, [2, 0]]
        target["boxes"] = bbox
        return flipped_image, target


class RandomVerticalFlip(torchvision.transforms.RandomVerticalFlip):
    """
    A modified version of the torchvision RandomVerticalFlip that accepts a target.
    Expects ToFRCNNFormat to be called beforehand.
    """

    def __call__(self, image, target):
        if random.random() >= self.p:
            return image, target
        flipped_image = F.vflip(image)
        _, height = image.size
        bbox = target["boxes"]
        bbox[:, [1, 3]] = height - bbox[:, [3, 1]]
        target["boxes"] = bbox
        return flipped_image, target


class ToFRCNNFormat(object):
    """
    Converts a CocoDetection target into a format that works for Faster R-CNN.
    Does not modify the provided image.
    """

    def __call__(self, image, target):
        boxes = []
        labels = []
        if not isinstance(target, list):
            target = [target]
        image_id = torch.tensor([target[0]["image_id"]])
        for annotation in target:
            [min_x, min_y, width, height] = annotation["bbox"]
            max_x = min_x + width
            max_y = min_y + height
            box = [min_x, min_y, max_x, max_y]
            label = annotation["category_id"]

            boxes.append(box)
            labels.append(label)

        boxes_tensor = torch.Tensor(boxes)
        labels_tensor = torch.tensor(labels, dtype=torch.int64)
        return (
            image,
            {"boxes": boxes_tensor, "labels": labels_tensor, "image_id": image_id},
        )


class ToTensor(torchvision.transforms.ToTensor):
    """
    A modified version of torchvision ToTensor that accepts a target.
    """

    def __call__(self, image, target):
        image = F.to_tensor(image)
        return image, target
