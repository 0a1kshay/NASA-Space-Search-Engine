import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Search, HelpCircle } from "lucide-react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const FAQ = () => {
  const faqs = [
  {
    category: "Getting Started",
    questions: [
      {
        q: "What is the NASA Space Biology Knowledge Engine?",
        a: "The NASA Space Biology Knowledge Engine is an open-access research platform that aggregates, analyzes, and visualizes biological data collected from spaceflight and analog missions. It connects experiments, missions, and publications to accelerate discoveries in life sciences beyond Earth.",
      },
      {
        q: "How do I search the database?",
        a: "You can use the global search bar on the homepage or the dedicated Search page for advanced filters. Search by mission name, organism type, experimental conditions, or specific biological outcomes. The search engine supports keyword, semantic, and DOI-based searches.",
      },
      {
        q: "Do I need an account to access the data?",
        a: "Basic access to mission summaries and publications is public. However, creating a free researcher account allows you to bookmark results, export datasets, customize dashboards, and request access to restricted data collections.",
      },
      {
        q: "How often is the database updated?",
        a: "The Knowledge Engine is continuously updated as NASA missions conclude and new research is published. Major data synchronization occurs monthly, while peer-reviewed publication imports and metadata updates happen in real time through automated pipelines.",
      },
    ],
  },
  {
    category: "Data & Research",
    questions: [
      {
        q: "What types of data are available?",
        a: "The repository hosts mission experiment reports, omics data (genomics, proteomics, metabolomics), microbial profiles, physiological measurements, imagery, and environmental parameters from spaceflight studies. Supported formats include CSV, JSON, HDF5, and image data (TIFF, PNG).",
      },
      {
        q: "Where does the data come from?",
        a: "Data originates from NASA-funded missions such as ISS, Space Shuttle, and Artemis-related research, as well as partner organizations like ESA and JAXA. Each dataset is curated and validated through NASA’s GeneLab and Space Biology repositories.",
      },
      {
        q: "Can I download datasets?",
        a: "Yes. Most datasets are available for direct download. Sensitive or embargoed datasets may require authenticated access or institutional verification. Download links appear on the dataset page once access permissions are granted.",
      },
      {
        q: "How can I cite data from this platform?",
        a: "Each dataset and publication includes a unique DOI (Digital Object Identifier). Click on the ‘Cite This’ button on a dataset or publication page to copy citations in multiple formats such as APA, MLA, or BibTeX.",
      },
    ],
  },
  {
    category: "Technical Support",
    questions: [
      {
        q: "What browsers are supported?",
        a: "We support the latest versions of Chrome, Firefox, Edge, and Safari. For optimal visualization and WebGL performance, ensure that hardware acceleration is enabled and your GPU drivers are up to date.",
      },
      {
        q: "I can’t view charts or 3D visualizations. What should I do?",
        a: "Check that WebGL is enabled in your browser settings. If issues persist, clear the cache, disable browser extensions, or try a different browser. For institutional computers, verify that WebGL isn’t restricted by network policy.",
      },
      {
        q: "How do I report a bug or issue?",
        a: "Visit the Contact page or email support@spacebioengine.nasa.gov with a detailed description, including screenshots, your browser version, and steps to reproduce the issue. Our technical team responds within 48 hours.",
      },
    ],
  },
  {
    category: "Account & Profile",
    questions: [
      {
        q: "How do I create an account?",
        a: "Click 'Sign Up' in the top navigation bar and fill out the registration form. You can also sign in with your ORCID or Google account for faster onboarding and automatic researcher verification.",
      },
      {
        q: "Can I change my password or email?",
        a: "Yes. Go to your profile settings and update your credentials. A verification email will be sent to confirm any changes before they take effect.",
      },
      {
        q: "How do I delete my account?",
        a: "You can delete your account under Profile Settings → Account → Delete Account. This is a permanent action and removes all saved searches, bookmarks, and API tokens.",
      },
    ],
    },
    {
      category: "Technical Support",
      questions: [
        {
          q: "What browsers are supported?",
          a: "The Knowledge Engine works best on the latest versions of Chrome, Firefox, Safari, and Edge. We recommend keeping your browser updated for optimal performance.",
        },
        {
          q: "I'm having trouble viewing visualizations. What should I do?",
          a: "Ensure your browser supports WebGL and that hardware acceleration is enabled. If problems persist, try clearing your browser cache or using a different browser.",
        },
        {
          q: "How do I report a bug or technical issue?",
          a: "Please use the Contact form to report any technical issues. Include details about your browser, operating system, and the specific problem you're experiencing.",
        },
      ],
    },
    {
      category: "Account & Profile",
      questions: [
        {
          q: "How do I create an account?",
          a: "Click the 'Sign Up' button in the top right corner and fill out the registration form. You can also sign up using your Google account for faster registration.",
        },
        {
          q: "Can I change my email address?",
          a: "Yes, you can update your email address in your profile settings. You'll need to verify the new email address before the change takes effect.",
        },
        {
          q: "How do I delete my account?",
          a: "Navigate to Profile Settings > Account > Delete Account. Note that this action is permanent and will remove all your saved searches and bookmarks.",
        },
      ],
    },
    {
      category: "Research & Collaboration",
      questions: [
        {
          q: "How can I contribute data to the knowledge engine?",
          a: "Researchers with NASA-affiliated missions can submit data through our data submission portal. Contact us for access credentials and submission guidelines.",
        },
        {
          q: "Can I collaborate with other researchers through this platform?",
          a: "While direct collaboration features are limited, you can share searches and datasets with colleagues. We're developing enhanced collaboration tools for future releases.",
        },
        {
          q: "Are there APIs available for programmatic access?",
          a: "Yes, we offer REST APIs for authorized researchers and institutions. Contact our technical support team to request API access and documentation.",
        },
      ],
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />

      <main className="flex-1">
        {/* Header */}
        <div className="bg-gradient-space py-16">
          <div className="container mx-auto px-4 text-center">
            <HelpCircle className="h-16 w-16 text-accent mx-auto mb-4" />
            <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
              Frequently Asked Questions
            </h1>
            <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto mb-8">
              Find answers to common questions about using the NASA Space Biology Knowledge Engine
            </p>

            {/* Search */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  placeholder="Search FAQs..."
                  className="pl-10 h-12 bg-card"
                />
              </div>
            </div>
          </div>
        </div>

        {/* FAQs */}
        <div className="container mx-auto px-4 py-12 max-w-4xl">
          <div className="space-y-8">
            {faqs.map((category, categoryIndex) => (
              <Card key={categoryIndex}>
                <CardContent className="p-6">
                  <h2 className="text-2xl font-bold mb-6 text-accent">{category.category}</h2>
                  <Accordion type="single" collapsible className="w-full">
                    {category.questions.map((faq, faqIndex) => (
                      <AccordionItem key={faqIndex} value={`item-${categoryIndex}-${faqIndex}`}>
                        <AccordionTrigger className="text-left">
                          {faq.q}
                        </AccordionTrigger>
                        <AccordionContent className="text-muted-foreground">
                          {faq.a}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Still Need Help */}
          <Card className="mt-12 bg-gradient-accent text-white">
            <CardContent className="p-8 text-center">
              <h2 className="text-2xl font-bold mb-4">Still have questions?</h2>
              <p className="mb-6 opacity-90">
                Can't find the answer you're looking for? Our support team is here to help.
              </p>
              <a href="/contact">
                <button className="bg-white text-accent px-6 py-3 rounded-lg font-semibold hover:bg-white/90 transition-colors">
                  Contact Support
                </button>
              </a>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default FAQ;
