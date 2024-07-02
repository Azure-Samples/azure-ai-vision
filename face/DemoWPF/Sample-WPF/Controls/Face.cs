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

using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Media;

namespace Microsoft.ProjectOxford.Face.Controls
{
    /// <summary>
    /// Face view model
    /// </summary>
    public class Face : INotifyPropertyChanged
    {
        #region Fields

        /// <summary>
        /// confidence value of this face to a target face
        /// </summary>
        private double _confidence;

        /// <summary>
        /// Person name
        /// </summary>
        private string _personName;

        /// <summary>
        /// Face height in pixel
        /// </summary>
        private int _height;

        /// <summary>
        /// Face position X relative to image left-top in pixel
        /// </summary>
        private int _left;

        /// <summary>
        /// Face position Y relative to image left-top in pixel
        /// </summary>
        private int _top;

        /// <summary>
        /// Face original position X relative to image left-top in pixel
        /// </summary>
        private int _originalLeft;

        /// <summary>
        /// Face original position Y relative to image left-top in pixel
        /// </summary>
        private int _originalTop;

        /// <summary>
        /// Face width in pixel
        /// </summary>
        private int _width;

        /// <summary>
        /// Face angle
        /// </summary>
        private double _faceAngle;

        /// <summary>
        /// Indicates the headPose
        /// </summary>
        private string _headPose;

        /// <summary>
        /// Indicates the glasses type
        /// </summary>
        private string _glasses;

        /// <summary>
        /// Indicates the eye occlusion
        /// </summary>
        private string _eyeOcclusion;

        /// <summary>
        /// Indicates the forehead occlusion
        /// </summary>
        private string _foreheadOcclusion;

        /// <summary>
        /// Indicates the mouth occlusion
        /// </summary>
        private string _mouthOcclusion;

        /// <summary>
        /// Indicates the accessories
        /// </summary>
        private string _accessories;

        /// <summary>
        /// Indicates the blur
        /// </summary>
        private string _blur;

        /// <summary>
        /// Indicates the exposure
        /// </summary>
        private string _exposure;

        /// <summary>
        /// Indicates the noise
        /// </summary>
        private string _noise;

        /// <summary>
        /// Indicates the quality for recognition
        /// </summary>
        private string _qualityForRecognition;

        #endregion Fields

        #region Events

        /// <summary>
        /// Implement INotifyPropertyChanged interface
        /// </summary>
        public event PropertyChangedEventHandler PropertyChanged;

        #endregion Events

        #region Properties

        /// <summary>
        /// Gets or sets confidence value
        /// </summary>
        public double Confidence
        {
            get
            {
                return _confidence;
            }

            set
            {
                _confidence = value;
                OnPropertyChanged<double>();
            }
        }

        /// <summary>
        /// Gets face rectangle on image
        /// </summary>
        public System.Windows.Int32Rect UIRect
        {
            get
            {
                return new System.Windows.Int32Rect(Left, Top, Width, Height);
            }
        }

        /// <summary>
        /// Gets or sets image path
        /// </summary>
        public ImageSource ImageFile
        {
            get;
            set;
        }

        /// <summary>
        /// Gets or sets face id
        /// </summary>
        public string FaceId
        {
            get;
            set;
        }

        /// <summary>
        /// Gets or sets person's name
        /// </summary>
        public string PersonName
        {
            get
            {
                return _personName;
            }

            set
            {
                _personName = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets face height
        /// </summary>
        public int Height
        {
            get
            {
                return _height;
            }

            set
            {
                _height = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets face position X
        /// </summary>
        public int Left
        {
            get
            {
                return _left;
            }

            set
            {
                _left = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets face position Y
        /// </summary>
        public int Top
        {
            get
            {
                return _top;
            }

            set
            {
                _top = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets face original position X
        /// </summary>
        public int OriginalLeft
        {
            get
            {
                return _originalLeft;
            }

            set
            {
                _originalLeft = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets face original position Y
        /// </summary>
        public int OriginalTop
        {
            get
            {
                return _originalTop;
            }

            set
            {
                _originalTop = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets face width
        /// </summary>
        public int Width
        {
            get
            {
                return _width;
            }

            set
            {
                _width = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets face angle
        /// </summary>
        public double FaceAngle
        {
            get
            {
                return _faceAngle;
            }

            set
            {
                _faceAngle = value;
                OnPropertyChanged<int>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the head pose value
        /// </summary>
        public string HeadPose
        {
            get { return _headPose; }
            set
            {
                _headPose = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the glasses type 
        /// </summary>
        public string Glasses
        {
            get
            {
                return _glasses;
            }

            set
            {
                _glasses = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the occlusion type of eye
        /// </summary>
        public string EyeOcclusion
        {
            get { return _eyeOcclusion; }
            set
            {
                _eyeOcclusion = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the occlusion type of forehead
        /// </summary>
        public string ForeheadOcclusion
        {
            get { return _foreheadOcclusion; }
            set
            {
                _foreheadOcclusion = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the occlusion type of mouth
        /// </summary>
        public string MouthOcclusion
        {
            get { return _mouthOcclusion; }
            set
            {
                _mouthOcclusion = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the accessories type
        /// </summary>
        public string Accessories
        {
            get { return _accessories; }
            set
            {
                _accessories = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the blur type
        /// </summary>
        public string Blur
        {
            get { return _blur; }
            set
            {
                _blur = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the exposure type
        /// </summary>
        public string Exposure
        {
            get { return _exposure; }
            set
            {
                _exposure = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the noise type
        /// </summary>
        public string Noise
        {
            get { return _noise; }
            set
            {
                _noise = value;
                OnPropertyChanged<string>();
            }
        }

        /// <summary>
        /// Gets or sets a value indicating the quality for recognition
        /// </summary>
        public string QualityForRecognition
        {
            get { return _qualityForRecognition; }
            set
            {
                _qualityForRecognition = value;
                OnPropertyChanged<string>();
            }
        }

        #endregion Properties

        #region Methods

        /// <summary>
        /// NotifyProperty Helper functions
        /// </summary>
        /// <typeparam name="T">property type</typeparam>
        /// <param name="caller">property change caller</param>
        private void OnPropertyChanged<T>([CallerMemberName]string caller = null)
        {
            var handler = PropertyChanged;
            if (handler != null)
            {
                handler(this, new PropertyChangedEventArgs(caller));
            }
        }

        #endregion Methods
    }
}