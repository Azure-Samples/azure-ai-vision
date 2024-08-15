using Azure;
using Azure.AI.Vision.Face;
using Azure.Core;
using Azure.Core.Pipeline;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Net.Http.Headers;

// This key for Face API.
string? FACE_KEY = Environment.GetEnvironmentVariable("FACE_API_KEY");
// The endpoint URL for Face API.
string? FACE_ENDPOINT = Environment.GetEnvironmentVariable("FACE_ENDPOINT_URL");
// This key for Background Removal API.
string? BACKGROUND_API_KEY = Environment.GetEnvironmentVariable("BACKGROUND_API_KEY");
// The endpoint URL for Background Removal.
string? BACKGROUND_ENDPOINT = Environment.GetEnvironmentVariable("BACKGROUND_ENDPOINT_URL");
// API version for Background Removal
const string BACKGROUND_REMOVAL_API_VERSION = "2023-02-01-preview";
// Foreground matting mode for Background Removal API
const string FOREGROUND_MATTING_MODE = "foregroundMatting";
// Image url for portrait processing sample
const string IMAGE_URL = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg";
// Maximum image size
const int MAX_IMAGE_SIZE = 1920;
// JPEG quality
const long JPEG_QUALITY = 95L;
// Detection model option
FaceDetectionModel DETECTION_MODEL = FaceDetectionModel.Detection03;
// Recognition model option
FaceRecognitionModel RECO_MODEL = FaceRecognitionModel.Recognition04;
// Face attribute options
FaceAttributeType[] FACE_ATTRIBUTES = [FaceAttributeType.Detection03.Blur, FaceAttributeType.Detection03.HeadPose, FaceAttributeType.Detection03.Mask, FaceAttributeType.Recognition04.QualityForRecognition];
// Margin ratio on face crop
const float TOP_MARGIN_MAX = 0.75F;
const float BOTTOM_MARGIN_MAX = 0.75F;
const float LEFT_MARGIN_MAX = 1.5F;
const float RIGHT_MARGIN_MAX = 1.5F;

Console.WriteLine("Sample code for portrait processing with Azure Face API and Background Removal API.");

// Read image from URL
HttpClient httpClient = new HttpClient();
Image image = Image.FromStream(await httpClient.GetStreamAsync(IMAGE_URL));

// Resize image and compress with JPEG to reduce overall latency.
int resizedWidth = image.Width;
int resizedHeight = image.Height;
if (resizedWidth > MAX_IMAGE_SIZE || resizedHeight > MAX_IMAGE_SIZE)
{
    if (resizedWidth > resizedHeight)
    {
        resizedWidth = Math.Min(resizedWidth, MAX_IMAGE_SIZE);
        resizedHeight = (int)((float)resizedHeight * ((float)resizedWidth / (float)image.Width));
    }
    else
    {
        resizedHeight = Math.Min(resizedHeight, MAX_IMAGE_SIZE);
        resizedWidth = (int)((float)resizedWidth * ((float)resizedHeight / (float)image.Height));
    }
}
Bitmap bitmap = new Bitmap(resizedWidth, resizedHeight);
using (Graphics graphics = Graphics.FromImage(bitmap))
{
    graphics.InterpolationMode = InterpolationMode.High;
    graphics.SmoothingMode = SmoothingMode.HighQuality;
    graphics.PixelOffsetMode = PixelOffsetMode.HighQuality;
    graphics.CompositingQuality = CompositingQuality.HighQuality;
    graphics.DrawImage(image, 0, 0, resizedWidth, resizedHeight);
}
MemoryStream imageMemoryStream = new MemoryStream();
bitmap.Save(
    imageMemoryStream,
    ImageCodecInfo.GetImageEncoders().First(c => c.FormatID == ImageFormat.Jpeg.Guid),
    new EncoderParameters() { Param = [new EncoderParameter(Encoder.Quality, JPEG_QUALITY)] });

// Detect faces in the image
var clientOptions = new AzureAIVisionFaceClientOptions();
clientOptions.AddPolicy(new SampleUsageTrackingPolicy(), HttpPipelinePosition.PerCall);
FaceClient faceClient = new FaceClient(new Uri(FACE_ENDPOINT), new AzureKeyCredential(FACE_KEY), clientOptions);
imageMemoryStream.Seek(0L, SeekOrigin.Begin);
Response<IReadOnlyList<FaceDetectionResult>> detectResponse = await faceClient.DetectAsync(
    BinaryData.FromStream(imageMemoryStream),
    DETECTION_MODEL,
    RECO_MODEL,
    returnFaceId: false,
    returnFaceAttributes: FACE_ATTRIBUTES,
    returnFaceLandmarks: true);
IReadOnlyList<FaceDetectionResult> detectedFaces = detectResponse.Value;

