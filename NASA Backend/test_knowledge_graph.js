// Test the Knowledge Graph generation logic
const generateKnowledgeGraph = (item) => {
  const tags = item.tags || [];
  const title = item.title || '';
  const type = item.type || 'Research';
  
  // Determine central concept based on research focus
  let centralConcept = 'Space Research';
  if (tags.includes('Human Research')) {
    centralConcept = 'Human Research';
  } else if (tags.includes('Plant Biology')) {
    centralConcept = 'Plant Biology';
  } else if (tags.includes('Bone Research')) {
    centralConcept = 'Bone Research';
  } else if (tags.includes('Space Radiation')) {
    centralConcept = 'Space Radiation';
  } else if (tags.includes('Microgravity')) {
    centralConcept = 'Microgravity';
  } else if (tags.includes('Cell Biology')) {
    centralConcept = 'Cell Biology';
  } else if (tags.includes('Technology Development')) {
    centralConcept = 'Technology Development';
  }
  
  // Generate connected nodes from tags and research context
  const connectedNodes = [];
  
  // Add primary tags as connected nodes
  tags.forEach(tag => {
    if (tag !== centralConcept && tag !== 'Space Biology') {
      connectedNodes.push({
        name: tag,
        color: getNodeColor(tag),
        position: getNodePosition(connectedNodes.length)
      });
    }
  });
  
  // Add contextual nodes based on research type
  if (type === 'Task Book Grants') {
    connectedNodes.push({
      name: 'ISS Research',
      color: 'bg-blue-400',
      position: getNodePosition(connectedNodes.length)
    });
  }
  
  // Add research methodology nodes based on content
  if (title.toLowerCase().includes('gene') || title.toLowerCase().includes('expression')) {
    connectedNodes.push({
      name: 'Gene Expression',
      color: 'bg-cyan-500',
      position: getNodePosition(connectedNodes.length)
    });
  }
  
  if (title.toLowerCase().includes('protein') || title.toLowerCase().includes('molecular')) {
    connectedNodes.push({
      name: 'Molecular Biology',
      color: 'bg-purple-400',
      position: getNodePosition(connectedNodes.length)
    });
  }
  
  // Limit to 4 connected nodes for clean visualization
  const limitedNodes = connectedNodes.slice(0, 4);
  
  return {
    centralConcept,
    connectedNodes: limitedNodes
  };
};

// Helper function to get node color based on research area
const getNodeColor = (tag) => {
  const colorMap = {
    'Human Research': 'bg-red-400',
    'Microgravity': 'bg-red-400',
    'Space Radiation': 'bg-orange-400',
    'Bone Research': 'bg-amber-400',
    'Muscle Research': 'bg-yellow-400',
    'Plant Biology': 'bg-green-400',
    'Cell Biology': 'bg-emerald-400',
    'Technology Development': 'bg-blue-400',
    'ISS Research': 'bg-indigo-400',
    'OSDR Data': 'bg-purple-400',
    'Task Book Grants': 'bg-pink-400'
  };
  return colorMap[tag] || 'bg-slate-400';
};

// Helper function to get node position
const getNodePosition = (index) => {
  const positions = [
    { top: '16px', left: '16px' },      // Top left
    { top: '16px', right: '16px' },     // Top right  
    { bottom: '16px', right: '24px' },  // Bottom right
    { bottom: '16px', left: '16px' }    // Bottom left
  ];
  return positions[index] || positions[0];
};

// Test cases
const testCases = [
  {
    title: "Tempus ALS ISS Technology Demonstration",
    tags: ["Human Research", "Technology Development", "ISS Research"],
    type: "Task Book Grants"
  },
  {
    title: "Microgravity effects on bone density",
    tags: ["Space Biology", "Microgravity", "Bone Research"],
    type: "Research Papers"
  },
  {
    title: "Gene expression in space-grown plants",
    tags: ["Plant Biology", "Cell Biology", "Space Biology"],
    type: "OSDR Data"
  },
  {
    title: "Space radiation impact on molecular structures",
    tags: ["Space Radiation", "Cell Biology", "Molecular Biology"],
    type: "Research Papers"
  }
];

console.log("Testing Knowledge Graph Generation:");
console.log("==================================");

testCases.forEach((testCase, index) => {
  console.log(`\nTest Case ${index + 1}: ${testCase.title}`);
  console.log(`Type: ${testCase.type}`);
  console.log(`Tags: ${testCase.tags.join(', ')}`);
  
  const graph = generateKnowledgeGraph(testCase);
  console.log(`\nGenerated Knowledge Graph:`);
  console.log(`Central Concept: ${graph.centralConcept}`);
  console.log(`Connected Nodes (${graph.connectedNodes.length}):`);
  graph.connectedNodes.forEach((node, i) => {
    console.log(`  ${i + 1}. ${node.name} (${node.color})`);
  });
});