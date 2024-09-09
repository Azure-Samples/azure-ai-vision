using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using System.Drawing;

namespace PortraitProcessing
{
    internal class BiRefNet
    {
        private InferenceSession _session;

        internal BiRefNet()
        {
            _session = new InferenceSession("BiRefNet-portrait-epoch_150.onnx");
        }

        internal Bitmap Predict(Bitmap image)
        {
            // normalize input to (1, c=3, h=1024, w=1024)
            Bitmap resized = new Bitmap(image, new Size(1024, 1024));
            float scale = 1.0F;
            for (int x = 0; x < resized.Width; x++)
            {
                for (int y = 0; y < resized.Height; y++)
                {
                    scale = Math.Max((float)resized.GetPixel(x, y).R, scale);
                    scale = Math.Max((float)resized.GetPixel(x, y).G, scale);
                    scale = Math.Max((float)resized.GetPixel(x, y).B, scale);
                }
            }
            DenseTensor<float> tensor = new DenseTensor<float>([1, 3, resized.Height, resized.Width]);
            for (int x = 0; x < resized.Width; x++)
            {
                for (int y = 0; y < resized.Height; y++)
                {
                    tensor[0, 0, y, x] = (((float)resized.GetPixel(x, y).R / scale) - 0.485F) / 0.229F;
                    tensor[0, 1, y, x] = (((float)resized.GetPixel(x, y).G / scale) - 0.456F) / 0.224F;
                    tensor[0, 2, y, x] = (((float)resized.GetPixel(x, y).B / scale) - 0.406F) / 0.225F;
                }
            }

            // feed into the model
            using IDisposableReadOnlyCollection<DisposableNamedOnnxValue> outputs = _session.Run([NamedOnnxValue.CreateFromTensor("input_image", tensor)]);

            // normalize the (1, 1, h=1024, w=1024) output prediction
            Tensor<float> pred = outputs.First().AsTensor<float>();
            for (int x = 0; x < resized.Width; x++)
            {
                for (int y = 0; y < resized.Height; y++)
                {
                    pred[0, 0, y, x] = 1.0F / (1.0F + (float)Math.Exp(-pred[0, 0, y, x]));
                }
            }
            float ma = pred.Max();
            float mi = pred.Min();
            for (int x = 0; x < resized.Width; x++)
            {
                for (int y = 0; y < resized.Height; y++)
                {
                    pred[0, 0, y, x] = (pred[0, 0, y, x] - mi) / (ma - mi);
                }
            }

            // convert and resize the matting back to Bitmap object
            Bitmap matting = new Bitmap(resized.Width, resized.Height);
            for (int x = 0; x < resized.Width; x++)
            {
                for (int y = 0; y < resized.Height; y++)
                {
                    matting.SetPixel(x, y, Color.FromArgb((int)(pred[0, 0, y, x] * 255.0F), (int)(pred[0, 0, y, x] * 255.0F), (int)(pred[0, 0, y, x] * 255.0F)));
                }
            }
            return new Bitmap(matting, new Size(image.Width, image.Height));
        }
    }
}