// Check portrait related attributes and propose crop rectangle for background removal
// Please note that the face attributes can be used to filter out low-quality images for portrait processing.
int cropLeft = 0;
int cropTop = 0;
int cropRight = 0;
int cropBottom = 0;
Console.WriteLine($"Number of faces detected: {detectedFaces.Count}");

if (detectedFaces.Count > 0)
{
    // Use the first face as an example
    FaceDetectionResult face = detectedFaces.First();

    // Face rectangle
    int faceWidth = face.FaceRectangle.Width;
    int faceHeight = face.FaceRectangle.Height;
    int faceLeft = face.FaceRectangle.Left;
    int faceTop = face.FaceRectangle.Top;
    Console.WriteLine($"Face detected: width={faceWidth}, height={faceHeight}, left={faceLeft}, top={faceTop}");

    // Head pose
    Console.WriteLine($"Head pose: yaw={face.FaceAttributes.HeadPose.Yaw}, pitch={face.FaceAttributes.HeadPose.Pitch}, roll={face.FaceAttributes.HeadPose.Roll}");

    // Quality
    Console.WriteLine($"Quality: {face.FaceAttributes.QualityForRecognition}");

    // Blur
    Console.WriteLine($"Blur: level={face.FaceAttributes.Blur.BlurLevel}, value={face.FaceAttributes.Blur.Value}");

    // Mask
    Console.WriteLine($"Mask: type={face.FaceAttributes.Mask.Type}, nose and mouth covered={face.FaceAttributes.Mask.NoseAndMouthCovered}");

    // Calculate crop for background removal
    float leftMargin = faceLeft - faceWidth * LEFT_MARGIN_MAX;
    float topMargin = faceTop - faceHeight * TOP_MARGIN_MAX;
    float rightMargin = faceLeft + faceWidth + faceWidth * RIGHT_MARGIN_MAX;
    float bottomMargin = faceTop + faceHeight + faceHeight * BOTTOM_MARGIN_MAX;

    cropLeft = Math.Max((int)leftMargin, 0);
    cropTop = Math.Max((int)topMargin, 0);
    cropRight = Math.Min((int)rightMargin, bitmap.Width);
    cropBottom = Math.Min((int)bottomMargin, bitmap.Height);
}
else
{
    Console.WriteLine("No face detected.");
}

if (detectedFaces.Count > 0)
{
    // crop the face
    Bitmap portrait = bitmap.Clone(Rectangle.FromLTRB(cropLeft, cropTop, cropRight, cropBottom), PixelFormat.Format32bppArgb);
    MemoryStream cropMemoryStream = new MemoryStream();
    portrait.Save(
        cropMemoryStream,
        ImageCodecInfo.GetImageEncoders().First(c => c.FormatID == ImageFormat.Jpeg.Guid),
        new EncoderParameters() { Param = [new EncoderParameter(Encoder.Quality, JPEG_QUALITY)] });

    // remove the background
    string url = $"{BACKGROUND_ENDPOINT}computervision/imageanalysis:segment?api-version={BACKGROUND_REMOVAL_API_VERSION}&mode={FOREGROUND_MATTING_MODE}";
    cropMemoryStream.Seek(0, SeekOrigin.Begin);
    using (StreamContent streamContent = new StreamContent(cropMemoryStream))
    {
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");
        streamContent.Headers.Add("Ocp-Apim-Subscription-Key", BACKGROUND_API_KEY);
        using (HttpResponseMessage response = await httpClient.PostAsync(url, streamContent))
        {
            if (response.IsSuccessStatusCode)
            {
                Bitmap matting = new Bitmap(Image.FromStream(await response.Content.ReadAsStreamAsync()));
                matting.Save("detection2_matting.bmp");

                // merge the image with the foreground matting
                for (int x = 0; x < portrait.Width; x++)
                {
                    for (int y = 0; y < portrait.Height; y++)
                    {
                        int alpha = ((int)matting.GetPixel(x, y).R + (int)matting.GetPixel(x, y).G + (int)matting.GetPixel(x, y).B) / 3;
                        portrait.SetPixel(x, y, Color.FromArgb(alpha, portrait.GetPixel(x, y).R, portrait.GetPixel(x, y).G, portrait.GetPixel(x, y).B));
                    }
                }
                portrait.Save("detection2_portrait.png");
            }
            else
            {
                Console.WriteLine("Background removal failed. No portrait image is generated.");
            }
        }
    }
}
else
{
    Console.WriteLine("No face is detect. No portrait image is generated.");
}

Console.WriteLine("End of the sample for portrait processing.");

class SampleUsageTrackingPolicy : HttpPipelineSynchronousPolicy
{
    public override void OnSendingRequest(HttpMessage message)
    {
        message.Request.Headers.Add("X-MS-AZSDK-Telemetry", "sample=portrait-processing");
    }
}