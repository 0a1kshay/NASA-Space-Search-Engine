// Test the generateOverviewData logic
const generateOverviewData = (item) => {
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

// Test cases
const testCases = [
  {
    title: "Microgravity effects on bone",
    tags: ["Space Biology", "Microgravity", "Bone Research"],
    type: "Research Papers",
    date: "2023",
    authors: ["Dr. Jane Smith", "Dr. John Doe"]
  },
  {
    title: "Tempus ALS Technology",
    tags: ["Human Research", "Technology Development", "ISS Research"],
    type: "Task Book Grants", 
    date: "2025",
    authors: ["Dr. Jerry Myers"]
  },
  {
    title: "Plant growth in space",
    tags: ["Plant Biology", "Space Biology"],
    type: "OSDR Data",
    date: "2021",
    authors: ["NASA Research Team"]
  }
];

console.log("Testing Overview Data Generation:");
console.log("=================================");

testCases.forEach((testCase, index) => {
  console.log(`\nTest Case ${index + 1}: ${testCase.title}`);
  console.log(`Type: ${testCase.type}`);
  console.log(`Tags: ${testCase.tags.join(', ')}`);
  console.log(`Date: ${testCase.date}`);
  console.log(`Authors: ${testCase.authors.join(', ')}`);
  
  const overview = generateOverviewData(testCase);
  console.log("\nGenerated Overview Data:");
  console.log(`  Department: ${overview.department}`);
  console.log(`  Location: ${overview.location}`);
  console.log(`  Lab Facilities: ${overview.labFacilities}`);
  console.log(`  Research Staff: ${overview.researchStaff}`);
  console.log(`  Subjects: ${overview.subjects}`);
  console.log(`  Duration: ${overview.duration}`);
  console.log(`  Funding: ${overview.fundingSource}`);
});