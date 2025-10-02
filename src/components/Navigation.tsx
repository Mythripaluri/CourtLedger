import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Scale, HardDrive, Home, Menu } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const navItems = [
    { href: "/", icon: Home, label: "Home" },
    { href: "/court", icon: Scale, label: "Court Tracker" },
  ];

  return (
    <nav className="bg-gradient-hero shadow-nav border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Title */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="bg-legal-gold p-2 rounded-lg">
              <Scale className="h-6 w-6 text-legal-gold-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-primary-foreground">
                Court Case & Drive Assistant
              </h1>
              <p className="text-xs text-primary-foreground/70 hidden sm:block">
                Professional Legal Management System
              </p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link key={item.href} to={item.href}>
                  <Button
                    variant={isActive(item.href) ? "legal-gold" : "ghost"}
                    size="sm"
                    className={cn(
                      "text-primary-foreground hover:text-legal-gold-foreground",
                      isActive(item.href) && "text-legal-gold-foreground"
                    )}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.label}
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden text-primary-foreground"
            onClick={() => setIsOpen(!isOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden pb-4">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.href} to={item.href} onClick={() => setIsOpen(false)}>
                    <Button
                      variant={isActive(item.href) ? "legal-gold" : "ghost"}
                      size="sm"
                      className={cn(
                        "w-full justify-start text-primary-foreground hover:text-legal-gold-foreground",
                        isActive(item.href) && "text-legal-gold-foreground"
                      )}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.label}
                    </Button>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;