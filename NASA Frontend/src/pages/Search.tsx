import { useState, useMemo, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search as SearchIcon, Filter, X, Calendar, MapPin, Users, BookOpen, Database, TrendingUp, Loader2, AlertCircle } from "lucide-react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { nasaAPI } from "@/services/api";
import { toast } from "sonner";

// Dummy data with proper categories and detailed information
const searchData = [
  {
    id: 1,
    title: "Effects of Microgravity on Plant Cell Wall Formation",
    type: "Research Papers",
    mission: "ISS National Lab",
    date: "2024",
    description: "Comprehensive analysis of how microgravity affects cellular structures in plant tissues, providing insights for future space agriculture.",
    tags: ["microgravity", "plant biology", "cell structure"],
    details: {
      summary: {
        objective: "To investigate how microgravity conditions affect plant cell wall formation and structural integrity in space environments.",
        methodology: "Arabidopsis thaliana samples were grown aboard the International Space Station for 30 days under controlled conditions. Cell wall thickness, composition, and structural proteins were analyzed using electron microscopy and biochemical assays.",
        keyFindings: [
          "Cell wall thickness decreased by 23% in microgravity conditions",
          "Altered expression of cellulose synthase genes",
          "Reduced lignin deposition in vascular tissues",
          "Modified pectin cross-linking patterns"
        ],
        implications: "These findings suggest significant structural adaptations in plant tissues under microgravity, with implications for space agriculture and food production systems."
      },
      overview: {
        authors: ["Dr. Sarah Chen", "Dr. Michael Rodriguez", "Dr. Lisa Zhang"],
        institution: "NASA Ames Research Center",
        fundingSource: "NASA Space Biology Program",
        duration: "24 months",
        subjects: "Arabidopsis thaliana seedlings",
        location: "International Space Station - Japanese Experiment Module",
        collaborators: ["JAXA", "European Space Agency", "University of California"]
      },
      knowledge: {
        relatedStudies: [
          "Microgravity Effects on Root Development (2023)",
          "Plant Hormone Regulation in Space (2022)",
          "Cell Division Patterns in Zero Gravity (2024)"
        ],
        applications: [
          "Space agriculture systems",
          "Lunar greenhouse design",
          "Mars habitat food production",
          "Earth-based controlled environment agriculture"
        ],
        futureResearch: [
          "Long-term plant adaptation studies",
          "Genetic modification for space environments",
          "Nutrient delivery optimization in microgravity"
        ]
      }
    }
  },
  {
    id: 2,
    title: "Arabidopsis Gene Expression in Space Flight",
    type: "OSDR Data",
    mission: "SpaceX CRS-20",
    date: "2023",
    description: "Complete transcriptomic dataset from Arabidopsis thaliana grown aboard the International Space Station for 30 days.",
    tags: ["gene expression", "arabidopsis", "transcriptomics"],
    details: {
      summary: {
        objective: "To analyze comprehensive gene expression changes in Arabidopsis thaliana during space flight conditions.",
        methodology: "RNA-seq analysis of whole plant tissues collected at multiple time points during 30-day growth period on ISS.",
        keyFindings: [
          "2,847 genes showed significant expression changes",
          "Stress response pathways were highly upregulated",
          "Cell wall biosynthesis genes were downregulated",
          "Gravitropic response genes showed altered expression patterns"
        ],
        implications: "This dataset provides crucial insights into plant molecular adaptation mechanisms in space environments."
      },
      overview: {
        authors: ["Dr. Anna Kowalski", "Dr. James Thompson", "Dr. Yuki Tanaka"],
        institution: "Kennedy Space Center",
        fundingSource: "OSDR Data Repository",
        duration: "30 days",
        subjects: "Arabidopsis thaliana (Columbia ecotype)",
        location: "International Space Station - Vegetable Production System",
        collaborators: ["JAXA", "ESA", "University of Wisconsin"]
      },
      knowledge: {
        relatedStudies: [
          "Plant Stress Response in Microgravity (2022)",
          "Comparative Genomics of Space-Grown Plants (2023)",
          "Transcriptional Networks in Zero Gravity (2024)"
        ],
        applications: [
          "Plant breeding for space missions",
          "Biomarker development for plant stress",
          "Agricultural optimization on Earth",
          "Space food security planning"
        ],
        futureResearch: [
          "Multi-generational gene expression studies",
          "Epigenetic modifications in space",
          "Single-cell RNA sequencing in microgravity"
        ]
      }
    }
  },
  {
    id: 3,
    title: "Investigating Bone Density Changes in Microgravity",
    type: "Task Book Grants",
    mission: "NASA Human Research Program",
    date: "2024",
    description: "Multi-year investigation into bone mineralization and density changes in astronauts during long-duration space missions.",
    tags: ["bone density", "human physiology", "astronaut health"],
    details: {
      summary: {
        objective: "To understand and mitigate bone density loss in astronauts during extended space missions.",
        methodology: "Longitudinal study of 45 astronauts using DEXA scans, biochemical markers, and exercise intervention protocols.",
        keyFindings: [
          "Average bone density loss of 1.5% per month in microgravity",
          "Hip and spine most affected regions",
          "Exercise countermeasures reduce loss by 40%",
          "Recovery takes 6-18 months post-mission"
        ],
        implications: "Critical for planning Mars missions and long-duration space exploration safety protocols."
      },
      overview: {
        authors: ["Dr. Maria Santos", "Dr. Robert Kim", "Dr. Elena Petrov"],
        institution: "Johnson Space Center",
        fundingSource: "NASA Human Research Program",
        duration: "60 months",
        subjects: "45 astronauts (6-month missions)",
        location: "International Space Station",
        collaborators: ["Mayo Clinic", "Harvard Medical School", "ESA"]
      },
      knowledge: {
        relatedStudies: [
          "Muscle Atrophy in Space (2023)",
          "Cardiovascular Changes in Microgravity (2022)",
          "Bone Remodeling Mechanisms (2024)"
        ],
        applications: [
          "Mars mission health protocols",
          "Osteoporosis treatment on Earth",
          "Aging and bone health research",
          "Exercise equipment design for space"
        ],
        futureResearch: [
          "Pharmaceutical interventions for bone loss",
          "Artificial gravity effectiveness studies",
          "Nutrition optimization for bone health"
        ]
      }
    }
  },
  // Simplified entries for remaining items
  {
    id: 4,
    title: "Radiation Effects on DNA Repair Mechanisms",
    type: "Research Papers",
    mission: "Mars Simulation Study",
    date: "2023",
    description: "Study of how cosmic radiation affects cellular DNA repair processes in mammalian cells.",
    tags: ["radiation", "DNA repair", "space medicine"],
    details: {
      summary: {
        objective: "Investigate cosmic radiation effects on DNA repair in mammalian cells.",
        methodology: "Cell culture studies with simulated cosmic radiation exposure.",
        keyFindings: ["Increased DNA damage", "Altered repair kinetics", "Cell cycle disruption"],
        implications: "Important for astronaut safety on Mars missions."
      },
      overview: {
        authors: ["Dr. John Smith", "Dr. Jane Doe"],
        institution: "NASA Goddard",
        fundingSource: "NASA Space Biology",
        duration: "18 months",
        subjects: "Human cell cultures",
        location: "Ground-based laboratory",
        collaborators: ["MIT", "Stanford University"]
      },
      knowledge: {
        relatedStudies: ["Space Radiation Biology (2022)", "Mars Mission Health (2023)"],
        applications: ["Astronaut protection", "Cancer research", "Radiation therapy"],
        futureResearch: ["Protective compounds", "Genetic resistance factors"]
      }
    }
  }
];

