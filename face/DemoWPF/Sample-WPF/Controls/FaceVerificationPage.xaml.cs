﻿//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license.
//
// Microsoft Cognitive Services (formerly Project Oxford): https://www.microsoft.com/cognitive-services
//
// Microsoft Cognitive Services (formerly Project Oxford) GitHub:
// https://github.com/Microsoft/Cognitive-Face-Windows
//
// Copyright (c) Microsoft Corporation
// All rights reserved.
//
// MIT License:
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so, subject to
// the following conditions:
//
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED ""AS IS"", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
// LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
// OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
// WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

using Azure;
using Azure.AI.Vision.Face;

namespace Microsoft.ProjectOxford.Face.Controls
{
    /// <summary>
    /// Interaction logic for FaceVerification.xaml
    /// </summary>
    public partial class FaceVerificationPage : Page, INotifyPropertyChanged
    {
        #region Fields

        /// <summary>
        /// Description dependency property
        /// </summary>
        public static readonly DependencyProperty DescriptionProperty = DependencyProperty.Register("Description", typeof(string), typeof(FaceVerificationPage));

        /// <summary>
        /// RecognitionModel for Face detection and LargePersonGroup
        /// </summary>
        private static readonly FaceRecognitionModel recognitionModel = FaceRecognitionModel.Recognition04;

        /// <summary>
        /// DetectionModel for Face detection
        /// </summary>
        private static readonly FaceDetectionModel detectionModel = FaceDetectionModel.Detection03;

        /// <summary>
        /// Temporary group name for create person database
        /// </summary>
        public static readonly string SampleGroupName = Guid.NewGuid().ToString();

        /// <summary>
        /// Face detection result container for image on the left
        /// </summary>
        private ObservableCollection<Face> _leftResultCollection = new ObservableCollection<Face>();

        /// <summary>
        /// Face detection result container for image on the right
        /// </summary>
        private ObservableCollection<Face> _rightResultCollection = new ObservableCollection<Face>();

        /// <summary>
        /// Face to face verification result
        /// </summary>
        private string _faceVerifyResult;

        #endregion Fields

        #region Constructors

        /// <summary>
        /// Initializes a new instance of the <see cref="FaceVerificationPage" /> class
        /// </summary>
        public FaceVerificationPage()
        {
            InitializeComponent();
        }

        #endregion Constructors

        #region Events

        /// <summary>
        /// Implement INotifyPropertyChanged interface
        /// </summary>
        public event PropertyChangedEventHandler PropertyChanged;

        #endregion Events

        #region Properties
     
        /// <summary>
        /// Gets face detection results for image on the left
        /// </summary>
        public ObservableCollection<Face> LeftResultCollection
        {
            get
            {
                return _leftResultCollection;
            }
        }

        /// <summary>
        /// Gets max image size for UI rendering
        /// </summary>
        public int MaxImageSize
        {
            get
            {
                return 300;
            }
        }

        /// <summary>
        /// Gets face detection results for image on the right
        /// </summary>
        public ObservableCollection<Face> RightResultCollection
        {
            get
            {
                return _rightResultCollection;
            }
        }

        /// <summary>
        /// Gets or sets selected face verification result
        /// </summary>
        public string FaceVerifyResult
        {
            get
            {
                return _faceVerifyResult;
            }

            set
            {
                _faceVerifyResult = value;
                if (PropertyChanged != null)
                {
                    PropertyChanged(this, new PropertyChangedEventArgs("FaceVerifyResult"));
                }
            }
        }

        #endregion Properties

        #region Methods

        /// <summary>
        /// Pick image for detection, get detection result and put detection results into LeftResultCollection 
        /// </summary>
        /// <param name="sender">Event sender</param>
        /// <param name="e">Event argument</param>
        private async void LeftImagePicker_Click(object sender, RoutedEventArgs e)
        {
            // Show image picker, show jpg type files only
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.DefaultExt = ".jpg";
            dlg.Filter = "Image files(*.jpg, *png, *.bmp, *.gif) | *.jpg; *.png; *.bmp; *.gif";
            var result = dlg.ShowDialog();

            if (result.HasValue && result.Value)
            {
                FaceVerifyResult = string.Empty;

                // User already picked one image
                var pickedImagePath = dlg.FileName;
                var renderingImage = UIHelper.LoadImageAppliedOrientation(pickedImagePath);
                var imageInfo = UIHelper.GetImageInfoForRendering(renderingImage);
                LeftImageDisplay.Source = renderingImage;

                // Clear last time detection results
                LeftResultCollection.Clear();
                FaceVerifyButton.IsEnabled = (LeftResultCollection.Count!=0 && RightResultCollection.Count!=0);
                MainWindow.Log("Request: Detecting in {0}", pickedImagePath);
                var sw = Stopwatch.StartNew();

                // Call detection REST API, detect faces inside the image
                using (var fileStream = File.OpenRead(pickedImagePath))
                {
                    try
                    {
                        var faceServiceClient = FaceServiceClientHelper.GetInstance(this);
                        Response<IReadOnlyList<FaceDetectionResult>> response = await faceServiceClient.DetectAsync(BinaryData.FromStream(fileStream), detectionModel, recognitionModel, true);
                        IList<FaceDetectionResult> faces = response.Value.ToList();

                        // Handle REST API calling error
                        if (faces == null)
                        {
                            return;
                        }

                        MainWindow.Log("Response: Success. Detected {0} face(s) in {1}", faces.Count, pickedImagePath);

                        // Convert detection results into UI binding object for rendering
                        foreach (var face in UIHelper.CalculateFaceRectangleForRendering(faces, MaxImageSize, imageInfo))
                        {
                            // Detected faces are hosted in result container, will be used in the verification later
                            LeftResultCollection.Add(face);
                        }

                        FaceVerifyButton.IsEnabled = (LeftResultCollection.Count != 0 && RightResultCollection.Count != 0);
                    }
                    catch (RequestFailedException ex)
                    {
                        MainWindow.Log("Response: {0}. {1}", ex.ErrorCode, ex.Message);
                    }
                }
            }
            GC.Collect();
        }

