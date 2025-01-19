export function initArchitectureDiagram() {
  const diagram = document.getElementById('architecture-diagram');
  
  // Create SVG architecture diagram
  diagram.innerHTML = `
    <svg width="100%" height="400" viewBox="0 0 800 400">
      <!-- ESP32 Node -->
      <g transform="translate(100,100)">
        <rect width="120" height="60" rx="5" fill="#4A90E2"/>
        <text x="60" y="35" fill="white" text-anchor="middle">ESP32</text>
      </g>
      
      <!-- Server -->
      <g transform="translate(350,100)">
        <rect width="120" height="60" rx="5" fill="#27AE60"/>
        <text x="60" y="35" fill="white" text-anchor="middle">Server</text>
      </g>
      
      <!-- Database -->
      <g transform="translate(600,100)">
        <rect width="120" height="60" rx="5" fill="#E67E22"/>
        <text x="60" y="35" fill="white" text-anchor="middle">Database</text>
      </g>
      
      <!-- Connection Lines -->
      <path d="M220,130 L350,130" stroke="#2C3E50" stroke-width="2"/>
      <path d="M470,130 L600,130" stroke="#2C3E50" stroke-width="2"/>
      
      <!-- Web Interface -->
      <g transform="translate(350,250)">
        <rect width="120" height="60" rx="5" fill="#8E44AD"/>
        <text x="60" y="35" fill="white" text-anchor="middle">Web Interface</text>
      </g>
      
      <!-- Connection to Web Interface -->
      <path d="M410,160 L410,250" stroke="#2C3E50" stroke-width="2"/>
    </svg>
  `;
}