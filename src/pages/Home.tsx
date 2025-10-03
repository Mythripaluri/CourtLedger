import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Scale, HardDrive, Search, FileText, Clock, Settings, MessageSquare, FolderOpen } from "lucide-react";

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="bg-gradient-hero p-8 rounded-2xl shadow-legal mb-8 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-600/10"></div>
            <div className="relative z-10">
              <div className="flex justify-center mb-6">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-2xl">
                  <img 
                    src="/logo.png" 
                    alt="CourtLedger Logo" 
                    className="h-16 w-16 object-contain filter brightness-0 invert"
                  />
                </div>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
                CourtLedger
              </h1>
              <p className="text-2xl text-primary-foreground/80 mb-2">
                Infinite Legal Solutions
              </p>
              <p className="text-lg text-primary-foreground/70 max-w-2xl mx-auto">
                Professional legal management system for tracking court cases and managing documents efficiently
              </p>
            </div>
          </div>
        </div>

        {/* Main Modules */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Court Case Tracker Module */}
          <Card className="bg-gradient-card shadow-card hover:shadow-legal transition-all duration-300 border-0">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-3 mb-2">
                <div className="bg-legal-gold p-3 rounded-lg">
                  <Scale className="h-8 w-8 text-legal-gold-foreground" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Court Case & Cause List Tracker</CardTitle>
                  <CardDescription className="text-base">
                    Search cases, download judgments, and track cause lists
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Link to="/court/search">
                  <Button variant="outline" className="w-full h-auto py-3 flex-col space-y-2">
                    <Search className="h-5 w-5" />
                    <span className="text-sm">Search Cases</span>
                  </Button>
                </Link>
                <Link to="/court/cause-list">
                  <Button variant="outline" className="w-full h-auto py-3 flex-col space-y-2">
                    <FileText className="h-5 w-5" />
                    <span className="text-sm">Cause List</span>
                  </Button>
                </Link>
                <Link to="/court/recent">
                  <Button variant="outline" className="w-full h-auto py-3 flex-col space-y-2">
                    <Clock className="h-5 w-5" />
                    <span className="text-sm">Recent Searches</span>
                  </Button>
                </Link>
                <Link to="/court/integrations">
                  <Button variant="outline" className="w-full h-auto py-3 flex-col space-y-2">
                    <Settings className="h-5 w-5" />
                    <span className="text-sm">Integrations</span>
                  </Button>
                </Link>
              </div>
              <Link to="/court" className="block">
                <Button variant="legal-gold" className="w-full mt-4">
                  Access Court Tracker
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* WhatsApp Drive Assistant Module */}
          <Card className="bg-gradient-card shadow-card hover:shadow-legal transition-all duration-300 border-0">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-3 mb-2">
                <div className="bg-teal p-3 rounded-lg">
                  <HardDrive className="h-8 w-8 text-teal-foreground" />
                </div>
                <div>
                  <CardTitle className="text-2xl">WhatsApp Google Drive Assistant</CardTitle>
                  <CardDescription className="text-base">
                    Manage Google Drive files through WhatsApp commands
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Link to="/drive/commands">
                  <Button variant="outline" className="w-full h-auto py-3 flex-col space-y-2">
                    <MessageSquare className="h-5 w-5" />
                    <span className="text-sm">WhatsApp Commands</span>
                  </Button>
                </Link>
                <Link to="/drive/browser">
                  <Button variant="outline" className="w-full h-auto py-3 flex-col space-y-2">
                    <FolderOpen className="h-5 w-5" />
                    <span className="text-sm">File Browser</span>
                  </Button>
                </Link>
              </div>
              <Link to="/drive" className="block">
                <Button variant="teal" className="w-full mt-4">
                  Access Drive Assistant
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Feature Highlights */}
        <div className="bg-card rounded-xl p-6 shadow-card">
          <h2 className="text-2xl font-bold text-center mb-6">Key Features</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-legal-gold/10 p-4 rounded-lg inline-block mb-3">
                <Search className="h-8 w-8 text-legal-gold" />
              </div>
              <h3 className="font-semibold mb-2">Case Search & Tracking</h3>
              <p className="text-muted-foreground text-sm">
                Search court cases by type, number, and year. Track hearing dates and case status.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-teal/10 p-4 rounded-lg inline-block mb-3">
                <FileText className="h-8 w-8 text-teal" />
              </div>
              <h3 className="font-semibold mb-2">Document Management</h3>
              <p className="text-muted-foreground text-sm">
                Download judgments, cause lists, and manage documents through automated systems.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary/10 p-4 rounded-lg inline-block mb-3">
                <MessageSquare className="h-8 w-8 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">WhatsApp Integration</h3>
              <p className="text-muted-foreground text-sm">
                Manage Google Drive files directly through WhatsApp commands for ultimate convenience.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;