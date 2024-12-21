import torchvision.models as models
import torchvision.transforms as transforms
import torch


def get_model_pipeline():
    resnet = models.resnet50(pretrained=True)
    resnet.eval()

    resnet = torch.nn.Sequential(*list(resnet.children())[:-1])

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    return resnet, transform
