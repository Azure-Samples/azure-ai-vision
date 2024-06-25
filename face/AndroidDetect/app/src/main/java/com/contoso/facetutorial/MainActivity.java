package com.contoso.facetutorial;

// <snippet_imports>
import java.io.*;
import java.util.*;
import android.app.*;
import android.content.*;
import android.net.*;
import android.os.*;
import android.view.*;
import android.graphics.*;
import android.widget.*;
import android.provider.*;
// </snippet_imports>

// <snippet_face_imports>
import com.azure.ai.vision.face.*;
import com.azure.ai.vision.face.models.*;
import com.azure.core.credential.*;
import com.azure.core.util.*;
// </snippet_face_imports>

public class MainActivity extends Activity {
    // <snippet_mainactivity_fields>
    // Add your Face endpoint to your environment variables.
    private final String apiEndpoint = System.getenv("FACE_ENDPOINT");
    // Add your Face subscription key to your environment variables.
    private final String subscriptionKey = System.getenv("FACE_SUBSCRIPTION_KEY");

    private final FaceClient faceServiceClient = new FaceClientBuilder()
            .endpoint(apiEndpoint)
            .credential(new AzureKeyCredential(subscriptionKey))
            .buildClient();

    private final int PICK_IMAGE = 1;
    private ProgressDialog detectionProgressDialog;
    // </snippet_mainactivity_fields>

    // <snippet_mainactivity_methods>
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Button button1 = findViewById(R.id.button1);
        button1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.setType("image/*");
                startActivityForResult(Intent.createChooser(
                        intent, "Select Picture"), PICK_IMAGE);
            }
        });

        detectionProgressDialog = new ProgressDialog(this);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PICK_IMAGE && resultCode == RESULT_OK &&
                data != null && data.getData() != null) {
            Uri uri = data.getData();
            try {
                Bitmap bitmap = MediaStore.Images.Media.getBitmap(
                        getContentResolver(), uri);
                ImageView imageView = findViewById(R.id.imageView1);
                imageView.setImageBitmap(bitmap);

                // Comment out for tutorial
                detectAndFrame(bitmap);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        // </snippet_mainactivity_methods>
    }

    // <snippet_detection_methods>
    // Detect faces by uploading a face image.
    // Frame faces after detection.
    private void detectAndFrame(final Bitmap imageBitmap) {
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream);

        AsyncTask<byte[], String, FaceDetectionResult[]> detectTask =
                new AsyncTask<byte[], String, FaceDetectionResult[]>() {
                    String exceptionMessage = "";

                    @Override
                    protected FaceDetectionResult[] doInBackground(byte[]... params) {
                        try {
                            publishProgress("Detecting...");
                            DetectOptions options = new DetectOptions(
                                    FaceDetectionModel.DETECTION_03,
                                    FaceRecognitionModel.RECOGNITION_04,
                                    false);
                            options.setReturnFaceLandmarks(true);
                            List<FaceDetectionResult> result = faceServiceClient.detect(
                                    BinaryData.fromBytes(params[0]),
                                    options);
                            if (result == null || result.isEmpty()){
                                publishProgress(
                                        "Detection Finished. Nothing detected");
                                return null;
                            }
                            publishProgress(String.format(
                                    "Detection Finished. %d face(s) detected",
                                    result.size()));
                            return result.stream().toArray(FaceDetectionResult[]::new);
                        } catch (Exception e) {
                            exceptionMessage = String.format(
                                    "Detection failed: %s", e.getMessage());
                            return null;
                        }
                    }

                    @Override
                    protected void onPreExecute() {
                        //TODO: show progress dialog
                        detectionProgressDialog.show();
                    }
                    @Override
                    protected void onProgressUpdate(String... progress) {
                        //TODO: update progress
                        detectionProgressDialog.setMessage(progress[0]);
                    }
                    @Override
                    protected void onPostExecute(FaceDetectionResult[] result) {
                        //TODO: update face frames
                        detectionProgressDialog.dismiss();

                        if(!exceptionMessage.equals("")){
                            showError(exceptionMessage);
                        }
                        if (result == null) return;

                        ImageView imageView = findViewById(R.id.imageView1);
                        Bitmap addRectangles = drawFaceRectanglesOnBitmap(imageBitmap, result);
                        Bitmap addLandmarks = drawFaceLandmarksOnBitmap(addRectangles, result);
                        imageView.setImageBitmap(addLandmarks);
                        imageBitmap.recycle();
                    }
                };

        detectTask.execute(outputStream.toByteArray());
    }

    private void showError(String message) {
        new AlertDialog.Builder(this)
                .setTitle("Error")
                .setMessage(message)
                .setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                    }})
                .create().show();
    }
    // </snippet_detection_methods>

    // <snippet_drawrectangles>
    private static Bitmap drawFaceRectanglesOnBitmap(
            Bitmap originalBitmap, FaceDetectionResult[] faces) {
        Bitmap bitmap = originalBitmap.copy(Bitmap.Config.ARGB_8888, true);
        Canvas canvas = new Canvas(bitmap);
        Paint paint = new Paint();
        paint.setAntiAlias(true);
        paint.setStyle(Paint.Style.STROKE);
        paint.setColor(Color.RED);
        paint.setStrokeWidth(10);
        if (faces != null) {
            for (FaceDetectionResult face : faces) {
                FaceRectangle faceRectangle = face.getFaceRectangle();
                canvas.drawRect(
                        faceRectangle.getLeft(),
                        faceRectangle.getTop(),
                        faceRectangle.getLeft() + faceRectangle.getWidth(),
                        faceRectangle.getTop() + faceRectangle.getHeight(),
                        paint);
            }
        }
        return bitmap;
    }
    // </snippet_drawrectangles>

    // <snippet_drawlandmarks>
    private static Bitmap drawFaceLandmarksOnBitmap(
            Bitmap originalBitmap, FaceDetectionResult[] faces) {
        Bitmap bitmap = originalBitmap.copy(Bitmap.Config.ARGB_8888, true);
        Canvas canvas = new Canvas(bitmap);
        Paint paint = new Paint();
        paint.setAntiAlias(true);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(5);
        if (faces != null) {
            for (FaceDetectionResult face : faces) {
                FaceLandmarks landmarks = face.getFaceLandmarks();
                paint.setColor(Color.BLUE);
                canvas.drawCircle(
                        (float) landmarks.getPupilLeft().getX(),
                        (float) landmarks.getPupilLeft().getY(),
                        5F,
                        paint);
                canvas.drawCircle(
                        (float) landmarks.getPupilRight().getX(),
                        (float) landmarks.getPupilRight().getY(),
                        5F,
                        paint);
                paint.setColor(Color.GREEN);
                canvas.drawCircle(
                        (float) landmarks.getNoseTip().getX(),
                        (float) landmarks.getNoseTip().getY(),
                        5F,
                        paint);
            }
        }
        return bitmap;
    }
    // </snippet_drawlandmarks>
}
