// Test the generateKeyFindings logic
const generateKeyFindings = (item) => {
  const findings = [];
  
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

// Test cases
const testCases = [
  {
    title: "Microgravity effects on bone",
    tags: ["Space Biology", "Microgravity", "Bone Research"],
    type: "Research Papers",
    date: "2023"
  },
  {
    title: "Tempus ALS Technology",
    tags: ["Human Research", "Technology Development", "ISS Research"],
    type: "Task Book Grants", 
    date: "2025"
  },
  {
    title: "Space radiation study",
    tags: ["Space Radiation", "Cell Biology"],
    type: "OSDR Data",
    date: "2021"
  },
  {
    title: "General space research",
    tags: [],
    type: "Research Papers",
    date: "2020"
  }
];

console.log("Testing Key Findings Generation:");
console.log("================================");

testCases.forEach((testCase, index) => {
  console.log(`\nTest Case ${index + 1}: ${testCase.title}`);
  console.log(`Tags: ${testCase.tags.join(', ')}`);
  console.log(`Type: ${testCase.type}`);
  console.log(`Date: ${testCase.date}`);
  
  const findings = generateKeyFindings(testCase);
  console.log("Generated Key Findings:");
  findings.forEach((finding, i) => {
    console.log(`  ${i + 1}. ${finding}`);
  });
});