﻿//
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
using System.Windows.Media;

using Azure;
using Azure.AI.Vision.Face;

namespace Microsoft.ProjectOxford.Face.Controls
{
    /// <summary>
    /// Interaction logic for FaceDetectionPage.xaml
    /// </summary>
    public partial class FaceDetectionPage : Page, INotifyPropertyChanged
    {

        #region Fields

        /// <summary>
        /// Description dependency property
        /// </summary>
        public static readonly DependencyProperty DescriptionProperty = DependencyProperty.Register("Description", typeof(string), typeof(FaceDetectionPage));

        /// <summary>
        /// RecognitionModel for Face detection
        /// </summary>
        private static readonly FaceRecognitionModel recognitionModel = FaceRecognitionModel.Recognition04;

        /// <summary>
        /// Face detection results in list container
        /// </summary>
        private ObservableCollection<Face> _detectedFaces = new ObservableCollection<Face>();

        /// <summary>
        /// Face detection results in text string
        /// </summary>
        private string _detectedResultsInText;

        /// <summary>
        /// Face detection results container
        /// </summary>
        private ObservableCollection<Face> _resultCollection = new ObservableCollection<Face>();

        /// <summary>
        /// Container of face detection results with faces rotated by head poses
        /// </summary>
        private ObservableCollection<Face> _resultCollectionWithHeadpose = new ObservableCollection<Face>();

        /// <summary>
        /// Image used for rendering and detecting
        /// </summary>
        private ImageSource _selectedFile;

        /// <summary>
        /// Whether to draw rectangles rotated by head poses
        /// </summary>
        private bool _drawHeadPose;

        #endregion Fields

        #region Constructors

        /// <summary>
        /// Initializes a new instance of the <see cref="FaceDetectionPage" /> class
        /// </summary>
        public FaceDetectionPage()
        {
            InitializeComponent();
        }

        #endregion Constructors

        #region Events

        /// <summary>
        /// Implement INotifyPropertyChanged event handler
        /// </summary>
        public event PropertyChangedEventHandler PropertyChanged;

        #endregion Events

        #region Properties

        /// <summary>
        /// Gets or sets description
        /// </summary>
        public string Description
        {
            get
            {
                return (string)GetValue(DescriptionProperty);
            }

            set
            {
                SetValue(DescriptionProperty, value);
            }
        }

        /// <summary>
        /// Gets face detection results
        /// </summary>
        public ObservableCollection<Face> DetectedFaces
        {
            get
            {
                return _detectedFaces;
            }
        }

        /// <summary>
        /// Gets or sets face detection results in text string
        /// </summary>
        public string DetectedResultsInText
        {
            get
            {
                return _detectedResultsInText;
            }

            set
            {
                _detectedResultsInText = value;
                if (PropertyChanged != null)
                {
                    PropertyChanged(this, new PropertyChangedEventArgs("DetectedResultsInText"));
                }
            }
        }

        /// <summary>
        /// Gets constant maximum image size for rendering detection result
        /// </summary>
        public int MaxImageSize
        {
            get
            {
                return 300;
            }
        }

        /// <summary>
        /// Gets face detection results
        /// </summary>
        public ObservableCollection<Face> ResultCollection
        {
            get
            {
                return _resultCollection;
            }
        }

        /// <summary>
        /// Gets or sets image for rendering and detecting
        /// </summary>
        public ImageSource SelectedFile
        {
            get
            {
                return _selectedFile;
            }

            set
            {
                _selectedFile = value;
                if (PropertyChanged != null)
                {
                    PropertyChanged(this, new PropertyChangedEventArgs("SelectedFile"));
                }
            }
        }

        /// <summary>
        /// Sets whether to draw face rectangles rotated by head poses.
        /// </summary>
        public bool DrawHeadPose
        {
            set
            {
                _drawHeadPose = value;

                // Update face rectangles.
                if (_drawHeadPose)
                {
                    for (int i = 0; i < ResultCollection.Count; i++)
                    {
                        ResultCollection[i].FaceAngle = _resultCollectionWithHeadpose[i].FaceAngle;
                        ResultCollection[i].Left = _resultCollectionWithHeadpose[i].Left;
                        ResultCollection[i].Top = _resultCollectionWithHeadpose[i].Top;
                    }
                }
                else
                {
                    for (int i = 0; i < ResultCollection.Count; i++)
                    {
                        ResultCollection[i].FaceAngle = 0;
                        ResultCollection[i].Left = _resultCollectionWithHeadpose[i].OriginalLeft;
                        ResultCollection[i].Top = _resultCollectionWithHeadpose[i].OriginalTop;
                    }
                }

                if (PropertyChanged != null)
                {
                    PropertyChanged(this, new PropertyChangedEventArgs("DrawHeadPose"));
                }
            }
        }

        #endregion Properties

        #region Methods

