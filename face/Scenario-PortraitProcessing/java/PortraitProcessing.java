import java.awt.Graphics;
import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.net.URL;
import java.util.Arrays;
import java.util.List;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;

import com.azure.ai.vision.face.FaceClient;
import com.azure.ai.vision.face.FaceClientBuilder;
import com.azure.ai.vision.face.models.DetectOptions;
import com.azure.ai.vision.face.models.FaceAttributeType;
import com.azure.ai.vision.face.models.FaceDetectionModel;
import com.azure.ai.vision.face.models.FaceDetectionResult;
import com.azure.ai.vision.face.models.FaceRecognitionModel;
import com.azure.core.credential.KeyCredential;
import com.azure.core.util.BinaryData;
import com.azure.core.util.ClientOptions;
import com.azure.core.util.Header;

public class PortraitProcessing {
    // This key for Face API.
    private static final String FACE_KEY = System.getenv("FACE_API_KEY");
    // The endpoint URL for Face API.
    private static final String FACE_ENDPOINT = System.getenv("FACE_ENDPOINT_URL");
    // Image url for portrait processing sample
    private static final String IMAGE_URL = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg";
    // Maximum image size
    private static final int MAX_IMAGE_SIZE = 1920;
    // JPEG quality
    private static final float JPEG_QUALITY = 0.95F;
    // Detection model option
    private static final FaceDetectionModel DETECTION_MODEL = FaceDetectionModel.DETECTION_03;
    // Recognition model option
    private static final FaceRecognitionModel RECO_MODEL = FaceRecognitionModel.RECOGNITION_04;
    // Face attribute options
    private static final List<FaceAttributeType> FACE_ATTRIBUTES = Arrays.asList(FaceAttributeType.ModelDetection03.BLUR, FaceAttributeType.ModelDetection03.HEAD_POSE, FaceAttributeType.ModelDetection03.MASK, FaceAttributeType.ModelRecognition04.QUALITY_FOR_RECOGNITION);
    // Margin ratio on face crop
    private static final float TOP_MARGIN_MAX = 0.75F;
    private static final float BOTTOM_MARGIN_MAX = 0.75F;
    private static final float LEFT_MARGIN_MAX = 1.5F;
    private static final float RIGHT_MARGIN_MAX = 1.5F;