const Search = () => {
  const [showFilters, setShowFilters] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState("relevance");
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // API state
  const [apiResults, setApiResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [databaseStats, setDatabaseStats] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [realCsvData, setRealCsvData] = useState<any[]>([]);
  const [loadingCsvData, setLoadingCsvData] = useState(true);
  
  // NASA API integration state
  const [includeNasaApis, setIncludeNasaApis] = useState(true);
  const [nasaApiStatus, setNasaApiStatus] = useState<any>(null);
  const [showNasaOnly, setShowNasaOnly] = useState(false);

  // Fetch database statistics and real CSV data on component mount
  useEffect(() => {
    const fetchDatabaseStats = async () => {
      try {
        setLoadingStats(true);
        const response = await nasaAPI.getSearchStats();
        setDatabaseStats(response.data);
      } catch (err: any) {
        console.error('Failed to fetch database stats:', err);
      } finally {
        setLoadingStats(false);
      }
    };

    const fetchRealCsvData = async () => {
      try {
        setLoadingCsvData(true);
        // Load a sample of real CSV data to get accurate filter counts
        const response = await nasaAPI.searchArticles("", 1000, false);
        
        if (response.data?.results) {
          const transformedData = response.data.results.map(item => ({
            id: item.id || Math.random(),
            title: item.title || 'Untitled Research',
            type: item.content_type || item.type || 'Research Papers',
            mission: item.mission || item.organization || 'NASA',
            date: item.date || item.publication_date || 'Date not available',
            description: item.abstract || item.description || 'Description not available',
            tags: item.tags || [],
            source: item.source || item.search_source || 'NASA Database',
            isNasaApi: item.is_nasa_api || false,
            relevanceScore: item.relevance_score || 0.5
          }));
          setRealCsvData(transformedData);
        }
      } catch (err: any) {
        console.error('Failed to fetch real CSV data:', err);
        // Fallback to dummy data if real data fails to load
        setRealCsvData([]);
      } finally {
        setLoadingCsvData(false);
      }
    };

    fetchDatabaseStats();
    fetchRealCsvData();
  }, []);

  // Test NASA APIs function
  const testNasaApis = async () => {
    try {
      const response = await nasaAPI.testNASAAPIs();
      setNasaApiStatus(response.data);
      toast.success("NASA API test completed - check results");
    } catch (err: any) {
      console.error('NASA API test failed:', err);
      toast.error("NASA API test failed");
    }
  };

  // Generate key findings from research data
  const generateKeyFindings = (item: any): string[] => {
    const findings: string[] = [];
    
    // Extract key findings from tags/keywords
    const tags = item.tags || item.keywords || [];
    if (tags.length > 0) {
      // Create findings based on research areas
      if (tags.includes('Space Biology')) {
        findings.push('Significant contributions to space biology research');
      }
      if (tags.includes('Microgravity')) {
        findings.push('Important insights into microgravity effects on biological systems');
      }
      if (tags.includes('Space Radiation')) {
        findings.push('Key findings on space radiation impact and mitigation');
      }
      if (tags.includes('Bone Research')) {
        findings.push('Critical discoveries in bone health during spaceflight');
      }
      if (tags.includes('Muscle Research')) {
        findings.push('Essential findings on muscle adaptation in space environment');
      }
      if (tags.includes('Cell Biology')) {
        findings.push('Fundamental cellular-level discoveries for space missions');
      }
      if (tags.includes('Plant Biology')) {
        findings.push('Breakthrough research in plant growth and adaptation in space');
      }
      if (tags.includes('Human Research')) {
        findings.push('Vital human health findings for long-duration space missions');
      }
      if (tags.includes('ISS Research')) {
        findings.push('International Space Station research providing unique insights');
      }
      if (tags.includes('Technology Development')) {
        findings.push('Innovative technology developments for space exploration');
      }
    }
    
    // Add findings based on research type
    const researchType = item.type;
    if (researchType === 'Task Book Grants') {
      findings.push('NASA-funded research project with strategic importance');
    } else if (researchType === 'OSDR Data') {
      findings.push('Open Science Data Repository findings available for further research');
    }
    
    // If no specific findings, create generic but meaningful ones
    if (findings.length === 0) {
      findings.push('Research contributes to NASA\'s space exploration goals');
      if (item.date && parseInt(item.date) >= 2020) {
        findings.push('Recent research findings relevant to current space missions');
      }
    }
    
    // Limit to 3 most relevant findings
    return findings.slice(0, 3);
  };

  // Generate overview data from research information
  const generateOverviewData = (item: any) => {
    const researchType = item.type;
    const tags = item.tags || [];
    const date = item.date;
    const authors = item.authors || ['NASA Space Biology Database'];
    
    // Determine institution based on research type and data
    let institution = 'NASA';
    let department = 'Space Biology Research Division';
    let location = 'NASA Research Center';
    let fundingSource = 'NASA';
    let labFacilities = 'Space Biology Laboratory';
    
    if (researchType === 'Task Book Grants') {
      institution = 'NASA';
      department = 'Human Research Program';
      location = 'NASA Johnson Space Center';
      fundingSource = 'NASA Task Book Program';
      labFacilities = 'Advanced Research Laboratory, Flight Systems Lab';
    } else if (researchType === 'OSDR Data') {
      institution = 'NASA';
      department = 'Open Science Data Repository';
      location = 'NASA Ames Research Center';
      fundingSource = 'NASA Open Science Initiative';
      labFacilities = 'Bioinformatics Center, Data Analysis Lab';
    }
    
    // Adjust based on research focus
    if (tags.includes('Human Research')) {
      department = 'Human Research Program';
      location = 'NASA Johnson Space Center';
      labFacilities = 'Human Research Facility, Medical Operations Lab';
    } else if (tags.includes('Plant Biology')) {
      department = 'Space Biology Research Division';
      labFacilities = 'Advanced Plant Growth Facility, Controlled Environment Laboratory';
    } else if (tags.includes('Bone Research') || tags.includes('Muscle Research')) {
      department = 'Human Research Program';
      labFacilities = 'Bone & Muscle Laboratory, Exercise Countermeasures Lab';
    } else if (tags.includes('Space Radiation')) {
      department = 'Space Radiation Laboratory';
      location = 'NASA Langley Research Center';
      labFacilities = 'Radiation Biology Laboratory, Particle Accelerator Facility';
    } else if (tags.includes('Microgravity')) {
      department = 'Physical Sciences Research';
      labFacilities = 'Microgravity Science Laboratory, Drop Tower Facility';
    }
    
    // Generate research staff based on research scope and type
    let researchStaff = 'Research staff information not available';
    if (researchType === 'Task Book Grants') {
      researchStaff = 'Principal investigator with graduate students and research associates';
    } else if (tags.includes('Human Research')) {
      researchStaff = 'Multidisciplinary team including physicians, researchers, and technicians';
    } else if (tags.includes('Plant Biology')) {
      researchStaff = 'Plant biologists, technicians, and graduate research assistants';
    } else {
      researchStaff = 'Research scientists and laboratory technicians';
    }
    
    // Determine subjects based on research area
    let subjects = 'Research subjects not specified';
    if (tags.includes('Human Research')) {
      subjects = 'Human subjects (astronauts and ground controls)';
    } else if (tags.includes('Plant Biology')) {
      subjects = 'Plant specimens and tissue cultures';
    } else if (tags.includes('Cell Biology')) {
      subjects = 'Cell cultures and biological samples';
    } else if (tags.includes('Bone Research') || tags.includes('Muscle Research')) {
      subjects = 'Human physiological measurements and tissue samples';
    }
    
    // Generate duration estimate based on publication date and type
    let duration = 'Duration not specified';
    if (date && parseInt(date) >= 2020) {
      if (researchType === 'Task Book Grants') {
        duration = 'Multi-year research project (ongoing)';
      } else {
        duration = 'Research study completed';
      }
    } else if (date) {
      duration = 'Historical research project';
    }
    
    return {
      authors: authors,
      institution: institution,
      department: department, 
      fundingSource: fundingSource,
      duration: duration,
      subjects: subjects,
      location: location,
      labFacilities: labFacilities,
      researchStaff: researchStaff,
      collaborators: ['NASA', 'International partners']
    };
  };

  // Generate knowledge graph data from research tags and content
  const generateKnowledgeGraph = (item: any) => {
    const tags = item.tags || [];
    const title = item.title || '';
    const type = item.type || 'Research';
    const abstract = item.abstract || '';
    
    // Determine central concept based on research focus with better prioritization
    let centralConcept = 'Space Research';
    
    // Priority order for central concept selection
    if (tags.includes('Human Research') || title.toLowerCase().includes('human') || title.toLowerCase().includes('astronaut')) {
      centralConcept = 'Human Space Research';
    } else if (tags.includes('Technology Development') || title.toLowerCase().includes('technology') || title.toLowerCase().includes('device')) {
      centralConcept = 'Space Technology';
    } else if (tags.includes('Plant Biology') || title.toLowerCase().includes('plant') || title.toLowerCase().includes('arabidopsis')) {
      centralConcept = 'Space Plant Science';
    } else if (tags.includes('Bone Research') || title.toLowerCase().includes('bone') || title.toLowerCase().includes('skeletal')) {
      centralConcept = 'Bone & Skeletal Research';
    } else if (tags.includes('Space Radiation') || title.toLowerCase().includes('radiation')) {
      centralConcept = 'Space Radiation Studies';
    } else if (tags.includes('Microgravity') || title.toLowerCase().includes('microgravity')) {
      centralConcept = 'Microgravity Research';
    } else if (tags.includes('Cell Biology') || title.toLowerCase().includes('cell') || title.toLowerCase().includes('cellular')) {
      centralConcept = 'Space Cell Biology';
    } else if (tags.includes('Muscle Research') || title.toLowerCase().includes('muscle')) {
      centralConcept = 'Muscle Physiology';
    }
    
    // Generate connected nodes with enhanced categorization
    const connectedNodes = [];
    const addedNodes = new Set();
    
    // Add primary research tags as connected nodes
    tags.forEach(tag => {
      if (tag !== 'Space Biology' && !centralConcept.toLowerCase().includes(tag.toLowerCase()) && !addedNodes.has(tag)) {
        connectedNodes.push({
          name: tag,
          category: getCategoryForTag(tag),
          priority: getTagPriority(tag)
        });
        addedNodes.add(tag);
      }
    });
    
    // Add contextual nodes based on research type and content
    if (type === 'Task Book Grants' && !addedNodes.has('ISS Operations')) {
      connectedNodes.push({
        name: 'ISS Operations',
        category: 'Platform',
        priority: 8
      });
      addedNodes.add('ISS Operations');
    }
    
    // Add methodology nodes based on title content analysis
    if ((title.toLowerCase().includes('gene') || title.toLowerCase().includes('expression') || abstract.toLowerCase().includes('gene')) && !addedNodes.has('Genomics')) {
      connectedNodes.push({
        name: 'Genomics',
        category: 'Method',
        priority: 7
      });
      addedNodes.add('Genomics');
    }
    
    if ((title.toLowerCase().includes('protein') || title.toLowerCase().includes('molecular') || abstract.toLowerCase().includes('molecular')) && !addedNodes.has('Molecular Analysis')) {
      connectedNodes.push({
        name: 'Molecular Analysis',
        category: 'Method',
        priority: 6
      });
      addedNodes.add('Molecular Analysis');
    }
    
    if ((title.toLowerCase().includes('growth') || title.toLowerCase().includes('development')) && !addedNodes.has('Growth Studies')) {
      connectedNodes.push({
        name: 'Growth Studies',
        category: 'Process',
        priority: 5
      });
      addedNodes.add('Growth Studies');
    }
    
    // Sort by priority and limit to 4 most relevant nodes
    const sortedNodes = connectedNodes
      .sort((a, b) => b.priority - a.priority)
      .slice(0, 4);
    
    return {
      centralConcept,
      connectedNodes: sortedNodes
    };
  };

  // Helper function to get category for research tags
  const getCategoryForTag = (tag: string): string => {
    const categoryMap: { [key: string]: string } = {
      'Human Research': 'Domain',
      'Plant Biology': 'Life Science',
      'Cell Biology': 'Life Science', 
      'Bone Research': 'Physiology',
      'Muscle Research': 'Physiology',
      'Space Radiation': 'Environment',
      'Microgravity': 'Environment',
      'Technology Development': 'Innovation',
      'ISS Research': 'Platform',
      'OSDR Data': 'Data Repository'
    };
    return categoryMap[tag] || 'Research Area';
  };

  // Helper function to get priority for tags
  const getTagPriority = (tag: string): number => {
    const priorityMap: { [key: string]: number } = {
      'Human Research': 10,
      'Technology Development': 9,
      'Plant Biology': 8,
      'Space Radiation': 7,
      'Microgravity': 7,
      'Bone Research': 6,
      'Cell Biology': 6,
      'Muscle Research': 5,
      'ISS Research': 4
    };
    return priorityMap[tag] || 3;
  };

  // Generate related studies based on research tags and content
  const generateRelatedStudies = (item: any): string[] => {
    const tags = item.tags || [];
    const title = item.title || '';
    const studies = [];
    
    // Generate related studies based on research area
    if (tags.includes('Human Research') || title.toLowerCase().includes('human')) {
      studies.push('Astronaut Physiological Adaptation Studies');
      studies.push('Human Performance in Microgravity Environment');
      studies.push('Cardiovascular Deconditioning Research');
    }
    
    if (tags.includes('Plant Biology') || title.toLowerCase().includes('plant')) {
      studies.push('Plant Growth Systems for Long-Duration Spaceflight');
      studies.push('Arabidopsis Gene Expression in Microgravity');
      studies.push('Space Agriculture Development Programs');
    }
    
    if (tags.includes('Bone Research') || title.toLowerCase().includes('bone')) {
      studies.push('Bone Density Loss Prevention Studies');
      studies.push('Countermeasure Exercise Equipment Research');
      studies.push('Calcium Metabolism in Space Environment');
    }
    
    if (tags.includes('Space Radiation') || title.toLowerCase().includes('radiation')) {
      studies.push('Cosmic Radiation Shielding Technologies');
      studies.push('DNA Damage from Space Radiation Exposure');
      studies.push('Radiation Risk Assessment for Mars Missions');
    }
    
    if (tags.includes('Technology Development') || title.toLowerCase().includes('technology')) {
      studies.push('Advanced Life Support Systems Research');
      studies.push('In-Situ Resource Utilization Technologies');
      studies.push('Robotic Systems for Space Exploration');
    }
    
    // Default studies if no specific tags
    if (studies.length === 0) {
      studies.push('International Space Station Research Programs');
      studies.push('NASA Space Biology Research Portfolio');
      studies.push('Fundamental Space Research Initiatives');
    }
    
    return studies.slice(0, 3); // Limit to 3 related studies
  };

  // Generate practical applications based on research focus
  const generateApplications = (item: any): string[] => {
    const tags = item.tags || [];
    const title = item.title || '';
    const applications = [];
    
    if (tags.includes('Human Research') || title.toLowerCase().includes('human')) {
      applications.push('Long-duration spaceflight mission preparation');
      applications.push('Medical monitoring systems for astronauts');
      applications.push('Terrestrial healthcare applications for aging');
    }
    
    if (tags.includes('Plant Biology') || title.toLowerCase().includes('plant')) {
      applications.push('Sustainable food production in space');
      applications.push('Closed-loop life support systems');
      applications.push('Agricultural optimization on Earth');
    }
    
    if (tags.includes('Bone Research') || title.toLowerCase().includes('bone')) {
      applications.push('Osteoporosis prevention treatments');
      applications.push('Exercise countermeasure protocols');
      applications.push('Bone health monitoring devices');
    }
    
    if (tags.includes('Space Radiation') || title.toLowerCase().includes('radiation')) {
      applications.push('Spacecraft radiation shielding design');
      applications.push('Cancer treatment research');
      applications.push('Radiation detection instrumentation');
    }
    
    if (tags.includes('Technology Development') || title.toLowerCase().includes('technology')) {
      applications.push('Mars mission technology development');
      applications.push('Commercial space industry applications');
      applications.push('Earth-based technology transfer');
    }
    
    // Default applications
    if (applications.length === 0) {
      applications.push('Space exploration mission support');
      applications.push('Scientific research advancement');
      applications.push('International space collaboration');
    }
    
    return applications.slice(0, 3);
  };

  // Generate future research directions
  const generateFutureResearch = (item: any): string[] => {
    const tags = item.tags || [];
    const title = item.title || '';
    const directions = [];
    
    if (tags.includes('Human Research') || title.toLowerCase().includes('human')) {
      directions.push('Mars mission crew health optimization');
      directions.push('Advanced physiological monitoring systems');
      directions.push('Genetic adaptation to space environment');
    }
    
    if (tags.includes('Plant Biology') || title.toLowerCase().includes('plant')) {
      directions.push('Multi-generational plant studies in space');
      directions.push('Bioregenerative life support system integration');
      directions.push('Crop optimization for planetary habitats');
    }
    
    if (tags.includes('Bone Research') || title.toLowerCase().includes('bone')) {
      directions.push('Pharmaceutical countermeasures development');
      directions.push('Artificial gravity system research');
      directions.push('Bone tissue engineering in microgravity');
    }
    
    if (tags.includes('Space Radiation') || title.toLowerCase().includes('radiation')) {
      directions.push('Advanced radiation protection materials');
      directions.push('Biological radiation resistance mechanisms');
      directions.push('Deep space radiation environment modeling');
    }
    
    if (tags.includes('Technology Development') || title.toLowerCase().includes('technology')) {
      directions.push('Autonomous systems for deep space missions');
      directions.push('Next-generation spacecraft technologies');
      directions.push('Interplanetary communication systems');
    }
    
    // Default future research
    if (directions.length === 0) {
      directions.push('Advanced space exploration capabilities');
      directions.push('Interdisciplinary space science research');
      directions.push('Sustainable space habitat development');
    }
    
    return directions.slice(0, 3);
  };

  // Generate methodology description based on research content
  const generateMethodology = (item: any): string => {
    const tags = item.tags || [];
    const title = item.title || '';
    const type = item.type || '';
    
    let methodology = '';
    
    if (tags.includes('Human Research') || title.toLowerCase().includes('human')) {
      methodology = 'Physiological monitoring and assessment protocols using non-invasive measurement techniques, controlled environment studies aboard the International Space Station, and comparative analysis with terrestrial control groups.';
    } else if (tags.includes('Plant Biology') || title.toLowerCase().includes('plant')) {
      methodology = 'Controlled growth experiments in microgravity environment, gene expression analysis using RNA sequencing, morphological assessment, and comparison with ground-based controls under similar conditions.';
    } else if (tags.includes('Bone Research') || title.toLowerCase().includes('bone')) {
      methodology = 'Bone density measurements using dual-energy X-ray absorptiometry, biochemical marker analysis, exercise intervention protocols, and longitudinal monitoring of skeletal health parameters.';
    } else if (tags.includes('Space Radiation') || title.toLowerCase().includes('radiation')) {
      methodology = 'Radiation dosimetry measurements, biological sample analysis for DNA damage assessment, computational modeling of radiation effects, and protective countermeasure evaluation.';
    } else if (tags.includes('Technology Development') || title.toLowerCase().includes('technology')) {
      methodology = 'Prototype development and testing, performance validation in simulated space environments, system integration testing, and operational reliability assessment under extreme conditions.';
    } else if (type === 'Task Book Grants') {
      methodology = 'Multi-phase research approach including literature review, experimental design, data collection and analysis, with regular progress reviews and milestone assessments throughout the project timeline.';
    } else {
      methodology = 'Systematic research approach involving controlled experimental design, data collection using standardized protocols, statistical analysis of results, and peer review validation of findings.';
    }
    
    return methodology;
  };

  // Generate research implications based on study focus
  const generateImplications = (item: any): string => {
    const tags = item.tags || [];
    const title = item.title || '';
    
    let implications = '';
    
    if (tags.includes('Human Research') || title.toLowerCase().includes('human')) {
      implications = 'Critical for ensuring astronaut health and performance during long-duration space missions. Findings contribute to medical countermeasures and support systems for future Mars exploration and deep space missions.';
    } else if (tags.includes('Plant Biology') || title.toLowerCase().includes('plant')) {
      implications = 'Essential for developing sustainable food production systems for space habitats. Research supports closed-loop life support systems and contributes to agricultural sustainability on Earth.';
    } else if (tags.includes('Bone Research') || title.toLowerCase().includes('bone')) {
      implications = 'Vital for preventing bone loss in astronauts and developing effective countermeasures. Results inform exercise protocols and pharmaceutical interventions for space missions and terrestrial osteoporosis treatment.';
    } else if (tags.includes('Space Radiation') || title.toLowerCase().includes('radiation')) {
      implications = 'Crucial for protecting crew health during space exploration. Findings inform radiation shielding design and risk mitigation strategies for interplanetary missions beyond Earth\'s magnetosphere.';
    } else if (tags.includes('Technology Development') || title.toLowerCase().includes('technology')) {
      implications = 'Advances space exploration capabilities and enables more ambitious missions. Technology developments often have dual-use applications benefiting both space exploration and terrestrial industries.';
    } else {
      implications = 'Contributes to the fundamental understanding of biological and physical processes in space environment, supporting the advancement of space science and exploration capabilities.';
    }
    
    return implications;
  };
  
  // Helper function to get node color based on category and research area
  const getNodeColor = (node: any): string => {
    const tag = typeof node === 'string' ? node : (node?.name || node);
    const category = typeof node === 'object' ? node?.category : null;
    
    // Color by category for better visual organization
    if (category) {
      const categoryColors: { [key: string]: string } = {
        'Domain': 'bg-red-400',
        'Life Science': 'bg-green-400',
        'Physiology': 'bg-orange-400',
        'Environment': 'bg-blue-400',
        'Innovation': 'bg-purple-400',
        'Platform': 'bg-cyan-400',
        'Method': 'bg-teal-400',
        'Process': 'bg-lime-400',
        'Data Repository': 'bg-slate-400'
      };
      return categoryColors[category] || 'bg-indigo-400';
    }
    
    // Fallback to tag-based colors for enhanced visualization
    const colorMap: { [key: string]: string } = {
      'Human Research': 'bg-red-400',
      'Microgravity': 'bg-blue-400',
      'Space Radiation': 'bg-orange-400',
      'Bone Research': 'bg-amber-400',
      'Muscle Research': 'bg-yellow-400',
      'Plant Biology': 'bg-green-400',
      'Cell Biology': 'bg-emerald-400',
      'Technology Development': 'bg-purple-400',
      'ISS Research': 'bg-cyan-400',
      'ISS Operations': 'bg-cyan-500',
      'OSDR Data': 'bg-purple-400',
      'Task Book Grants': 'bg-pink-400',
      'Genomics': 'bg-teal-500',
      'Molecular Analysis': 'bg-purple-500',
      'Growth Studies': 'bg-lime-500'
    };
    return colorMap[tag] || 'bg-slate-400';
  };
  
  // Helper function to get node position
  const getNodePosition = (index: number): { [key: string]: string } => {
    const positions = [
      { top: '16px', left: '16px' },      // Top left
      { top: '16px', right: '16px' },     // Top right  
      { bottom: '16px', right: '24px' },  // Bottom right
      { bottom: '16px', left: '16px' }    // Bottom left
    ];
    return positions[index] || positions[0];
  };

  // API search function
  const performSearch = async (query: string = searchTerm) => {
    if (!query.trim()) {
      setApiResults([]);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      let response;
      if (showNasaOnly) {
        // Search only NASA APIs
        response = await nasaAPI.searchNASAOnly(query, 50);
      } else {
        // Search with local + NASA APIs integration
        response = await nasaAPI.searchArticles(query, 50, includeNasaApis);
      }
      
      const results = response.data.results || [];
      
      // Transform API results to match our component structure
      const transformedResults = results.map((item: any, index: number) => ({
        id: index + 1,
        title: item.title || item.Title || 'Untitled',
        type: item.content_type || item.type || 'Research Papers',
        mission: item.mission || 'NASA Research',
        date: item.date || '2024',
        description: item.abstract || item.Description || 'No description available',
        tags: item.tags || item.keywords || ['space', 'research'],
        link: item.url || item.Link || item.link || '#',
        source: item.source || item.search_source || 'NASA Database',
        isNasaApi: item.is_nasa_api || false,
        relevanceScore: item.relevance_score || 0.5,
        details: {
          summary: {
            objective: item.abstract || 'Research objective not available',
            methodology: generateMethodology(item),
            keyFindings: generateKeyFindings(item),
            implications: generateImplications(item)
          },
          overview: generateOverviewData(item),
          knowledge: {
            relatedStudies: generateRelatedStudies(item),
            applications: generateApplications(item),
            futureResearch: generateFutureResearch(item)
          }
        }
      }));

      setApiResults(transformedResults);
      
      if (transformedResults.length === 0) {
        toast.info(`No results found for "${query}"`);
      } else {
        toast.success(`Found ${transformedResults.length} results for "${query}"`);
      }
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Search failed';
      setError(errorMessage);
      toast.error(`Search failed: ${errorMessage}`);
      setApiResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter and search logic
  const filteredResults = useMemo(() => {
    let results = hasSearched ? apiResults : (realCsvData.length > 0 ? realCsvData : searchData);

    // Filter by content type
    if (selectedTypes.length > 0) {
      results = results.filter(item => selectedTypes.includes(item.type));
    }

    // Sort results
    switch (sortBy) {
      case "date-new":
        results.sort((a, b) => String(b.date).localeCompare(String(a.date)));
        break;
      case "date-old":
        results.sort((a, b) => String(a.date).localeCompare(String(b.date)));
        break;
      case "relevance":
      default:
        // Keep original order for relevance
        break;
    }

    return results;
  }, [apiResults, realCsvData, searchData, selectedTypes, sortBy, hasSearched]);

  // Count by type - now uses real-time data from current results
  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    
    // Use real data: search results if available, otherwise real CSV data, fallback to dummy data
    const currentData = hasSearched ? apiResults : (realCsvData.length > 0 ? realCsvData : searchData);
    
    // Count all items by type
    currentData.forEach(item => {
      const itemType = item.type || 'Research Papers';
      counts[itemType] = (counts[itemType] || 0) + 1;
    });
    
    // Ensure all filter types exist with 0 count if not present
    ["Research Papers", "OSDR Data", "Task Book Grants"].forEach(type => {
      if (!(type in counts)) {
        counts[type] = 0;
      }
    });

    return counts;
  }, [apiResults, realCsvData, searchData, hasSearched]);

  const handleTypeToggle = (type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const resetFilters = () => {
    setSelectedTypes([]);
    setSearchTerm("");
    setSortBy("relevance");
    setApiResults([]);
    setHasSearched(false);
    setError(null);
  };

  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    performSearch();
  };

  const openDetailsModal = (item: typeof searchData[0]) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const closeDetailsModal = () => {
    setIsModalOpen(false);
    setSelectedItem(null);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />

      <main className="flex-1">
        <div className="bg-gradient-space py-12">
          <div className="container mx-auto px-4">
            <h1 className="text-4xl font-bold text-primary-foreground mb-6">Advanced Search</h1>
            <form onSubmit={handleSearch} className="flex gap-3">
              <div className="relative flex-1">
                <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search experiments, species, research..."
                  className="pl-10 h-12 bg-card"
                  disabled={loading}
                />
              </div>
              <Button 
                type="submit"
                size="lg" 
                className="h-12"
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                ) : (
                  <SearchIcon className="mr-2 h-5 w-5" />
                )}
                Search
              </Button>
            </form>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Filters Sidebar */}
            <aside className={`lg:w-80 ${showFilters ? 'block' : 'hidden lg:block'}`}>
              <Card className="sticky top-20">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold flex items-center">
                      <Filter className="mr-2 h-5 w-5" />
                      Filters
                    </h2>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowFilters(false)}
                      className="lg:hidden"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="space-y-6">
                    {/* Content Type */}
                    <div>
                      <h3 className="font-medium mb-3">Content Type</h3>
                      <div className="space-y-2">
                        {["Research Papers", "OSDR Data", "Task Book Grants"].map((type) => (
                          <div key={type} className="flex items-center space-x-2">
                            <Checkbox 
                              id={type} 
                              checked={selectedTypes.includes(type)}
                              onCheckedChange={() => handleTypeToggle(type)}
                              disabled={loadingStats || loadingCsvData}
                            />
                            <label htmlFor={type} className="text-sm cursor-pointer flex-1">
                              {type}
                              <span className="text-muted-foreground ml-2">
                                {(loadingStats || loadingCsvData) ? (
                                  <Loader2 className="inline h-3 w-3 animate-spin" />
                                ) : (
                                  <>({typeCounts[type] || 0})</>
                                )}
                              </span>
                            </label>
                          </div>
                        ))}
                      </div>
                      <div className="mt-3 p-2 bg-muted/30 rounded text-xs">
                        <div className="flex items-center gap-1 text-green-600">
                          <Database className="h-3 w-3" />
                          Live data: {Object.values(typeCounts).reduce((sum, count) => sum + count, 0)} total items
                        </div>
                        <div className="text-muted-foreground mt-1">
                          {hasSearched ? 'Showing search results' : 'Sources: NASA Articles CSV'}
                        </div>
                      </div>
                    </div>
                    <Button className="w-full" variant="outline" onClick={resetFilters}>
                      Reset Filters
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </aside>

            {/* Results */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-6">
                <p className="text-muted-foreground">
                  Found <span className="font-semibold text-foreground">{filteredResults.length}</span> results
                  {selectedTypes.length > 0 && (
                    <span className="ml-2">
                      (filtered by: {selectedTypes.join(", ")})
                    </span>
                  )}
                </p>
                
                {/* NASA API Controls - Hidden */}
                {false && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant={includeNasaApis ? "default" : "outline"}
                      size="sm"
                      onClick={() => setIncludeNasaApis(!includeNasaApis)}
                    >
                      NASA APIs {includeNasaApis ? "ON" : "OFF"}
                    </Button>
                    <Button
                      variant={showNasaOnly ? "default" : "outline"}
                      size="sm"
                      onClick={() => setShowNasaOnly(!showNasaOnly)}
                    >
                      NASA Only
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={testNasaApis}
                    >
                      Test APIs
                    </Button>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {/* Loading State */}
                {loading && (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <Loader2 className="h-12 w-12 text-primary mx-auto mb-4 animate-spin" />
                      <h3 className="text-lg font-semibold mb-2">Searching NASA Database...</h3>
                      <p className="text-muted-foreground">
                        Please wait while we search through the research archives
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Error State */}
                {error && !loading && (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold mb-2">Search Error</h3>
                      <p className="text-muted-foreground mb-4">{error}</p>
                      <Button onClick={() => performSearch()} variant="outline">
                        Try Again
                      </Button>
                    </CardContent>
                  </Card>
                )}

                {/* Results */}
                {!loading && !error && filteredResults.length > 0 ? (
                  filteredResults.map((result) => (
                    <Card key={result.id} className="hover-lift">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-xl font-semibold">{result.title}</h3>
                          <span className="bg-accent/10 text-accent px-3 py-1 rounded-full text-xs font-medium">
                            {result.type}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                          <span>{result.mission}</span>
                          <span>•</span>
                          <span>{result.date}</span>
                          {result.source && (
                            <>
                              <span>•</span>
                              <span className={`font-medium ${result.isNasaApi ? 'text-blue-600' : 'text-green-600'}`}>
                                {result.source}
                              </span>
                            </>
                          )}
                          {result.isNasaApi && (
                            <>
                              <span>•</span>
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                                NASA API
                              </span>
                            </>
                          )}
                        </div>
                        <p className="text-muted-foreground mb-4">
                          {result.description.length > 200 
                            ? `${result.description.substring(0, 200)}...` 
                            : result.description
                          }
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex flex-wrap gap-1">
                            {result.tags?.slice(0, 3).map((tag: string) => (
                              <span 
                                key={tag} 
                                className="bg-secondary text-secondary-foreground px-2 py-1 rounded text-xs"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                          <div className="flex gap-2">
                            {result.link && result.link !== '#' && (
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => window.open(result.link, '_blank')}
                              >
                                View Source
                              </Button>
                            )}
                            <Button 
                              variant="link" 
                              className="p-0 h-auto"
                              onClick={() => openDetailsModal(result)}
                            >
                              View Details →
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : !loading && !error && hasSearched ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <SearchIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No results found</h3>
                      <p className="text-muted-foreground mb-4">
                        No results found for "{searchTerm}". Try different keywords or check your spelling.
                      </p>
                      <Button onClick={resetFilters} variant="outline">
                        Clear Search
                      </Button>
                    </CardContent>
                  </Card>
                ) : !hasSearched && !loading ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <SearchIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-semibold mb-2">Search NASA Research Database</h3>
                      <p className="text-muted-foreground mb-4">
                        Enter keywords above to search through NASA's space biology research archives
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Try searching for terms like "microgravity", "space", "plant", "cell", or "ISS"
                      </p>
                    </CardContent>
                  </Card>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Research Details Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">
              {selectedItem?.title}
              <span className="ml-3 text-sm font-normal text-muted-foreground">
                - {selectedItem?.type}
              </span>
            </DialogTitle>
          </DialogHeader>
          
          {selectedItem && (
            <div className="mt-4">
              {/* Header Info */}
              <div className="flex items-center gap-6 mb-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  {selectedItem.mission}
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  {selectedItem.date}
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  {selectedItem.details?.overview?.authors?.length || 0} Authors
                </div>
              </div>

              {/* Tabs Section */}
              <Tabs defaultValue="summary" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="summary" className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Summary
                  </TabsTrigger>
                  <TabsTrigger value="overview" className="flex items-center gap-2">
                    <Database className="h-4 w-4" />
                    Overview
                  </TabsTrigger>
                  <TabsTrigger value="knowledge" className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Knowledge Graph
                  </TabsTrigger>
                </TabsList>

                {/* Summary Tab */}
                <TabsContent value="summary" className="mt-6 space-y-6 max-h-[60vh] overflow-y-auto">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Executive Summary</h3>
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-3">
                            <h4 className="font-medium">Research Objective</h4>
                            <span className="bg-accent/20 text-accent px-2 py-1 rounded text-xs">
                              {selectedItem.relevanceScore ? `${Math.round(selectedItem.relevanceScore * 100)}% Relevance` : 'High Relevance'}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-4">
                            {selectedItem.description || selectedItem.details?.summary?.objective || 'Research objective information not available'}
                          </p>
                          
                          <div className="grid md:grid-cols-2 gap-4 mt-4">
                            <div className="space-y-2">
                              <h5 className="font-medium text-sm">Research Type</h5>
                              <span className="bg-primary/10 text-primary px-2 py-1 rounded text-xs">
                                {selectedItem.type}
                              </span>
                            </div>
                            <div className="space-y-2">
                              <h5 className="font-medium text-sm">Data Source</h5>
                              <span className={`px-2 py-1 rounded text-xs ${
                                selectedItem.isNasaApi ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                              }`}>
                                {selectedItem.source || 'NASA Database'}
                              </span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <Database className="h-4 w-4" />
                            Methodology Overview
                          </h4>
                          <p className="text-sm text-muted-foreground mb-3">
                            {selectedItem.description || selectedItem.details?.summary?.methodology || 'Research methodology details not available for this study.'}
                          </p>
                          <div className="space-y-2">
                            <div className="flex justify-between text-xs">
                              <span>Publication Date:</span>
                              <span className="font-medium">
                                {selectedItem.date || 'Not specified'}
                              </span>
                            </div>
                            <div className="flex justify-between text-xs">
                              <span>Mission/Program:</span>
                              <span className="font-medium">{selectedItem.mission || 'NASA Research'}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                              <span>Research Type:</span>
                              <span className="font-medium">
                                {selectedItem.type || 'Research Paper'}
                              </span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <TrendingUp className="h-4 w-4" />
                            Search Relevance
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <div className="flex justify-between text-xs mb-1">
                                <span>Relevance Score</span>
                                <span className="font-medium">
                                  {selectedItem.relevanceScore ? Math.round(selectedItem.relevanceScore * 100) : 'N/A'}%
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div className="bg-accent h-2 rounded-full" style={{width: `${selectedItem.relevanceScore ? selectedItem.relevanceScore * 100 : 75}%`}}></div>
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between text-xs mb-1">
                                <span>Data Source</span>
                                <span className="font-medium">
                                  {selectedItem.isNasaApi ? 'NASA API' : 'Local Database'}
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div className={`h-2 rounded-full ${selectedItem.isNasaApi ? 'bg-blue-500' : 'bg-green-500'}`} style={{width: '100%'}}></div>
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between text-xs mb-1">
                                <span>Keywords Match</span>
                                <span className="font-medium">
                                  {selectedItem.tags ? selectedItem.tags.length : 0} tags
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div className="bg-primary h-2 rounded-full" style={{width: `${selectedItem.tags ? Math.min(selectedItem.tags.length * 25, 100) : 50}%`}}></div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <BookOpen className="h-4 w-4" />
                        Key Findings & Results
                      </h4>
                      <div className="grid md:grid-cols-2 gap-4">
                        <Card>
                          <CardContent className="p-4">
                            <h5 className="font-medium mb-2">Primary Findings</h5>
                            <div className="space-y-2">
                              {selectedItem.details?.summary?.keyFindings ? (
                                selectedItem.details.summary.keyFindings.map((finding, index) => (
                                  <div key={index} className="flex items-start gap-2">
                                    <div className="w-2 h-2 bg-accent rounded-full mt-2 flex-shrink-0" />
                                    <p className="text-sm">{finding}</p>
                                  </div>
                                ))
                              ) : (
                                <div className="flex items-start gap-2">
                                  <div className="w-2 h-2 bg-accent rounded-full mt-2 flex-shrink-0" />
                                  <p className="text-sm">{selectedItem.description || 'Key findings information not available'}</p>
                                </div>
                              )}
                              {selectedItem.tags && selectedItem.tags.length > 0 && (
                                <div className="mt-3">
                                  <h6 className="font-medium text-xs mb-1">Research Keywords:</h6>
                                  <div className="flex flex-wrap gap-1">
                                    {selectedItem.tags.map((tag, index) => (
                                      <span key={index} className="bg-secondary text-secondary-foreground px-2 py-1 rounded text-xs">
                                        {tag}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardContent className="p-4">
                            <h5 className="font-medium mb-2">Research Details</h5>
                            <div className="space-y-2">
                              <div className="flex items-start gap-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                <p className="text-sm">
                                  <span className="font-medium">Title:</span> {selectedItem.title}
                                </p>
                              </div>
                              <div className="flex items-start gap-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                <p className="text-sm">
                                  <span className="font-medium">Type:</span> {selectedItem.type}
                                </p>
                              </div>
                              <div className="flex items-start gap-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                <p className="text-sm">
                                  <span className="font-medium">Mission:</span> {selectedItem.mission || 'NASA Research'}
                                </p>
                              </div>
                              {selectedItem.link && selectedItem.link !== '#' && (
                                <div className="flex items-start gap-2">
                                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                  <p className="text-sm">
                                    <span className="font-medium">Source Available:</span> 
                                    <a href={selectedItem.link} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline ml-1">
                                      View Original
                                    </a>
                                  </p>
                                </div>
                              )}
                              {selectedItem.relevanceScore && (
                                <div className="flex items-start gap-2">
                                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                  <p className="text-sm">
                                    <span className="font-medium">Search Relevance:</span> {Math.round(selectedItem.relevanceScore * 100)}%
                                  </p>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>

                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-2 flex items-center gap-2">
                          <Users className="h-4 w-4" />
                          Research Impact & Implications
                        </h4>
                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <h5 className="font-medium text-sm mb-2">Research Summary</h5>
                            <p className="text-sm text-muted-foreground">
                              {selectedItem.description || selectedItem.details?.summary?.implications || 'Research summary not available'}
                            </p>
                          </div>
                          <div>
                            <h5 className="font-medium text-sm mb-2">Research Categories</h5>
                            <div className="flex flex-wrap gap-1">
                              {selectedItem.tags && selectedItem.tags.length > 0 ? (
                                selectedItem.tags.map((tag, index) => (
                                  <span key={index} className="bg-primary/10 text-primary px-2 py-1 rounded text-xs">
                                    {tag}
                                  </span>
                                ))
                              ) : (
                                <span className="text-sm text-muted-foreground">No categories available</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-2">Publication & Citation Metrics</h4>
                        <div className="grid md:grid-cols-3 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-accent">
                              {selectedItem.relevanceScore ? Math.round(selectedItem.relevanceScore * 100) : 'N/A'}%
                            </div>
                            <div className="text-xs text-muted-foreground">Relevance Score</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-primary">{selectedItem.type}</div>
                            <div className="text-xs text-muted-foreground">Content Type</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-tech-accent">
                              {selectedItem.isNasaApi ? 'API' : 'Local'}
                            </div>
                            <div className="text-xs text-muted-foreground">Data Source</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>

                {/* Overview Tab */}
                <TabsContent value="overview" className="mt-6 space-y-6 max-h-[60vh] overflow-y-auto">
                  <div className="space-y-6">
                    {/* Research Team & Leadership */}
                    <div className="grid md:grid-cols-2 gap-6">
                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            Research Team
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <span className="text-sm font-medium">Authors:</span>
                              <div className="mt-1">
                                {selectedItem.details?.overview?.authors && selectedItem.details.overview.authors.length > 0 ? (
                                  selectedItem.details.overview.authors.map((author, index) => (
                                    <div key={index} className="text-sm font-medium text-primary">
                                      {author}
                                    </div>
                                  ))
                                ) : (
                                  <div className="text-sm text-muted-foreground">
                                    Author information not available
                                  </div>
                                )}
                                <div className="text-xs text-muted-foreground mt-1">
                                  {selectedItem.details?.overview?.institution || 'NASA Research'}
                                </div>
                              </div>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Publication Info:</span>
                              <div className="mt-1 space-y-1">
                                <div className="text-sm text-muted-foreground">
                                  Date: {selectedItem.date || 'Not specified'}
                                </div>
                                <div className="text-sm text-muted-foreground">
                                  Mission: {selectedItem.mission || 'NASA Research'}
                                </div>
                                {selectedItem.link && selectedItem.link !== '#' && (
                                  <div className="text-sm">
                                    <a href={selectedItem.link} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                                      View Original Source →
                                    </a>
                                  </div>
                                )}
                              </div>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Research Staff:</span>
                              <div className="text-sm text-muted-foreground mt-1">
                                {selectedItem.details?.overview?.researchStaff || 'Research staff information not available'}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            Institutional Details
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <span className="text-sm font-medium">Lead Institution:</span>
                              <p className="text-sm text-muted-foreground mt-1">
                                {selectedItem.details?.overview?.institution}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Department:</span>
                              <p className="text-sm text-muted-foreground mt-1">
                                {selectedItem.details?.overview?.department || 'Department information not available'}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Research Location:</span>
                              <p className="text-sm text-muted-foreground mt-1">
                                {selectedItem.details?.overview?.location}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Lab Facilities:</span>
                              <p className="text-sm text-muted-foreground mt-1">
                                {selectedItem.details?.overview?.labFacilities || 'Lab facilities information not available'}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Funding & Timeline */}
                    <div className="grid md:grid-cols-3 gap-4">
                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-3">Funding Information</h4>
                          <div className="space-y-2">
                            <div>
                              <span className="text-sm font-medium">Primary Source:</span>
                              <p className="text-sm text-muted-foreground">
                                {selectedItem.details?.overview?.fundingSource}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Grant Amount:</span>
                              <p className="text-sm text-muted-foreground">
                                {selectedItem.type === 'Task Book Grants' ? 'NASA-funded project' : 'Funding information not specified'}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Grant ID:</span>
                              <p className="text-sm text-muted-foreground font-mono">
                                {selectedItem.type === 'Task Book Grants' ? 'NASA Task Book Project' : 'Research publication'}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-3">Project Timeline</h4>
                          <div className="space-y-2">
                            <div>
                              <span className="text-sm font-medium">Duration:</span>
                              <p className="text-sm text-muted-foreground">
                                {selectedItem.details?.overview?.duration}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Start Date:</span>
                              <p className="text-sm text-muted-foreground">
                                {selectedItem.date ? `${selectedItem.date}` : 'Date not specified'}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Status:</span>
                              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                                {selectedItem.date === "2024" ? "Completed" : "Ongoing"}
                              </span>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Progress:</span>
                              <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                                <div className="bg-accent h-2 rounded-full" style={{width: selectedItem.date === "2024" ? '100%' : '75%'}}></div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <h4 className="font-medium mb-3">Study Subjects</h4>
                          <div className="space-y-2">
                            <div>
                              <span className="text-sm font-medium">Primary Subjects:</span>
                              <p className="text-sm text-muted-foreground">
                                {selectedItem.details?.overview?.subjects}
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Sample Size:</span>
                              <p className="text-sm text-muted-foreground">
                                Research sample size not specified
                              </p>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Control Groups:</span>
                              <p className="text-sm text-muted-foreground">
                                Control group information not available
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Technical Specifications */}
                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-3">Technical Specifications & Equipment</h4>
                        <div className="grid md:grid-cols-2 gap-6">
                          <div>
                            <h5 className="font-medium text-sm mb-2">Primary Equipment</h5>
                            <div className="space-y-1">
                              {selectedItem.id === 1 && (
                                <>
                                  <div className="text-sm">• Advanced Plant Habitat (APH)</div>
                                  <div className="text-sm">• LED Growth Chamber System</div>
                                  <div className="text-sm">• Environmental Monitoring Sensors</div>
                                  <div className="text-sm">• Confocal Microscopy System</div>
                                </>
                              )}
                              {selectedItem.id === 2 && (
                                <>
                                  <div className="text-sm">• RNA Sequencing Platform</div>
                                  <div className="text-sm">• Cell Culture Maintenance System</div>
                                  <div className="text-sm">• Automated Liquid Handling</div>
                                  <div className="text-sm">• High-Performance Computing Cluster</div>
                                </>
                              )}
                              {selectedItem.id > 2 && (
                                <>
                                  <div className="text-sm">• Specialized Research Equipment</div>
                                  <div className="text-sm">• Data Collection Systems</div>
                                  <div className="text-sm">• Analysis Software Suite</div>
                                </>
                              )}
                            </div>
                          </div>
                          <div>
                            <h5 className="font-medium text-sm mb-2">Data Collection Methods</h5>
                            <div className="space-y-1">
                              {selectedItem.id === 1 && (
                                <>
                                  <div className="text-sm">• Time-lapse imaging (24h cycles)</div>
                                  <div className="text-sm">• Biochemical assays (weekly)</div>
                                  <div className="text-sm">• Gene expression analysis</div>
                                  <div className="text-sm">• Morphometric measurements</div>
                                </>
                              )}
                              {selectedItem.id === 2 && (
                                <>
                                  <div className="text-sm">• RNA-seq at multiple timepoints</div>
                                  <div className="text-sm">• qPCR validation studies</div>
                                  <div className="text-sm">• Metabolomic profiling</div>
                                  <div className="text-sm">• Bioinformatics analysis</div>
                                </>
                              )}
                              {selectedItem.id > 2 && (
                                <>
                                  <div className="text-sm">• Regular data collection protocols</div>
                                  <div className="text-sm">• Quality control measures</div>
                                  <div className="text-sm">• Statistical analysis methods</div>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>

                {/* Knowledge Graph Tab */}
                <TabsContent value="knowledge" className="mt-6 space-y-6 max-h-[60vh] overflow-y-auto">
                  <div className="space-y-6">
                    {/* Related Concepts Section */}
                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-3 text-accent">Related Concepts</h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedItem.tags.map((tag, index) => {
                            // Define color variations for different tag types
                            const getTagColor = (tagName: string) => {
                              const colorMap: { [key: string]: string } = {
                                'Human Research': 'bg-red-500 text-white',
                                'Space Biology': 'bg-primary text-primary-foreground',
                                'Microgravity': 'bg-orange-500 text-white',
                                'Space Radiation': 'bg-red-600 text-white',
                                'Bone Research': 'bg-amber-500 text-white',
                                'Muscle Research': 'bg-yellow-500 text-black',
                                'Plant Biology': 'bg-green-500 text-white',
                                'Cell Biology': 'bg-emerald-500 text-white',
                                'Technology Development': 'bg-blue-500 text-white',
                                'ISS Research': 'bg-indigo-500 text-white',
                                'Task Book Grants': 'bg-purple-500 text-white'
                              };
                              return colorMap[tagName] || 'bg-secondary text-secondary-foreground';
                            };

                            return (
                              <span 
                                key={index}
                                className={`${getTagColor(tag)} px-4 py-2 rounded-lg text-sm font-medium`}
                              >
                                {tag.charAt(0).toUpperCase() + tag.slice(1)}
                              </span>
                            );
                          })}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Graph Visualization */}
                    <Card>
                      <CardContent className="p-6">
                        <h4 className="font-medium mb-4 text-accent">Graph Visualization</h4>
                        <div className="relative bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950 rounded-xl p-8 min-h-[400px] overflow-hidden border border-slate-700/50">
                          {/* Background pattern */}
                          <div className="absolute inset-0 opacity-10">
                            <div className="absolute inset-0" style={{
                              backgroundImage: 'radial-gradient(circle at 25% 25%, #3b82f6 0%, transparent 50%), radial-gradient(circle at 75% 75%, #8b5cf6 0%, transparent 50%)',
                              backgroundSize: '100px 100px'
                            }}></div>
                          </div>
                          
                          {(() => {
                            const graphData = generateKnowledgeGraph(selectedItem);
                            
                            return (
                              <>
                                {/* Central Research Hub */}
                                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20">
                                  <div className="relative">
                                    {/* Pulsing outer ring */}
                                    <div className="absolute inset-0 bg-cyan-400 rounded-full animate-ping opacity-20 scale-125"></div>
                                    {/* Main central node */}
                                    <div className="relative bg-gradient-to-br from-cyan-400 to-blue-500 text-white px-8 py-4 rounded-xl font-bold text-center shadow-2xl border-2 border-cyan-300/50 backdrop-blur-sm">
                                      <div className="text-lg font-bold">{graphData.centralConcept}</div>
                                      <div className="text-xs opacity-80 mt-1">Research Focus</div>
                                      {/* Central glow effect */}
                                      <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/20 to-blue-500/20 rounded-xl blur-xl -z-10"></div>
                                    </div>
                                  </div>
                                </div>

                                {/* Research Network Nodes */}
                                {graphData.connectedNodes.map((node, index) => {
                                  const positions = [
                                    { top: '15%', left: '15%', transform: 'translate(-50%, -50%)' },
                                    { top: '15%', right: '15%', transform: 'translate(50%, -50%)' },
                                    { bottom: '15%', right: '15%', transform: 'translate(50%, 50%)' },
                                    { bottom: '15%', left: '15%', transform: 'translate(-50%, 50%)' }
                                  ];
                                  
                                  // Generate color gradient based on node category
                                  const getNodeGradient = (node: any): string => {
                                    const categoryGradients: { [key: string]: string } = {
                                      'Domain': 'from-red-500 to-pink-600',
                                      'Life Science': 'from-green-500 to-emerald-600',
                                      'Physiology': 'from-orange-500 to-amber-600',
                                      'Environment': 'from-blue-500 to-cyan-600',
                                      'Innovation': 'from-purple-500 to-violet-600',
                                      'Platform': 'from-cyan-500 to-teal-600',
                                      'Method': 'from-teal-500 to-green-600',
                                      'Process': 'from-lime-500 to-green-600',
                                      'Data Repository': 'from-slate-500 to-gray-600'
                                    };
                                    return categoryGradients[node.category] || 'from-indigo-500 to-purple-600';
                                  };
                                  
                                  return (
                                    <div 
                                      key={index} 
                                      className="absolute z-10" 
                                      style={positions[index]}
                                    >
                                      <div className="relative group cursor-pointer">
                                        {/* Node hover effect */}
                                        <div className="absolute inset-0 bg-white/20 rounded-lg scale-0 group-hover:scale-110 transition-transform duration-300 blur"></div>
                                        {/* Main node */}
                                        <div className={`relative bg-gradient-to-br ${getNodeGradient(node)} text-white px-4 py-3 rounded-lg font-semibold shadow-xl border border-white/20 backdrop-blur-sm transition-all duration-300 group-hover:scale-105 group-hover:shadow-2xl`}>
                                          <div className="text-sm font-semibold">{node.name}</div>
                                          <div className="text-xs opacity-75 mt-1">
                                            {node.category || 'Research Area'}
                                          </div>
                                          {/* Node glow */}
                                          <div className={`absolute inset-0 bg-gradient-to-br ${getNodeGradient(node)} opacity-30 rounded-lg blur-lg -z-10`}></div>
                                        </div>
                                      </div>
                                    </div>
                                  );
                                })}

                                {/* Enhanced Connection Lines with Data Flow Animation */}
                                <svg className="absolute inset-0 w-full h-full pointer-events-none z-5">
                                  <defs>
                                    {/* Gradient for connection lines */}
                                    <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                      <stop offset="0%" style={{stopColor: '#06b6d4', stopOpacity: 0.8}} />
                                      <stop offset="50%" style={{stopColor: '#3b82f6', stopOpacity: 0.6}} />
                                      <stop offset="100%" style={{stopColor: '#8b5cf6', stopOpacity: 0.8}} />
                                    </linearGradient>
                                    
                                    {/* Animated dots for data flow */}
                                    <circle id="flowDot" r="3" fill="#06b6d4" opacity="0.8">
                                      <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" />
                                    </circle>
                                  </defs>
                                  
                                  {graphData.connectedNodes.map((node, index) => {
                                    const lineCoords = [
                                      { x1: "50%", y1: "50%", x2: "15%", y2: "15%" },
                                      { x1: "50%", y1: "50%", x2: "85%", y2: "15%" },
                                      { x1: "50%", y1: "50%", x2: "85%", y2: "85%" },
                                      { x1: "50%", y1: "50%", x2: "15%", y2: "85%" }
                                    ];
                                    
                                    return (
                                      <g key={index}>
                                        {/* Main connection line */}
                                        <line
                                          x1={lineCoords[index]?.x1 || "50%"}
                                          y1={lineCoords[index]?.y1 || "50%"}
                                          x2={lineCoords[index]?.x2 || "50%"}
                                          y2={lineCoords[index]?.y2 || "50%"}
                                          stroke="url(#connectionGradient)"
                                          strokeWidth="3"
                                          strokeDasharray="5,5"
                                          opacity="0.7"
                                        >
                                          <animate 
                                            attributeName="stroke-dashoffset" 
                                            values="0;-10" 
                                            dur="1s" 
                                            repeatCount="indefinite"
                                          />
                                        </line>
                                        
                                        {/* Data flow dots */}
                                        <circle r="2" fill="#06b6d4" opacity="0.9">
                                          <animateMotion 
                                            dur="3s" 
                                            repeatCount="indefinite"
                                            path={`M ${lineCoords[index]?.x1} ${lineCoords[index]?.y1} L ${lineCoords[index]?.x2} ${lineCoords[index]?.y2}`}
                                          />
                                          <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" />
                                        </circle>
                                      </g>
                                    );
                                  })}
                                </svg>

                                {/* Research Stats Overlay */}
                                <div className="absolute top-4 right-4 z-30">
                                  <div className="bg-black/30 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/10">
                                    <div className="text-white text-xs space-y-1">
                                      <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                                        <span>Core Focus: {graphData.centralConcept}</span>
                                      </div>
                                      <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                        <span>Connected Areas: {graphData.connectedNodes.length}</span>
                                      </div>
                                      <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                                        <span>Research Type: {selectedItem.type}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* Legend */}
                                <div className="absolute bottom-4 left-4 z-30">
                                  <div className="bg-black/30 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/10">
                                    <div className="text-white text-xs">
                                      <div className="font-semibold mb-2">Research Network</div>
                                      <div className="space-y-1">
                                        <div className="flex items-center gap-2">
                                          <div className="w-3 h-3 bg-gradient-to-r from-cyan-400 to-blue-500 rounded"></div>
                                          <span>Primary Focus</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                          <div className="w-3 h-3 bg-gradient-to-r from-red-500 to-pink-600 rounded"></div>
                                          <span>Related Domains</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                          <div className="w-8 h-0.5 bg-gradient-to-r from-cyan-400 to-purple-500 rounded opacity-70"></div>
                                          <span>Data Flow</span>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </>
                            );
                          })()}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-3">Related Studies</h4>
                        <div className="space-y-2">
                          {selectedItem.details?.knowledge?.relatedStudies?.map((study, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <BookOpen className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">{study}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-3">Practical Applications</h4>
                        <div className="grid md:grid-cols-2 gap-2">
                          {selectedItem.details?.knowledge?.applications?.map((app, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <TrendingUp className="h-4 w-4 text-accent" />
                              <span className="text-sm">{app}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="p-4">
                        <h4 className="font-medium mb-3">Future Research Directions</h4>
                        <div className="space-y-2">
                          {selectedItem.details?.knowledge?.futureResearch?.map((research, index) => (
                            <div key={index} className="flex items-start gap-2">
                              <div className="w-2 h-2 bg-tech-accent rounded-full mt-2 flex-shrink-0" />
                              <span className="text-sm">{research}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
};

export default Search;
