
## Azure AI Vision Face Samples

[![NuGet Version](https://img.shields.io/nuget/vpre/Azure.AI.Vision.Face)](https://aka.ms/azsdk-csharp-face-pkg)
[![PyPI - Version](https://img.shields.io/pypi/v/azure-ai-vision-face)](https://aka.ms/azsdk-python-face-pkg)
[![NPM Version](https://img.shields.io/npm/v/%40azure-rest%2Fai-vision-face)](https://www.npmjs.com/package/@azure-rest/ai-vision-face)
[![Maven Central Version](https://img.shields.io/maven-central/v/com.azure/azure-ai-vision-face)](https://central.sonatype.com/artifact/com.azure/azure-ai-vision-face)

Explore our samples and discover the things you can build with face service.

| Project | Description | C# | Py | JS | Java |
| :- | :- | :- | :- | :- | :- |
| [AndroidDetect](./AndroidDetect) | Detect and frame faces in an image on Android. | | | | ✅ |
| [CustomerCheckinManagement](./CustomerCheckinManagement) | Manage customer check-ins by leveraging face enrollment and identification. | | ✅ | | |
| [DemoWPF](./DemoWPF) | Run face detection, face grouping, finding similar faces, and face verification in Windows Presentation Foundation. | ✅ | | | |
| [EnrollWithReactNative](https://github.com/Azure-Samples/cognitive-services-FaceAPIEnrollmentSample) | Get started with the sample face enrollment application for Android/iOS. | | | ✅ | |
| [FacePhotoTagging](./FacePhotoTagging) | Enroll each person’s faces from image directories and tag faces for new input images. | | ✅ | | |
| [FindFaces](./FindFaces) | Create and manage face collections, add faces, and verify faces within images. | | ✅ | | |
| [PortraitProcessing](./PortraitProcessing) | Make a portrait image out of an original image. | ✅ | ✅ | | ✅ |
| [UnifiedFaceCollection](./UnifiedFaceCollection) | Provide a unified interface for managing both face and person, using face lists and person groups. | | ✅ | | |

> [!NOTE]
> The [face liveness detection solution](https://learn.microsoft.com/azure/ai-services/computer-vision/tutorials/liveness) requires additional mobile/web SDKs to start the camera, guide the end-user in adjusting their position, and compose the liveness payload. See the frontend app integration samples:
>
> | Platform | Sample | Dependency (Client SDK) |
> | :- | :- | :- |
> | Android | [azure-ai-vision-sdk/tree/main/samples/kotlin/face/FaceAnalyzerSample](https://github.com/Azure-Samples/azure-ai-vision-sdk/tree/main/samples/kotlin/face/FaceAnalyzerSample) | [azure-ai-vision-faceanalyzer](https://azure.github.io/azure-sdk-for-android/azure-ai-vision-faceanalyzer/com/azure/android/ai/vision/faceanalyzer/package-summary.html) |
> | iOS | [azure-ai-vision-sdk/tree/main/samples/swift/face/FaceAnalyzerSample](https://github.com/Azure-Samples/azure-ai-vision-sdk/tree/main/samples/swift/face/FaceAnalyzerSample) | [AzureAIVisionFace](https://azure.github.io/azure-sdk-for-ios/AzureAIVisionFace/index.html) |
> | Web | [azure-ai-vision-sdk/tree/main/samples/web](https://github.com/Azure-Samples/azure-ai-vision-sdk/tree/main/samples/web) | azure-ai-vision-faceanalyzer |


### Documentation

* https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity
* https://learn.microsoft.com/azure/ai-services/computer-vision/quickstarts-sdk/identity-client-library
* https://learn.microsoft.com/rest/api/face/operation-groups


### More SDK Samples

| Language | Link |
| :- | :- |
| C# | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/face/Azure.AI.Vision.Face/samples |
| Python | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples |
| JavaScript | https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/face/ai-vision-face-rest/samples |
| Java | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/face/azure-ai-vision-face/src/samples |


### Deprecated Samples

* https://github.com/Azure-Samples/Cognitive-Face-CSharp-sample
* https://github.com/Azure-Samples/cognitive-services-vision-face-finder
* https://github.com/Azure-Samples/cognitive-services-face-android-detect
* https://github.com/Azure-Samples/cognitive-services-dotnet-sdk-samples/tree/master/app-samples
* https://github.com/Azure-Samples/cognitive-services-dotnet-sdk-samples/tree/master/documentation-samples/quickstarts/Face
* https://github.com/Azure-Samples/cognitive-services-dotnet-sdk-samples/tree/master/samples/Face
* https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/tree/master/samples/face
* https://github.com/microsoft/Cognitive-Face-DotNetCore
* https://github.com/microsoft/Cognitive-Face-Python
* https://github.com/microsoft/Cognitive-Face-Windows
* https://github.com/microsoft/Cognitive-Face-Android
* https://github.com/microsoft/Cognitive-Face-iOS
* https://github.com/microsoft/Cognitive-Samples-IntelligentKiosk/tree/master/Kiosk/Views/FaceApiExplorer
