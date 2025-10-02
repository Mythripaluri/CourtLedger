import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Download, FileText, Calendar, Users, Gavel, Loader2, AlertCircle } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { courtApi, CaseQuery } from "@/lib/api";

const CourtSearch = () => {
  const [loading, setLoading] = useState(false);
  const [caseDetails, setCaseDetails] = useState<CaseQuery | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    caseType: "",
    caseNumber: "",
    year: "",
    courtName: "High Court of Delhi", // Default court
  });

  const handleSearch = async () => {
    if (!formData.caseType || !formData.caseNumber || !formData.year) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields to search for a case.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // Construct case number in the format expected by backend
      const fullCaseNumber = `${formData.caseType} ${formData.caseNumber}/${formData.year}`;
      
      // First try to get existing case details
      try {
        const existingCase = await courtApi.getCaseDetails(fullCaseNumber);
        setCaseDetails(existingCase);
        
        toast({
          title: "Case Found",
          description: "Case details retrieved successfully from database.",
        });
      } catch (getCaseError) {
        // If case doesn't exist, submit a new query to scrape it
        console.log("Case not found in database, submitting new query...");
        
        const newCase = await courtApi.submitCaseQuery({
          case_number: fullCaseNumber,
          court_name: formData.courtName,
        });
        
        setCaseDetails(newCase);
        
        toast({
          title: "Case Query Submitted",
          description: "New case query has been submitted. Details will be updated when available.",
        });
      }
      
      // Save to recent searches
      const recentSearches = JSON.parse(localStorage.getItem("recentSearches") || "[]");
      const newSearch = {
        id: Date.now(),
        ...formData,
        searchDate: new Date().toISOString(),
      };
      recentSearches.unshift(newSearch);
      localStorage.setItem("recentSearches", JSON.stringify(recentSearches.slice(0, 10)));
      
    } catch (error: any) {
      console.error("Error searching case:", error);
      setError(error.response?.data?.detail || error.message || "Failed to search case");
      
      toast({
        title: "Search Failed",
        description: error.response?.data?.detail || "Failed to search for case. Please check if the backend server is running.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (type: string) => {
    toast({
      title: "Download Started",
      description: `Downloading ${type}...`,
    });
    // Simulate download
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Search Court Cases</h1>
        <p className="text-muted-foreground">
          Enter case details to fetch information from court records
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Search Form */}
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Search className="h-5 w-5 mr-2 text-legal-gold" />
              Case Search
            </CardTitle>
            <CardDescription>
              Enter the case details to search court records
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="caseType">Case Type</Label>
              <Select
                value={formData.caseType}
                onValueChange={(value) => setFormData({ ...formData, caseType: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select case type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CS">Civil Suit (CS)</SelectItem>
                  <SelectItem value="CRL">Criminal (CRL)</SelectItem>
                  <SelectItem value="WP">Writ Petition (WP)</SelectItem>
                  <SelectItem value="CC">Contempt Case (CC)</SelectItem>
                  <SelectItem value="MA">Miscellaneous Application (MA)</SelectItem>
                  <SelectItem value="PIL">Public Interest Litigation (PIL)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="caseNumber">Case Number</Label>
              <Input
                id="caseNumber"
                placeholder="Enter case number (e.g., 12345)"
                value={formData.caseNumber}
                onChange={(e) => setFormData({ ...formData, caseNumber: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="year">Year</Label>
              <Select
                value={formData.year}
                onValueChange={(value) => setFormData({ ...formData, year: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select year" />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 10 }, (_, i) => {
                    const year = new Date().getFullYear() - i;
                    return (
                      <SelectItem key={year} value={year.toString()}>
                        {year}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="courtName">Court Name</Label>
              <Select
                value={formData.courtName}
                onValueChange={(value) => setFormData({ ...formData, courtName: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select court" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="High Court of Delhi">High Court of Delhi</SelectItem>
                  <SelectItem value="Supreme Court of India">Supreme Court of India</SelectItem>
                  <SelectItem value="District Court Delhi">District Court Delhi</SelectItem>
                  <SelectItem value="High Court of Bombay">High Court of Bombay</SelectItem>
                  <SelectItem value="High Court of Madras">High Court of Madras</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleSearch}
              className="w-full"
              variant="legal-gold"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Fetch Case Details
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="shadow-card border-destructive">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <div>
                  <p className="font-semibold">Search Error</p>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Case Details */}
        {caseDetails && (
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-teal" />
                Case Details
              </CardTitle>
              <CardDescription>
                {caseDetails.case_number} - {caseDetails.court_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Case Title</Label>
                  <p className="font-semibold">{caseDetails.case_title || 'Not available'}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Case Type</Label>
                  <p className="font-semibold">{caseDetails.case_type || 'Not available'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Petitioner</Label>
                  <p className="font-semibold">{caseDetails.petitioner || 'Not available'}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Respondent</Label>
                  <p className="font-semibold">{caseDetails.respondent || 'Not available'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Filing Date</Label>
                    <p className="font-semibold">
                      {caseDetails.filing_date ? new Date(caseDetails.filing_date).toLocaleDateString() : 'Not available'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Next Hearing</Label>
                    <p className="font-semibold text-warning">
                      {caseDetails.next_hearing_date ? new Date(caseDetails.next_hearing_date).toLocaleDateString() : 'Not scheduled'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Gavel className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Status</Label>
                    <p className="font-semibold text-warning">{caseDetails.case_status || 'Not available'}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Judge</Label>
                    <p className="font-semibold">{caseDetails.judge_name || 'Not assigned'}</p>
                  </div>
                </div>
              </div>

              <div className="pt-4 space-y-2">
                <Button
                  onClick={() => handleDownload("Judgment PDF")}
                  className="w-full"
                  variant="outline"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download Judgment PDF
                </Button>
                <Button
                  onClick={() => handleDownload("Cause List PDF")}
                  className="w-full"
                  variant="outline"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download Cause List PDF
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CourtSearch;