    public static void main(String[] args) throws Exception {
        System.out.println("Sample code for portrait processing with Azure Face API and Background Removal.");

        // Read image from URL
        BufferedImage image = ImageIO.read(new URL(IMAGE_URL));

        // Resize image and compress with JPEG to reduce overall latency.
        int resizedWidth = image.getWidth();
        int resizedHeight = image.getHeight();
        if (resizedWidth > MAX_IMAGE_SIZE || resizedHeight > MAX_IMAGE_SIZE) {
            if (resizedWidth > resizedHeight) {
                resizedWidth = Math.min(resizedWidth, MAX_IMAGE_SIZE);
                resizedHeight = (int) ((float) resizedHeight * ((float) resizedWidth / (float) image.getWidth()));
            } else {
                resizedHeight = Math.min(resizedHeight, MAX_IMAGE_SIZE);
                resizedWidth = (int) ((float) resizedWidth * ((float) resizedHeight / (float) image.getHeight()));
            }
        }
        BufferedImage bufferedImage = new BufferedImage(resizedWidth, resizedHeight, BufferedImage.TYPE_INT_RGB);
        Graphics graphics = bufferedImage.getGraphics();
        graphics.drawImage(image.getScaledInstance(resizedWidth, resizedHeight, Image.SCALE_SMOOTH), 0, 0, null);
        graphics.dispose();
        ByteArrayOutputStream imageMemoryStream = new ByteArrayOutputStream();
        ImageWriter imageMemoryStreamWriter = ImageIO.getImageWritersByFormatName("jpg").next();
        ImageWriteParam imageMemoryStreamParam = imageMemoryStreamWriter.getDefaultWriteParam();
        imageMemoryStreamParam.setCompressionMode(ImageWriteParam.MODE_EXPLICIT);
        imageMemoryStreamParam.setCompressionQuality(JPEG_QUALITY);
        imageMemoryStreamWriter.setOutput(ImageIO.createImageOutputStream(imageMemoryStream));
        imageMemoryStreamWriter.write(null, new IIOImage(bufferedImage, null, null), imageMemoryStreamParam);
        imageMemoryStreamWriter.dispose();

        // Detect faces in the image
        ClientOptions clientOptions = new ClientOptions().setHeaders(Arrays.asList(new Header("X-MS-AZSDK-Telemetry", "sample=portrait-processing")));
        FaceClient faceClient = new FaceClientBuilder().endpoint(FACE_ENDPOINT).credential(new KeyCredential(FACE_KEY)).clientOptions(clientOptions).buildClient();
        DetectOptions options = new DetectOptions(DETECTION_MODEL, RECO_MODEL, false).setReturnFaceAttributes(FACE_ATTRIBUTES).setReturnFaceLandmarks(true);
        List<FaceDetectionResult> detectedFaces = faceClient.detect(BinaryData.fromBytes(imageMemoryStream.toByteArray()), options);

        // Check portrait related attributes and propose crop rectangle for background removal
        // Please note that the face attributes can be used to filter out low-quality images for portrait processing.
        int cropLeft = 0;
        int cropTop = 0;
        int cropRight = 0;
        int cropBottom = 0;
        System.out.println("Number of faces detected: " + detectedFaces.size());

        if (!detectedFaces.isEmpty()) {
            // Use the first face as an example
            FaceDetectionResult face = detectedFaces.get(0);

            // Face rectangle
            int faceWidth = face.getFaceRectangle().getWidth();
            int faceHeight = face.getFaceRectangle().getHeight();
            int faceLeft = face.getFaceRectangle().getLeft();
            int faceTop = face.getFaceRectangle().getTop();
            System.out.println("Face detected: width=" + faceWidth + ", height=" + faceHeight + ", left=" + faceLeft + ", top=" + faceTop);

            // Head pose
            System.out.println("Head pose: yaw=" + face.getFaceAttributes().getHeadPose().getYaw() + ", pitch=" + face.getFaceAttributes().getHeadPose().getPitch() + ", roll=" + face.getFaceAttributes().getHeadPose().getRoll());

            // Quality
            System.out.println("Quality: " + face.getFaceAttributes().getQualityForRecognition());

            // Blur
            System.out.println("Blur: level=" + face.getFaceAttributes().getBlur().getBlurLevel() + ", value=" + face.getFaceAttributes().getBlur().getValue());

            // Mask
            System.out.println("Mask: type=" + face.getFaceAttributes().getMask().getType() + ", nose and mouth covered=" + face.getFaceAttributes().getMask().isNoseAndMouthCovered());

            // Calculate crop for background removal
            float leftMargin = faceLeft - faceWidth * LEFT_MARGIN_MAX;
            float topMargin = faceTop - faceHeight * TOP_MARGIN_MAX;
            float rightMargin = faceLeft + faceWidth + faceWidth * RIGHT_MARGIN_MAX;
            float bottomMargin = faceTop + faceHeight + faceHeight * BOTTOM_MARGIN_MAX;

            cropLeft = Math.max((int) leftMargin, 0);
            cropTop = Math.max((int) topMargin, 0);
            cropRight = Math.min((int) rightMargin, bufferedImage.getWidth());
            cropBottom = Math.min((int) bottomMargin, bufferedImage.getHeight());
        } else {
            System.out.println("No face detected.");
        }

        if (!detectedFaces.isEmpty()) {
            // crop the face
            BufferedImage crop = bufferedImage.getSubimage(cropLeft, cropTop, cropRight - cropLeft, cropBottom - cropTop);

            // remove the background
            BufferedImage matting = new BiRefNet().predict(crop);
            ImageIO.write(matting, "bmp", new File("detection2_matting.bmp"));

            // merge the image with the foreground matting
            BufferedImage portrait = new BufferedImage(crop.getWidth(), crop.getHeight(), BufferedImage.TYPE_INT_ARGB);
            int[] cropPixels = crop.getRGB(0, 0, crop.getWidth(), crop.getHeight(), null, 0, crop.getWidth());
            int[] mattingPixels = matting.getRGB(0, 0, matting.getWidth(), matting.getHeight(), null, 0, matting.getWidth());
            int[] portraitPixels = portrait.getRGB(0, 0, portrait.getWidth(), portrait.getHeight(), null, 0, portrait.getWidth());
            for (int i = 0; i < portraitPixels.length; i++) {
                int alpha = (((mattingPixels[i] >> 16) & 0x000000FF) + ((mattingPixels[i] >> 8) & 0x000000FF) + (mattingPixels[i] & 0x000000FF)) / 3;
                portraitPixels[i] = (cropPixels[i] & 0x00FFFFFF) | (alpha << 24);
            }
            portrait.setRGB(0, 0, portrait.getWidth(), portrait.getHeight(), portraitPixels, 0, portrait.getWidth());
            ImageIO.write(portrait, "png", new File("detection2_portrait.png"));
        } else {
            System.out.println("No face is detect. No portrait image is generated.");
        }

        System.out.println("End of the sample for portrait processing.");
    }
}
