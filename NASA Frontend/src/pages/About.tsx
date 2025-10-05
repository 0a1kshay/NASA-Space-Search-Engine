import { Card, CardContent } from "@/components/ui/card";
import { Rocket, Target, Users, Globe, Lightbulb, Award } from "lucide-react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const About = () => {
  const values = [
    {
      icon: Target,
      title: "Mission",
      description: "To advance the understanding of biological systems in space environments and support the future of human space exploration.",
    },
    {
      icon: Lightbulb,
      title: "Innovation",
      description: "Pioneering new research methods and technologies to study life beyond Earth's atmosphere.",
    },
    {
      icon: Users,
      title: "Collaboration",
      description: "Fostering international partnerships and open science to accelerate discovery.",
    },
    {
      icon: Globe,
      title: "Impact",
      description: "Translating space biology research into applications that benefit life on Earth.",
    },
  ];

  const achievements = [
    { year: "1961", event: "First organism in space - yeast cells aboard Vostok" },
    { year: "1973", event: "Skylab biology experiments begin" },
    { year: "1998", event: "ISS Space Biology program launches" },
    { year: "2012", event: "First plant grown from seed to seed in space" },
    { year: "2020", event: "10,000th space biology publication milestone" },
    { year: "2024", event: "Advanced lunar biology research program established" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />

      <main className="flex-1">
        {/* Hero */}
        <div className="bg-gradient-space py-20">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-6">
              About NASA Space Biology
            </h1>
            <p className="text-xl text-primary-foreground/90 max-w-3xl mx-auto">
              Pioneering the study of life in space for over six decades
            </p>
          </div>
        </div>

        {/* Introduction */}
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto space-y-6 text-lg">
            <p>
              The NASA Space Biology Knowledge Engine serves as the comprehensive repository for all 
              space biology research conducted by NASA and its international partners. Our platform 
              aggregates mission data, experimental results, publications, and visualizations to 
              support researchers, educators, and the public in understanding how life functions 
              beyond Earth.
            </p>
            <p>
              Since the earliest days of spaceflight, understanding how living systems respond to 
              the space environment has been critical to enabling long-duration human missions. 
              Space biology research has led to breakthrough discoveries in cellular biology, 
              genetics, plant science, and human physiology.
            </p>
            <p>
              Our knowledge engine represents decades of collaborative research, bringing together 
              data from missions to low Earth orbit, lunar expeditions, and preparations for Mars 
              exploration. We're committed to making this wealth of knowledge accessible and 
              actionable for the global scientific community.
            </p>
          </div>
        </div>

        {/* Values */}
        <div className="bg-muted/30 py-16">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">Our Values</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((value, index) => (
                <Card key={index} className="hover-lift">
                  <CardContent className="p-6 text-center">
                    <div className="bg-accent/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                      <value.icon className="h-8 w-8 text-accent" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                    <p className="text-muted-foreground">{value.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="container mx-auto px-4 py-16">
          <h2 className="text-3xl font-bold text-center mb-12">Key Milestones</h2>
          <div className="max-w-3xl mx-auto space-y-6">
            {achievements.map((achievement, index) => (
              <div key={index} className="flex gap-6 items-start group">
                <div className="flex flex-col items-center">
                  <div className="bg-accent text-accent-foreground w-20 h-20 rounded-full flex items-center justify-center font-bold group-hover:shadow-accent-glow transition-all">
                    {achievement.year}
                  </div>
                  {index < achievements.length - 1 && (
                    <div className="w-0.5 h-16 bg-border my-2"></div>
                  )}
                </div>
                <Card className="flex-1 hover-lift">
                  <CardContent className="p-4">
                    <p className="text-lg">{achievement.event}</p>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="bg-gradient-cosmic py-16">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-primary-foreground text-center mb-12">
              By the Numbers
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-accent mb-2">60+</div>
                <div className="text-primary-foreground">Years of Research</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-accent mb-2">150+</div>
                <div className="text-primary-foreground">Missions</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-accent mb-2">2,500+</div>
                <div className="text-primary-foreground">Experiments</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-accent mb-2">50+</div>
                <div className="text-primary-foreground">Countries</div>
              </div>
            </div>
          </div>
        </div>

        {/* Research Areas */}
        <div className="container mx-auto px-4 py-16">
          <h2 className="text-3xl font-bold text-center mb-12">Research Focus Areas</h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <Card className="hover-lift">
              <CardContent className="p-6">
                <Award className="h-10 w-10 text-accent mb-4" />
                <h3 className="text-xl font-semibold mb-2">Cellular Biology</h3>
                <p className="text-muted-foreground">
                  Understanding how cells and tissues respond to microgravity and radiation
                </p>
              </CardContent>
            </Card>
            <Card className="hover-lift">
              <CardContent className="p-6">
                <Award className="h-10 w-10 text-tech mb-4" />
                <h3 className="text-xl font-semibold mb-2">Plant Science</h3>
                <p className="text-muted-foreground">
                  Developing sustainable food systems for long-duration space missions
                </p>
              </CardContent>
            </Card>
            <Card className="hover-lift">
              <CardContent className="p-6">
                <Award className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-semibold mb-2">Human Physiology</h3>
                <p className="text-muted-foreground">
                  Studying adaptations and countermeasures for human spaceflight
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default About;
