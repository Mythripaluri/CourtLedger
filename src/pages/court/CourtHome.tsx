import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Scale, Search, FileText, Clock, Settings, Calendar, Users, Gavel } from "lucide-react";

const CourtHome = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="bg-gradient-hero p-8 rounded-2xl shadow-legal mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-legal-gold p-4 rounded-full">
              <Scale className="h-12 w-12 text-legal-gold-foreground" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            Court Case & Cause List Tracker
          </h1>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
            Professional legal management system for tracking court cases, cause lists, and legal documents.
          </p>
        </div>
      </div>

      {/* Main Features Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-6 mb-12">
        {/* Search Cases */}
        <Link to="/court/search">
          <Card className="shadow-card hover:shadow-legal transition-all duration-300 h-full border-0 bg-gradient-card">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-3 mb-2">
                <div className="bg-legal-gold/10 p-3 rounded-lg">
                  <Search className="h-8 w-8 text-legal-gold" />
                </div>
                <div>
                  <CardTitle className="text-xl">Search Court Cases</CardTitle>
                  <CardDescription>
                    Find case details, parties, and hearing dates
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mb-4">
                <div className="flex items-center space-x-2 text-sm">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <span>Parties information</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>Filing & hearing dates</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Gavel className="h-4 w-4 text-muted-foreground" />
                  <span>Case status & proceedings</span>
                </div>
              </div>
              <Button variant="legal-gold" className="w-full">
                Search Cases
              </Button>
            </CardContent>
          </Card>
        </Link>

        {/* Cause List */}
        <Link to="/court/cause-list">
          <Card className="shadow-card hover:shadow-legal transition-all duration-300 h-full border-0 bg-gradient-card">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-3 mb-2">
                <div className="bg-teal/10 p-3 rounded-lg">
                  <FileText className="h-8 w-8 text-teal" />
                </div>
                <div>
                  <CardTitle className="text-xl">Daily Cause List</CardTitle>
                  <CardDescription>
                    View court schedules and case listings
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mb-4">
                <div className="flex items-center space-x-2 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>Date-wise listings</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Hearing schedules</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Search className="h-4 w-4 text-muted-foreground" />
                  <span>Find your cases</span>
                </div>
              </div>
              <Button variant="teal" className="w-full">
                View Cause List
              </Button>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Secondary Features */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {/* Recent Searches */}
        <Link to="/court/recent">
          <Card className="shadow-card hover:shadow-legal transition-all duration-300 border-0 bg-gradient-card">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Clock className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>Recent Searches</CardTitle>
                  <CardDescription>
                    Access your search history and re-run queries
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                View Search History
              </Button>
            </CardContent>
          </Card>
        </Link>

        {/* Integrations */}
        <Link to="/court/integrations">
          <Card className="shadow-card hover:shadow-legal transition-all duration-300 border-0 bg-gradient-card">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-success/10 p-3 rounded-lg">
                  <Settings className="h-6 w-6 text-success" />
                </div>
                <div>
                  <CardTitle>Integrations</CardTitle>
                  <CardDescription>
                    Connect with Google Drive, Calendar, and automation tools
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                Manage Integrations
              </Button>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Features Overview */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="text-center text-2xl mb-2">Court Case Tracker Features</CardTitle>
          <CardDescription className="text-center text-base">
            Comprehensive legal case management at your fingertips
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-legal-gold/10 p-3 rounded-lg inline-block mb-3">
                <Search className="h-6 w-6 text-legal-gold" />
              </div>
              <h3 className="font-semibold mb-2">Case Search</h3>
              <p className="text-sm text-muted-foreground">
                Find cases by number, type, year, and parties involved
              </p>
            </div>
            <div className="text-center">
              <div className="bg-teal/10 p-3 rounded-lg inline-block mb-3">
                <FileText className="h-6 w-6 text-teal" />
              </div>
              <h3 className="font-semibold mb-2">Document Access</h3>
              <p className="text-sm text-muted-foreground">
                Download judgments, orders, and cause list PDFs
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary/10 p-3 rounded-lg inline-block mb-3">
                <Calendar className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Schedule Tracking</h3>
              <p className="text-sm text-muted-foreground">
                Monitor hearing dates and court schedules
              </p>
            </div>
            <div className="text-center">
              <div className="bg-success/10 p-3 rounded-lg inline-block mb-3">
                <Settings className="h-6 w-6 text-success" />
              </div>
              <h3 className="font-semibold mb-2">Automation</h3>
              <p className="text-sm text-muted-foreground">
                Integrate with calendar and cloud storage services
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CourtHome;