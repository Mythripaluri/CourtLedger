import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, Search, Trash2, RefreshCw } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";

interface RecentSearch {
  id: number;
  caseType: string;
  caseNumber: string;
  year: string;
  searchDate: string;
}

const RecentSearches = () => {
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem("recentSearches");
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  const handleRerun = (search: RecentSearch) => {
    toast({
      title: "Re-running Search",
      description: `Searching for ${search.caseType} ${search.caseNumber}/${search.year}`,
    });
    
    // Navigate back to search with pre-filled data
    navigate("/court/search", { 
      state: { 
        caseType: search.caseType, 
        caseNumber: search.caseNumber, 
        year: search.year 
      } 
    });
  };

  const handleDelete = (id: number) => {
    const updated = recentSearches.filter(search => search.id !== id);
    setRecentSearches(updated);
    localStorage.setItem("recentSearches", JSON.stringify(updated));
    
    toast({
      title: "Search Deleted",
      description: "Recent search has been removed from history.",
    });
  };

  const handleClearAll = () => {
    setRecentSearches([]);
    localStorage.removeItem("recentSearches");
    
    toast({
      title: "History Cleared",
      description: "All recent searches have been cleared.",
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getCaseTypeLabel = (caseType: string) => {
    const types: Record<string, string> = {
      CS: "Civil Suit",
      CRL: "Criminal",
      WP: "Writ Petition",
      CC: "Contempt Case",
      MA: "Miscellaneous Application",
      PIL: "Public Interest Litigation",
    };
    return types[caseType] || caseType;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Recent Searches</h1>
            <p className="text-muted-foreground">
              View and re-run your previously searched cases
            </p>
          </div>
          {recentSearches.length > 0 && (
            <Button onClick={handleClearAll} variant="destructive" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </Button>
          )}
        </div>
      </div>

      {recentSearches.length === 0 ? (
        <Card className="shadow-card">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="bg-muted/50 p-6 rounded-full mb-4">
              <Clock className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No Recent Searches</h3>
            <p className="text-muted-foreground text-center mb-6 max-w-md">
              Your recent case searches will appear here. Start by searching for a case to build your history.
            </p>
            <Button onClick={() => navigate("/court/search")} variant="legal-gold">
              <Search className="h-4 w-4 mr-2" />
              Search Cases
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {recentSearches.map((search) => (
            <Card key={search.id} className="shadow-card hover:shadow-legal transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="bg-legal-gold/10 p-3 rounded-lg">
                      <Search className="h-6 w-6 text-legal-gold" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge variant="secondary" className="font-mono">
                          {search.caseType} {search.caseNumber}/{search.year}
                        </Badge>
                        <Badge variant="outline">
                          {getCaseTypeLabel(search.caseType)}
                        </Badge>
                      </div>
                      <div className="flex items-center text-sm text-muted-foreground">
                        <Clock className="h-4 w-4 mr-1" />
                        Searched on {formatDate(search.searchDate)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={() => handleRerun(search)}
                      variant="outline"
                      size="sm"
                    >
                      <RefreshCw className="h-4 w-4 mr-1" />
                      Re-run
                    </Button>
                    <Button
                      onClick={() => handleDelete(search.id)}
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="mt-8">
        <Card className="shadow-card bg-muted/30">
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
            <CardDescription>
              Manage your search history and preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button onClick={() => navigate("/court/search")} variant="legal-gold">
              <Search className="h-4 w-4 mr-2" />
              New Search
            </Button>
            <Button onClick={() => navigate("/court/cause-list")} variant="outline">
              View Cause List
            </Button>
            <Button onClick={() => navigate("/court/integrations")} variant="outline">
              Integrations
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RecentSearches;