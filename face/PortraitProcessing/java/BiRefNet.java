import java.awt.Graphics;
import java.awt.Image;
import java.awt.image.BufferedImage;
import java.util.Arrays;
import java.util.Collections;
import java.util.stream.IntStream;

import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtException;
import ai.onnxruntime.OrtSession;
import ai.onnxruntime.OrtSession.Result;

public class BiRefNet {
    private OrtEnvironment environment = null;
    private OrtSession session = null;

    public BiRefNet() throws OrtException {
        environment = OrtEnvironment.getEnvironment();
        session = environment.createSession("BiRefNet-portrait-epoch_150.onnx");
    }

    public BufferedImage predict(BufferedImage image) throws OrtException {
        // normalize input to (1, c=3, h=1024, w=1024)
        BufferedImage resized = getResizedBufferedImage(image, 1024, 1024);
        float scale = 1.0F;
        for (int x = 0; x < resized.getWidth(); x++) {
            for (int y = 0; y < resized.getHeight(); y++) {
                scale = Math.max((float) ((resized.getRGB(x, y) >> 16) & 0x000000FF), scale);
                scale = Math.max((float) ((resized.getRGB(x, y) >> 8) & 0x000000FF), scale);
                scale = Math.max((float) (resized.getRGB(x, y) & 0x000000FF), scale);
            }
        }
        float[][][][] normalized = new float[1][3][resized.getHeight()][resized.getWidth()];
        for (int x = 0; x < resized.getWidth(); x++) {
            for (int y = 0; y < resized.getHeight(); y++) {
                normalized[0][0][y][x] = (((float) ((resized.getRGB(x, y) >> 16) & 0x000000FF) / scale) - 0.485F) / 0.229F;
                normalized[0][1][y][x] = (((float) ((resized.getRGB(x, y) >> 8) & 0x000000FF) / scale) - 0.456F) / 0.224F;
                normalized[0][2][y][x] = (((float) (resized.getRGB(x, y) & 0x000000FF) / scale) - 0.406F) / 0.225F;
            }
        }

        // feed into the model
        OnnxTensor tensor = OnnxTensor.createTensor(environment, normalized);
        Result outputs = session.run(Collections.singletonMap("input_image", tensor));

        // normalize the (1, 1, h=1024, w=1024) output prediction
        float[][][][] pred = (float[][][][]) outputs.get(0).getValue();
        for (int x = 0; x < resized.getWidth(); x++) {
            for (int y = 0; y < resized.getHeight(); y++) {
                pred[0][0][y][x] = 1.0F / (1.0F + (float) Math.exp(-pred[0][0][y][x]));
            }
        }
        float ma = (float) Arrays.stream(pred).flatMap(Arrays::stream).flatMap(Arrays::stream).flatMapToDouble(f -> IntStream.range(0, f.length).mapToDouble(i -> f[i])).max().orElseThrow();
        float mi = (float) Arrays.stream(pred).flatMap(Arrays::stream).flatMap(Arrays::stream).flatMapToDouble(f -> IntStream.range(0, f.length).mapToDouble(i -> f[i])).min().orElseThrow();
        for (int x = 0; x < resized.getWidth(); x++) {
            for (int y = 0; y < resized.getHeight(); y++) {
                pred[0][0][y][x] = (pred[0][0][y][x] - mi) / (ma - mi);
            }
        }

        // convert and resize the matting back to BufferedImage object
        BufferedImage matting = new BufferedImage(resized.getWidth(), resized.getHeight(), BufferedImage.TYPE_INT_RGB);
        for (int x = 0; x < resized.getWidth(); x++) {
            for (int y = 0; y < resized.getHeight(); y++) {
                int value = (int) (pred[0][0][y][x] * 255.0F);
                matting.setRGB(x, y, (value << 16) | (value << 8) | value);
            }
        }
        return getResizedBufferedImage(matting, image.getWidth(), image.getHeight());
    }

    private BufferedImage getResizedBufferedImage(BufferedImage image, int width, int height) {
        BufferedImage resized = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics graphics = resized.getGraphics();
        graphics.drawImage(image.getScaledInstance(resized.getWidth(), resized.getHeight(), Image.SCALE_SMOOTH), 0, 0, null);
        graphics.dispose();
        return resized;
    }
}
