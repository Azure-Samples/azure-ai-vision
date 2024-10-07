# -*- coding: utf-8 -*-

import numpy as np
import onnxruntime as ort
import PIL

class BiRefNet:

    def __init__(self):
        self.session = ort.InferenceSession("BiRefNet-portrait-epoch_150.onnx")

    def predict(self, image: PIL.Image.Image) -> PIL.Image.Image:
        # normalize input to (1, c=3, h=1024, w=1024)
        normalized = image.convert("RGB").resize((1024, 1024), PIL.Image.Resampling.LANCZOS)
        normalized = np.array(normalized).astype(np.float32)
        normalized = normalized / np.max(normalized)
        normalized[:, :, 0] = (normalized[:, :, 0] - 0.485) / 0.229
        normalized[:, :, 1] = (normalized[:, :, 1] - 0.456) / 0.224
        normalized[:, :, 2] = (normalized[:, :, 2] - 0.406) / 0.225
        normalized = np.expand_dims(normalized.transpose((2, 0, 1)), 0)

        # feed into the model
        outputs = self.session.run(None, {"input_image": normalized})

        # normalize the (1, 1, h=1024, w=1024) output prediction
        pred = 1 / (1 + np.exp(-outputs[0][0, 0, :, :]))
        ma = np.max(pred)
        mi = np.min(pred)
        pred = (pred - mi) / (ma - mi)

        # convert and resize the matting back to PIL object
        matting = PIL.Image.fromarray((pred * 255).astype(np.uint8), mode="L")
        return matting.resize(image.size, PIL.Image.Resampling.LANCZOS)
