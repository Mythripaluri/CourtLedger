import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { 
  FileText, 
  Calendar, 
  Workflow, 
  CheckCircle, 
  XCircle, 
  Settings, 
  ExternalLink,
  Loader2,
  Cloud
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

const Integrations = () => {
  const [integrations, setIntegrations] = useState({
    googleDrive: { connected: false, loading: false },
    googleCalendar: { connected: false, loading: false },
    n8n: { connected: false, loading: false },
  });

  const handleConnect = async (service: keyof typeof integrations) => {
    setIntegrations(prev => ({
      ...prev,
      [service]: { ...prev[service], loading: true }
    }));

    // Simulate connection process
    setTimeout(() => {
      setIntegrations(prev => ({
        ...prev,
        [service]: { connected: !prev[service].connected, loading: false }
      }));

      const action = integrations[service].connected ? "disconnected from" : "connected to";
      toast({
        title: `Integration ${action.split(" ")[0]}`,
        description: `Successfully ${action} ${service.replace(/([A-Z])/g, ' $1').toLowerCase()}.`,
      });
    }, 2000);
  };

  const getIntegrationDetails = (service: string) => {
    switch (service) {
      case 'googleDrive':
        return {
          name: 'Google Drive',
          description: 'Sync case documents and judgments to your Google Drive',
          icon: FileText,
          benefits: [
            'Automatic document backup',
            'Organized folder structure',
            'Access from anywhere',
            'Version control'
          ],
          color: 'text-blue-600'
        };
      case 'googleCalendar':
        return {
          name: 'Google Calendar',
          description: 'Add hearing dates and case deadlines to your calendar',
          icon: Calendar,
          benefits: [
            'Automatic hearing reminders',
            'Deadline notifications',
            'Calendar sync across devices',
            'Meeting scheduling'
          ],
          color: 'text-green-600'
        };
      case 'n8n':
        return {
          name: 'n8n Workflow',
          description: 'Create automated workflows for case management',
          icon: Workflow,
          benefits: [
            'Custom automation workflows',
            'Email notifications',
            'Data processing',
            'Third-party integrations'
          ],
          color: 'text-purple-600'
        };
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Integrations</h1>
        <p className="text-muted-foreground">
          Connect external services to enhance your court case management workflow
        </p>
      </div>

      <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {Object.entries(integrations).map(([service, status]) => {
          const details = getIntegrationDetails(service);
          if (!details) return null;

          const Icon = details.icon;

          return (
            <Card key={service} className="shadow-card hover:shadow-legal transition-all duration-300">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg bg-muted/50`}>
                      <Icon className={`h-6 w-6 ${details.color}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{details.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {details.description}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge 
                    variant={status.connected ? "default" : "secondary"}
                    className={status.connected ? "bg-success text-success-foreground" : ""}
                  >
                    {status.connected ? (
                      <CheckCircle className="h-3 w-3 mr-1" />
                    ) : (
                      <XCircle className="h-3 w-3 mr-1" />
                    )}
                    {status.connected ? "Connected" : "Not Connected"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2 text-sm">Benefits:</h4>
                    <ul className="space-y-1">
                      {details.benefits.map((benefit, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start">
                          <span className="w-1 h-1 bg-legal-gold rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="pt-2 border-t">
                    <Button
                      onClick={() => handleConnect(service as keyof typeof integrations)}
                      className="w-full"
                      variant={status.connected ? "destructive" : "legal-gold"}
                      disabled={status.loading}
                    >
                      {status.loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          {status.connected ? "Disconnecting..." : "Connecting..."}
                        </>
                      ) : (
                        <>
                          {status.connected ? "Disconnect" : "Connect"}
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Integration Settings */}
      <Card className="shadow-card mb-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2 text-legal-gold" />
            Integration Settings
          </CardTitle>
          <CardDescription>
            Configure how integrations work with your court case data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="auto-sync" className="font-medium">Auto-sync Documents</Label>
              <p className="text-sm text-muted-foreground">
                Automatically sync downloaded documents to connected cloud services
              </p>
            </div>
            <Switch id="auto-sync" />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="calendar-reminders" className="font-medium">Calendar Reminders</Label>
              <p className="text-sm text-muted-foreground">
                Send calendar notifications 24 hours before hearings
              </p>
            </div>
            <Switch id="calendar-reminders" defaultChecked />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="workflow-automation" className="font-medium">Workflow Automation</Label>
              <p className="text-sm text-muted-foreground">
                Enable automated workflows for case status updates
              </p>
            </div>
            <Switch id="workflow-automation" />
          </div>
        </CardContent>
      </Card>

      {/* Available Integrations */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Cloud className="h-5 w-5 mr-2 text-teal" />
            More Integrations
          </CardTitle>
          <CardDescription>
            Additional services that can be integrated with your workflow
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              {
                name: "Microsoft Outlook",
                description: "Sync with Outlook Calendar and OneDrive",
                status: "Coming Soon"
              },
              {
                name: "Slack",
                description: "Get case updates in your Slack workspace",
                status: "Coming Soon"
              },
              {
                name: "Telegram Bot",
                description: "Receive case notifications via Telegram",
                status: "Coming Soon"
              },
              {
                name: "WhatsApp Business",
                description: "Send case updates via WhatsApp",
                status: "Available"
              }
            ].map((integration, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">{integration.name}</h4>
                  <p className="text-sm text-muted-foreground">{integration.description}</p>
                </div>
                <Badge 
                  variant={integration.status === "Available" ? "default" : "secondary"}
                  className={integration.status === "Available" ? "bg-success text-success-foreground" : ""}
                >
                  {integration.status}
                </Badge>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-muted/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <ExternalLink className="h-5 w-5 text-legal-gold mt-0.5" />
              <div>
                <h4 className="font-medium">Need Custom Integration?</h4>
                <p className="text-sm text-muted-foreground mt-1">
                  Contact our support team to discuss custom integrations for your specific workflow needs.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Integrations;