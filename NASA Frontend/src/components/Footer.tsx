import { Link } from "react-router-dom";
import { Rocket, Mail, Globe, Github } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-secondary text-secondary-foreground mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-gradient-accent p-2 rounded-lg">
                <Rocket className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold">NASA Space Biology</span>
            </div>
            <p className="text-sm text-secondary-foreground/80">
              Advancing our understanding of life in space through research, exploration, and innovation.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="hover:text-accent transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-accent transition-colors">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/search" className="hover:text-accent transition-colors">
                  Search Database
                </Link>
              </li>
              <li>
                <Link to="/faq" className="hover:text-accent transition-colors">
                  FAQ
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-accent transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold mb-4">Connect</h3>
            <ul className="space-y-3">
              <li className="flex items-center space-x-2 text-sm">
                <Mail className="h-4 w-4 text-accent" />
                <span>biology@nasa.gov</span>
              </li>
              <li className="flex items-center space-x-2 text-sm">
                <Globe className="h-4 w-4 text-accent" />
                <a href="https://nasa.gov" className="hover:text-accent transition-colors">
                  nasa.gov
                </a>
              </li>
              <li className="flex items-center space-x-2 text-sm">
                <Github className="h-4 w-4 text-accent" />
                <a href="#" className="hover:text-accent transition-colors">
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-secondary-foreground/20 mt-8 pt-8 text-center text-sm text-secondary-foreground/60">
          <p>© 2025 NASA Space Biology Knowledge Engine. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
