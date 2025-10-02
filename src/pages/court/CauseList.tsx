import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Calendar, Download, FileText, Search, Loader2, Clock, AlertCircle } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { courtApi, CauseListEntry } from "@/lib/api";

const CauseList = () => {
  const [loading, setLoading] = useState(false);
  const [causeListData, setCauseListData] = useState<CauseListEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    courtType: "High Court of Delhi",
    date: new Date().toISOString().split('T')[0], // Today's date
    caseNumber: "",
  });

  // Load cause list on component mount
  useEffect(() => {
    handleSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = async () => {
    if (!formData.courtType || !formData.date) {
      toast({
        title: "Missing Information",
        description: "Please select court type and date.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const params = {
        court_name: formData.courtType,
        date: formData.date,
        limit: 50,
      };

      const data = await courtApi.getCauseList(params);
      setCauseListData(data);
      
      toast({
        title: "Cause List Retrieved",
        description: `Found ${data.length} cases for ${formData.date}`,
      });
    } catch (error: unknown) {
      console.error("Error fetching cause list:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to fetch cause list";
      setError(errorMessage);
      
      toast({
        title: "Fetch Failed",
        description: "Failed to fetch cause list. Please check if the backend server is running.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCauseList = () => {
    toast({
      title: "Download Started",
      description: "Downloading cause list as PDF...",
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Cause List</h1>
        <p className="text-muted-foreground">
          View daily cause lists and check case listings for specific dates
        </p>
      </div>

      {/* Search Form */}
      <Card className="shadow-card mb-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2 text-legal-gold" />
            Cause List Search
          </CardTitle>
          <CardDescription>
            Select court type and date to view the cause list
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="courtType">Court Type</Label>
              <Select
                value={formData.courtType}
                onValueChange={(value) => setFormData({ ...formData, courtType: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select court" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="high-court">High Court</SelectItem>
                  <SelectItem value="district-court">District Court</SelectItem>
                  <SelectItem value="session-court">Session Court</SelectItem>
                  <SelectItem value="magistrate-court">Magistrate Court</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="caseNumber">Case Number (Optional)</Label>
              <Input
                id="caseNumber"
                placeholder="Enter case number"
                value={formData.caseNumber}
                onChange={(e) => setFormData({ ...formData, caseNumber: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>&nbsp;</Label>
              <Button
                onClick={handleSearch}
                className="w-full"
                variant="legal-gold"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Get Cause List
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cause List Results */}
      {causeListData.length > 0 && (
        <Card className="shadow-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-teal" />
                  Cause List - {formData.date}
                </CardTitle>
                <CardDescription>
                  {formData.courtType.replace("-", " ").toUpperCase()} • {causeListData.length} cases listed
                </CardDescription>
              </div>
              <Button onClick={handleDownloadCauseList} variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Sr. No.</TableHead>
                    <TableHead>Case Number</TableHead>
                    <TableHead>Parties</TableHead>
                    <TableHead>Hearing</TableHead>
                    <TableHead className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      Time
                    </TableHead>
                    <TableHead>Court</TableHead>
                    <TableHead>Judge</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {causeListData.map((item, index) => {
                    const isHighlighted = formData.caseNumber && item.case_number.includes(formData.caseNumber);
                    return (
                      <TableRow 
                        key={item.id} 
                        className={isHighlighted ? "bg-legal-gold/10 border-legal-gold" : ""}
                      >
                        <TableCell className="font-medium">{index + 1}</TableCell>
                        <TableCell className="font-mono text-sm">
                          {isHighlighted && (
                            <div className="flex items-center">
                              <div className="w-2 h-2 bg-legal-gold rounded-full mr-2"></div>
                            </div>
                          )}
                          {item.case_number}
                        </TableCell>
                        <TableCell className="max-w-xs">
                          <div className="truncate" title={`${item.petitioner} vs ${item.respondent}`}>
                            {item.petitioner} vs {item.respondent}
                          </div>
                        </TableCell>
                        <TableCell>{item.case_title || 'Not available'}</TableCell>
                        <TableCell className="font-semibold text-warning">
                          {item.hearing_time || 'Not scheduled'}
                        </TableCell>
                        <TableCell>{item.courtroom || 'Not assigned'}</TableCell>
                        <TableCell className="text-sm">{item.judge_name || 'Not assigned'}</TableCell>
                        <TableCell>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${
                              item.case_status === "Listed"
                                ? "bg-success/10 text-success"
                                : "bg-warning/10 text-warning"
                            }`}
                          >
                            {item.case_status}
                          </span>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>

            {formData.caseNumber && causeListData.some(item => item.case_number.includes(formData.caseNumber)) && (
              <div className="mt-4 p-3 bg-legal-gold/10 border border-legal-gold rounded-lg">
                <div className="flex items-center text-legal-gold">
                  <Search className="h-4 w-4 mr-2" />
                  <span className="font-medium">Your searched case is highlighted above</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CauseList;