        /// <summary>
        /// Pick image for face detection and set detection result to result container
        /// </summary>
        /// <param name="sender">Event sender</param>
        /// <param name="e">Event argument</param>
        private async void ImagePicker_Click(object sender, RoutedEventArgs e)
        {
            // Show file picker dialog
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.DefaultExt = ".jpg";
            dlg.Filter = "Image files (*.jpg, *.png, *.bmp, *.gif) | *.jpg; *.png; *.bmp; *.gif";
            var result = dlg.ShowDialog();

            if (result.HasValue && result.Value)
            {
                // User picked one image
                var pickedImagePath = dlg.FileName;
                var renderingImage = UIHelper.LoadImageAppliedOrientation(pickedImagePath);
                var imageInfo = UIHelper.GetImageInfoForRendering(renderingImage);
                SelectedFile = renderingImage;

                // Clear last detection result
                ResultCollection.Clear();
                _resultCollectionWithHeadpose.Clear();
                DetectedFaces.Clear();
                DetectedResultsInText = string.Format("Detecting...");

                MainWindow.Log("Request: Detecting {0}", pickedImagePath);
                var sw = Stopwatch.StartNew();

                // Call detection REST API
                using (var fStream = File.OpenRead(pickedImagePath))
                {
                    try
                    {
                        var faceServiceClient = FaceServiceClientHelper.GetInstance(this);
                        Response<IReadOnlyList<FaceDetectionResult>> response = await faceServiceClient.DetectAsync(
                            BinaryData.FromStream(fStream),
                            FaceDetectionModel.Detection01,
                            recognitionModel,
                            returnFaceId: true,
                            new FaceAttributeType[]
                            {
                                FaceAttributeType.Detection01.Accessories,
                                FaceAttributeType.Detection01.Blur,
                                FaceAttributeType.Detection01.Exposure,
                                FaceAttributeType.Detection01.Glasses,
                                FaceAttributeType.Detection01.HeadPose,
                                FaceAttributeType.Detection01.Noise,
                                FaceAttributeType.Detection01.Occlusion,
                                FaceAttributeType.Recognition04.QualityForRecognition,
                            }
                        );
                        IList<FaceDetectionResult> faces = response.Value.ToList();

                        MainWindow.Log("Response: Success. Detected {0} face(s) in {1}", faces.Count, pickedImagePath);

                        DetectedResultsInText = string.Format("{0} face(s) has been detected", faces.Count);

                        foreach (var face in faces)
                        {
                            DetectedFaces.Add(new Face()
                            {
                                ImageFile = renderingImage,
                                Left = face.FaceRectangle.Left,
                                Top = face.FaceRectangle.Top,
                                Width = face.FaceRectangle.Width,
                                Height = face.FaceRectangle.Height,
                                FaceId = face.FaceId?.ToString(),
                                HeadPose = string.Format("Pitch: {0}, Roll: {1}, Yaw: {2}", Math.Round(face.FaceAttributes.HeadPose.Pitch, 2), Math.Round(face.FaceAttributes.HeadPose.Roll, 2), Math.Round(face.FaceAttributes.HeadPose.Yaw, 2)),
                                Glasses = string.Format("GlassesType: {0}", face.FaceAttributes.Glasses.ToString()),
                                EyeOcclusion = string.Format("EyeOccluded: {0}", ((face.FaceAttributes.Occlusion.EyeOccluded) ? "Yes" : "No")),
                                ForeheadOcclusion = string.Format("ForeheadOccluded: {0}", (face.FaceAttributes.Occlusion.ForeheadOccluded ? "Yes" : "No")),
                                MouthOcclusion = string.Format("MouthOccluded: {0}", (face.FaceAttributes.Occlusion.MouthOccluded ? "Yes" : "No")),
                                Accessories = $"{GetAccessories(face.FaceAttributes.Accessories.ToList())}",
                                Blur = string.Format("Blur: {0}", face.FaceAttributes.Blur.BlurLevel.ToString()),
                                Exposure = string.Format("{0}", face.FaceAttributes.Exposure.ExposureLevel.ToString()),
                                Noise = string.Format("Noise: {0}", face.FaceAttributes.Noise.NoiseLevel.ToString()),
                                QualityForRecognition = string.Format("QualityForRecognition: {0}", face.FaceAttributes.QualityForRecognition.ToString()),
                            });
                        }

                        // Convert detection result into UI binding object for rendering
                        foreach (var face in UIHelper.CalculateFaceRectangleForRendering(faces, MaxImageSize, imageInfo))
                        {
                            _resultCollectionWithHeadpose.Add(
                                new Face()
                                {
                                    FaceAngle = face.FaceAngle,
                                    Left = face.Left,
                                    Top = face.Top,
                                    OriginalLeft = face.OriginalLeft,
                                    OriginalTop = face.OriginalTop
                                });

                            if (!_drawHeadPose)
                            {
                                face.FaceAngle = 0;
                                face.Top = face.OriginalTop;
                                face.Left = face.OriginalLeft;
                            }

                            ResultCollection.Add(face);
                        }
                    }
                    catch (RequestFailedException ex)
                    {
                        MainWindow.Log("Response: {0}. {1}", ex.ErrorCode, ex.Message);
                        GC.Collect();
                        return;
                    }
                    GC.Collect();
                }
            }
        }

        private string GetAccessories(IList<AccessoryItem> accessories)
        {
            if (accessories.Count == 0)
            {
                return "NoAccessories";
            }

            string[] accessoryArray = new string[accessories.Count];

            for (int i = 0; i < accessories.Count; ++i)
            {
                accessoryArray[i] = accessories[i].Type.ToString();
            }

            return "Accessories: " + String.Join(",", accessoryArray);
        }

        #endregion Methods
    }
}