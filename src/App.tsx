import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navigation from "./components/Navigation";

// Court-related pages only
import Home from "./pages/Home";
import CourtHome from "./pages/court/CourtHome";
import CourtSearch from "./pages/court/CourtSearch";
import CauseList from "./pages/court/CauseList";
import RecentSearches from "./pages/court/RecentSearches";
import Integrations from "./pages/court/Integrations";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            
            {/* Court Case Tracker Routes */}
            <Route path="/court" element={<CourtHome />} />
            <Route path="/court/search" element={<CourtSearch />} />
            <Route path="/court/cause-list" element={<CauseList />} />
            <Route path="/court/recent" element={<RecentSearches />} />
            <Route path="/court/integrations" element={<Integrations />} />
            
            {/* Catch-all route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