        /// <summary>
        /// Pick image for detection, get detection result and put detection results into RightResultCollection 
        /// </summary>
        /// <param name="sender">Event sender</param>
        /// <param name="e">Event argument</param>
        private async void RightImagePicker_Click(object sender, RoutedEventArgs e)
        {
            // Show image picker, show jpg type files only
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.DefaultExt = ".jpg";
            dlg.Filter = "Image files(*.jpg, *.png, *.bmp, *.gif) | *.jpg; *.png; *.bmp; *.gif";
            var result = dlg.ShowDialog();

            if (result.HasValue && result.Value)
            {
                FaceVerifyResult = string.Empty;

                // User already picked one image
                var pickedImagePath = dlg.FileName;
                var renderingImage = UIHelper.LoadImageAppliedOrientation(pickedImagePath);
                var imageInfo = UIHelper.GetImageInfoForRendering(renderingImage);
                RightImageDisplay.Source = renderingImage;

                // Clear last time detection results
                RightResultCollection.Clear();
                FaceVerifyButton.IsEnabled = (LeftResultCollection.Count != 0 && RightResultCollection.Count != 0);

                MainWindow.Log("Request: Detecting in {0}", pickedImagePath);
                var sw = Stopwatch.StartNew();

                // Call detection REST API, detect faces inside the image
                using (var fileStream = File.OpenRead(pickedImagePath))
                {
                    try
                    {
                        var faceServiceClient = FaceServiceClientHelper.GetInstance(this);
                        Response<IReadOnlyList<FaceDetectionResult>> response = await faceServiceClient.DetectAsync(BinaryData.FromStream(fileStream), detectionModel, recognitionModel, true);
                        IList<FaceDetectionResult> faces = response.Value.ToList();

                        // Handle REST API calling error
                        if (faces == null)
                        {
                            return;
                        }

                        MainWindow.Log("Response: Success. Detected {0} face(s) in {1}", faces.Count, pickedImagePath);

                        // Convert detection results into UI binding object for rendering
                        foreach (var face in UIHelper.CalculateFaceRectangleForRendering(faces, MaxImageSize, imageInfo))
                        {
                            // Detected faces are hosted in result container, will be used in the verification later
                            RightResultCollection.Add(face);
                        }
                        FaceVerifyButton.IsEnabled = (LeftResultCollection.Count != 0 && RightResultCollection.Count != 0);
                    }
                    catch (RequestFailedException ex)
                    {
                        MainWindow.Log("Response: {0}. {1}", ex.ErrorCode, ex.Message);

                        return;
                    }
                }
            }
            GC.Collect();
        }

        /// <summary>
        /// Verify two detected faces, get whether these two faces belong to the same person
        /// </summary>
        /// <param name="sender">Event sender</param>
        /// <param name="e">Event argument</param>
        private async void Face2FaceVerification_Click(object sender, RoutedEventArgs e)
        {
            // Call face to face verification, verify REST API supports one face to one face verification only
            // Here, we handle single face image only
            if (LeftResultCollection.Count == 1 && RightResultCollection.Count == 1)
            {
                FaceVerifyResult = "Verifying...";
                var faceId1 = LeftResultCollection[0].FaceId;
                var faceId2 = RightResultCollection[0].FaceId;

                MainWindow.Log("Request: Verifying face {0} and {1}", faceId1, faceId2);

                // Call verify REST API with two face id
                try
                {
                    var faceServiceClient = FaceServiceClientHelper.GetInstance(this);
                    Response<FaceVerificationResult> response  = await faceServiceClient.VerifyFaceToFaceAsync(Guid.Parse(faceId1), Guid.Parse(faceId2));
                    FaceVerificationResult res = response.Value;

                    // Verification result contains IsIdentical (true or false) and Confidence (in range 0.0 ~ 1.0),
                    // here we update verify result on UI by FaceVerifyResult binding
                    FaceVerifyResult = string.Format("Confidence = {0:0.00}, {1}", res.Confidence,  res.IsIdentical ? "two faces belong to same person" : "two faces not belong to same person");
                    MainWindow.Log("Response: Success. Face {0} and {1} {2} to the same person", faceId1, faceId2, res.IsIdentical ? "belong" : "not belong");
                }
                catch (RequestFailedException ex)
                {
                    MainWindow.Log("Response: {0}. {1}", ex.ErrorCode, ex.Message);

                    return;
                }
            }
            else
            {
                MessageBox.Show("Verification accepts two faces as input, please pick images with only one detectable face in it.", "Warning", MessageBoxButton.OK);
            }
            GC.Collect();
        }

        #endregion Methods
    }
}