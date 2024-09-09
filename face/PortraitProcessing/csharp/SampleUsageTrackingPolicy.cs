using Azure.Core;
using Azure.Core.Pipeline;

namespace PortraitProcessing
{
    internal class SampleUsageTrackingPolicy : HttpPipelineSynchronousPolicy
    {
        public override void OnSendingRequest(HttpMessage message)
        {
            message.Request.Headers.Add("X-MS-AZSDK-Telemetry", "sample=portrait-processing");
        }
    }
}
