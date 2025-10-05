import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Search, Rocket, Database, FlaskConical, ArrowRight } from "lucide-react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import heroImage from "@/assets/hero-space-biology.jpg";

const Home = () => {
  const stats = [
    { icon: Database, value: "50TB+", label: "Data Archived" },
    { icon: FlaskConical, value: "2,500+", label: "Experiments" },
    { icon: Search, value: "10,000+", label: "Research Papers" },
    { icon: Rocket, value: "Active", label: "Research Programs" },
  ];

  return (
    <div className="min-h-screen">
      <Navigation />

      {/* Hero Section */}
      <section className="relative overflow-hidden min-h-screen flex items-center">
        {/* Single Beautiful Space Background */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(https://images.unsplash.com/photo-1446776877081-d282a0f896e2?q=80&w=2072&auto=format&fit=crop)`,
          }}
        />
        
        {/* Gradient overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/50 to-black/30" />
        
        <div className="relative container mx-auto px-4 py-24 md:py-32">
          <div className="max-w-4xl mx-auto text-center space-y-8 animate-fade-in">
            <h1 className="text-4xl md:text-6xl font-bold text-primary-foreground leading-tight">
              NASA Space Biology
              <span className="block text-accent mt-2">Knowledge Engine</span>
            </h1>
            <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
              Explore decades of space biology research and discoveries. 
              Unlock insights into how life adapts beyond Earth.
            </p>

            {/* Call to Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-lg mx-auto">
              <Link to="/search" className="flex-1">
                <Button size="lg" className="w-full h-12 shadow-accent-glow">
                  <Search className="mr-2 h-5 w-5" />
                  Start Exploring
                </Button>
              </Link>
              <Link to="/about" className="flex-1">
                <Button variant="outline" size="lg" className="w-full h-12 bg-card/50 backdrop-blur border-accent/30 hover:bg-accent/10">
                  <Rocket className="mr-2 h-5 w-5" />
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <Card key={index} className="hover-lift">
                <CardContent className="p-6 text-center">
                  <stat.icon className="h-10 w-10 mx-auto mb-3 text-accent" />
                  <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Connection Status Section */}
      <section className="py-16 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">System Status</h2>
            <p className="text-lg text-muted-foreground">
              Real-time connection status to NASA's research database
            </p>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20 bg-gradient-cosmic">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center text-primary-foreground space-y-6">
            <h2 className="text-3xl md:text-4xl font-bold">
              About NASA Space Biology Knowledge Engine
            </h2>
            <p className="text-lg opacity-90">
              The NASA Space Biology Knowledge Engine is a comprehensive resource for researchers, 
              educators, and space enthusiasts. Our platform aggregates decades of space biology 
              research, providing easy access to mission data, experimental results, and scientific 
              publications.
            </p>
            <p className="text-lg opacity-90">
              From understanding how microorganisms survive in space to developing sustainable 
              life support systems for long-duration missions, our database supports the future 
              of human space exploration.
            </p>
            <Link to="/about">
              <Button size="lg" variant="secondary" className="mt-4">
                Learn More About Us <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Home;
